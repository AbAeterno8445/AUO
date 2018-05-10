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

        self.clock = pygame.time.Clock()

        self.spr_list_maptiles = pygame.sprite.LayeredDirty()
        self.spr_list_palette = pygame.sprite.LayeredDirty()
        for ptile in self.map.tile_palette:
            self.spr_list_palette.add(ptile)

        self.selected_tile = 0

    def init_display(self, disp_w, disp_h):
        self.display = pygame.display.set_mode((disp_w, disp_h))
        self.tiles_surface = pygame.Surface((disp_w, disp_h))
        self.palette_surface = pygame.Surface((self.map.palette_rowlen * 32, disp_h))

    def load_map(self, mapname):
        map_path = "../data/maps/" + mapname
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

    def main_loop(self):
        # Selection rectangle
        rect_sel = pygame.Rect(0,0,32,32)

        # Background for map surface
        background = pygame.Surface(self.display.get_size())
        background = background.convert()
        background.fill((0, 0, 0))
        self.spr_list_maptiles.clear(self.display, background)

        self.load_map("town")

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
            self.keys_held = pygame.key.get_pressed()
            # Mouse buttons held
            self.mouse_held = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

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
            if self.mouse_held[0]:
                # Tile selecting/placing
                if mouse_pos[0] < self.map.palette_rowlen * 32:  # Mouse x < palette x, selecting tile
                    try: self.selected_tile = self.map.tile_palette[mouse_pos32x + mouse_pos32y * self.map.palette_rowlen].tile_id
                    except: pass
                else:  # Mouse x > palette x, placing tile in map
                    try:
                        changed_tile = self.map.map_data[mouse_tileposy][mouse_tileposx]
                        self.spr_list_maptiles.remove(changed_tile)
                        changed_tile.set_tile(self.selected_tile)
                        self.spr_list_maptiles.add(changed_tile)
                    except: pass

            self.spr_list_maptiles.update()

            self.display.fill((0, 0, 0))

            self.spr_list_palette.draw(self.palette_surface) # Draw tiles to palette surface
            self.spr_list_maptiles.draw(self.tiles_surface) # Draw maptiles to map surface

            # Draw map surface
            self.display.blit(self.tiles_surface, self.camera_pos)
            # Draw palette surface
            self.display.blit(self.palette_surface, (0,0))
            pygame.draw.rect(self.display, (255,255,255), self.palette_surface.get_rect(), 1)

            if self.map.loaded:
                # Selection rectangle
                # Mouse x > palette x, editing map
                if mouse_pos[0] >= self.map.palette_rowlen * 32:
                    pygame.draw.rect(self.display, (200, 127, 30), (self.camera_pos.x + mouse_tileposx * 32, self.camera_pos.y + mouse_tileposy * 32, 32, 32), 1)
                else: # Selecting tile
                    pygame.draw.rect(self.display, (220, 220, 50), (floor(mouse_pos[0] / 32) * 32, floor(mouse_pos[1] / 32) * 32, 32, 32), 1)

                # Selected tile rectangle
                pygame.draw.rect(self.display, (220, 30, 30), (self.selected_tile % self.map.palette_rowlen * 32, floor(self.selected_tile / self.map.palette_rowlen) * 32, 32, 32), 1)

            pygame.display.update(self.tiles_surface.get_rect())

            self.clock.tick(60)