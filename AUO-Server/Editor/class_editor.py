import os.path
from class_map import GameMap
import pygame
from pygame.math import Vector2
from math import floor

class Editor(object):
    def __init__(self):
        self.map = GameMap()
        self.keys_held = []
        self.mouse_held = []

        self.camera_pos = Vector2(320, 0)
        self.display = None
        self.tiles_surface = None
        self.palette_surface = None
        self.settings_surface = None

        self.clock = pygame.time.Clock()

        self.spr_list_maptiles = pygame.sprite.LayeredDirty()
        self.spr_list_palette = pygame.sprite.LayeredDirty()
        for ptile in self.map.tile_palette:
            self.spr_list_palette.add(ptile)

        self.selected_tile = [0, 0]

        self.font = pygame.font.Font("monobit.ttf", 32)
        self.font_color = pygame.Color(255, 255, 255)
        self.text_info = ""
        self.text_input = ""
        self.input_action = ""
        self.inputting = False

    def init_display(self, disp_w, disp_h):
        disp_w = max(800, min(1920, disp_w))
        disp_h = max(600, min(1080, disp_h))
        self.display = pygame.display.set_mode((disp_w, disp_h))
        self.tiles_surface = pygame.Surface((disp_w, disp_h))
        self.settings_surface = pygame.Surface((disp_w, 128))
        self.palette_surface = pygame.Surface((self.map.palette_rowlen * 32, disp_h - self.settings_surface.get_height()))

    def load_map(self, mapname):
        map_path = "../data/maps/" + mapname
        print("Loading map " + mapname + "...")
        if os.path.isfile(map_path):
            # Unload current map if loaded
            if self.map.loaded:
                for row in self.map.map_data:
                    for tile in row:
                        self.spr_list_maptiles.remove(tile)

            map_tiles = self.map.load(map_path)
            for row in map_tiles:
                for tile in row:
                    self.spr_list_maptiles.add(tile)
                    if tile.foreg_tile:
                        self.spr_list_maptiles.add(tile.foreg_tile)

            self.camera_pos.x = self.palette_surface.get_width() + self.map.width * 16
            self.camera_pos.y += self.map.height * 16
            return True
        else:
            print("Could not find map!")
            return False

    def save_map(self, mapname):
        map_path = "../data/maps/" + mapname
        if self.map.save(map_path):
            print("Map " + mapname + " saved.")
        else:
            print("No map loaded!")

    def map_changetile(self, ty, tx, newtile):
        try:
            changed_tile = self.map.map_data[tx][ty]
            self.spr_list_maptiles.remove(changed_tile)
            changed_tile.set_tile(newtile)
            self.spr_list_maptiles.add(changed_tile)
            return True
        except: return False

    def main_loop(self):
        # Background for map surface
        background = pygame.Surface(self.display.get_size())
        background = background.convert()
        background.fill((0, 0, 0))
        self.spr_list_maptiles.clear(self.display, background)

        # Tile selector rectangles
        rect_sel = [
            [pygame.Color(220, 30, 30), pygame.Rect(0, 0, 32, 32)],
            [pygame.Color(30, 220, 220), pygame.Rect(1, 1, 30, 30)]
        ]

        done = False
        while not done:
            # Mouse position
            mouse_pos = pygame.mouse.get_pos()
            # Mouse position aligned to 32x32 grid
            mouse_pos32x, mouse_pos32y = floor(mouse_pos[0] / 32), floor(mouse_pos[1] / 32)
            # Mouse tile position within map surface
            mouse_tileposx, mouse_tileposy = 0, 0
            if self.map.loaded:
                mouse_tileposx = min(max(floor((mouse_pos[0] - self.camera_pos.x) / 32), 0), self.map.width - 1)
                mouse_tileposy = min(max(floor((mouse_pos[1] - self.camera_pos.y) / 32), 0), self.map.height - 1)

            # Keyboard keys held
            if not self.inputting:
                self.keys_held = pygame.key.get_pressed()
            # Mouse buttons held
            self.mouse_held = pygame.mouse.get_pressed()

            # Pygame event polling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    # Inputting
                    if self.inputting:
                        if event.key == pygame.K_RETURN:
                            if self.input_action == "save": # Save map
                                self.save_map(self.text_input)
                            elif self.input_action == "load": # Load map
                                self.load_map(self.text_input)
                            self.text_input = ""
                            self.inputting = False

                        elif event.key == pygame.K_BACKSPACE:
                            self.text_input = self.text_input[:-1]
                        else:
                            self.text_input += event.unicode

                    else: # Normal keypress
                        if self.keys_held[pygame.K_LSHIFT]: # Shift + key
                            if event.key == pygame.K_s: # SHIFT + S, save map
                                self.text_info = "Save map as > "
                                self.text_input = self.map.name
                                self.input_action = "save"
                                self.inputting = True
                            elif event.key == pygame.K_l: # SHIFT + L, load map
                                self.text_info = "Load map > "
                                self.input_action = "load"
                                self.inputting = True

            # Camera movement
            mv_axis = [0, 0]
            cam_spd = 5
            if self.keys_held[pygame.K_LSHIFT]: # fast movement (lshift)
                cam_spd = 20
            if self.keys_held[pygame.K_d]:  # right
                mv_axis[0] = cam_spd
            elif self.keys_held[pygame.K_a]:  # left
                mv_axis[0] = -cam_spd
            if self.keys_held[pygame.K_w]:  # up
                mv_axis[1] = -cam_spd
            elif self.keys_held[pygame.K_s]:  # down
                mv_axis[1] = cam_spd
            self.camera_pos -= mv_axis

            # Left mouse button held
            for i in range(2):
                if self.mouse_held[i*2]: # get mouse held 0(left) and 2(right)
                    upd_rel_sect = False
                    if mouse_pos[0] < self.palette_surface.get_width():  # Mouse x < palette x, selecting tile
                        self.selected_tile[i] = self.map.tile_palette[mouse_pos32x + mouse_pos32y * self.map.palette_rowlen].tile_id
                        upd_rel_sect = True
                    else:  # Mouse x > palette x, placing tile in map
                        # CTRL key - Tile picker
                        if self.keys_held[pygame.K_LCTRL]:
                            self.selected_tile[i] = self.map.map_data[mouse_tileposy][mouse_tileposx].tile_id
                            upd_rel_sect = True
                        else: # Place tile
                            self.map_changetile(mouse_tileposx, mouse_tileposy, self.selected_tile[i])

                    if upd_rel_sect:
                        rect_sel[i][1].topleft = (self.selected_tile[i] % self.map.palette_rowlen * 32 + i, floor(self.selected_tile[i] / self.map.palette_rowlen) * 32 + i)

            self.spr_list_maptiles.update()

            self.display.fill((0, 0, 0))

            self.spr_list_palette.draw(self.palette_surface) # Draw tiles to palette surface
            self.spr_list_maptiles.draw(self.tiles_surface) # Draw maptiles to map surface

            # Draw map surface
            self.display.blit(self.tiles_surface, self.camera_pos)

            # Draw palette surface
            self.display.blit(self.palette_surface, (0,0))
            pygame.draw.rect(self.display, (255,255,255), self.palette_surface.get_rect(), 1)

            # Draw settings surface
            self.settings_surface.fill((0,0,0))
            # Save/load info text
            if self.inputting:
                tmp_text = self.font.render(self.text_info + self.text_input, False, self.font_color)
                self.settings_surface.blit(tmp_text, (4, self.settings_surface.get_height() - tmp_text.get_height() - 4))
            self.display.blit(self.settings_surface, (0, self.palette_surface.get_height()))

            if self.map.loaded:
                # Selection rectangle
                # Mouse x > palette x, editing map
                if mouse_pos[0] >= self.palette_surface.get_width():
                    pygame.draw.rect(self.display, (200, 127, 30), (self.camera_pos.x + mouse_tileposx * 32, self.camera_pos.y + mouse_tileposy * 32, 32, 32), 1)
                else: # Selecting tile
                    pygame.draw.rect(self.display, (220, 220, 50), (floor(mouse_pos[0] / 32) * 32, floor(mouse_pos[1] / 32) * 32, 32, 32), 1)

            # Selected tile rectangle (primary/secondary)
            for r in rect_sel:
                pygame.draw.rect(self.display, r[0], r[1], 1)

            pygame.display.update((self.tiles_surface.get_rect(), self.settings_surface.get_rect()))

            self.clock.tick(60)