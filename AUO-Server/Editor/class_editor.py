import os.path, math
from class_map import GameMap
import pygame
from pygame.math import Vector2

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

        # Palette scrolling
        self.palette_pad_av = 0
        self.palette_pad = 0

        self.clock = pygame.time.Clock()

        self.spr_list_palette = pygame.sprite.LayeredDirty()
        for ptile in self.map.tile_palette:
            self.spr_list_palette.add(ptile)

        self.selected_tile = [0, 0]
        self.foreg_mode = False
        self.newtileflags = []

        self.font = pygame.font.Font("monobit.ttf", 32)
        self.font_color = pygame.Color(255, 255, 255)
        self.text_info = ""
        self.text_input = ""
        self.input_action = ""
        self.input_data = {} # Extra input data, e.g. new map x/y size, resize map x/y size
        self.inputting = False

    def init_display(self, disp_w, disp_h):
        disp_w = max(800, min(1920, disp_w))
        disp_h = max(600, min(1080, disp_h))
        self.display = pygame.display.set_mode((disp_w, disp_h))
        self.tiles_surface = pygame.Surface((disp_w, disp_h))
        self.settings_surface = pygame.Surface((disp_w, 128))

        palette_rows = math.ceil(len(self.map.tile_palette) / self.map.palette_rowlen)
        self.palette_surface = pygame.Surface((self.map.palette_rowlen * 32, palette_rows * 32))

        self.palette_pad_av = palette_rows - math.ceil((disp_h - self.settings_surface.get_height()) / 32) + 1

    # Scales tiles surface to current map size
    def updatesize_tilesurface(self):
        #pass # does not yet work correctly
        self.tiles_surface = pygame.transform.scale(self.tiles_surface, (self.map.width * 32, self.map.height * 32))

    def map_load(self, mapname):
        map_path = "../data/maps/" + mapname
        print("Loading map " + mapname + "...")
        if os.path.isfile(map_path):
            self.map.load(map_path)

            self.camera_pos.x = self.palette_surface.get_width() + self.map.width * 16
            self.camera_pos.y = self.map.height * 16 - self.settings_surface.get_height() / 2

            self.updatesize_tilesurface()
            return True
        else:
            print("Could not find map!")
            return False

    def map_save(self, mapname=""):
        if not mapname:
            mapname = self.map.name
        map_path = "../data/maps/" + mapname
        if self.map.save(map_path):
            print("Map " + mapname + " saved.")
        else:
            print("No map loaded!")

    def map_new(self, name, xsize, ysize):
        self.map.newmap(name, xsize, ysize)
        self.updatesize_tilesurface()

    def map_resize(self, newsize_x, newsize_y):
        self.map.resize(newsize_x, newsize_y)
        self.updatesize_tilesurface()

    def map_changetile(self, tx, ty, newtile, flags, foreg=False):
        try:
            changed_tile = self.map.map_data[ty][tx]

            # Flags list including subflags
            flags_full = []
            # Keep foreground flag
            tmp_foreg_flag = changed_tile.find_subflag("fg")
            if tmp_foreg_flag:
                flags_full.append(tmp_foreg_flag)

            for f in flags:
                tmp_flag = f.split('/')
                if len(tmp_flag) == 1:
                    flags_full.append(tmp_flag[0])
                else:
                    flags_full.append(tmp_flag)
            changed_tile.flags = flags_full

            if not foreg:
                changed_tile.set_tile(newtile)
            else:
                changed_tile.set_foreg(newtile)

            return True
        except: pass
        return False

    def set_inputmode(self, active, action="", info="", inp=""):
        self.inputting = active
        if self.inputting:
            self.input_action = action
            self.text_info = info
            self.text_input = inp
            return True

        self.input_data = {}
        return False

    def main_loop(self):
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
            mouse_pos32x, mouse_pos32y = math.floor(mouse_pos[0] / 32), math.floor(mouse_pos[1] / 32)
            # Mouse tile position within map surface
            mouse_tileposx, mouse_tileposy = 0, 0
            if self.map.loaded:
                mouse_tileposx = min(max(math.floor((mouse_pos[0] - self.camera_pos.x) / 32), 0), self.map.width - 1)
                mouse_tileposy = min(max(math.floor((mouse_pos[1] - self.camera_pos.y) / 32), 0), self.map.height - 1)

            # Keyboard keys held
            if not self.inputting:
                self.keys_held = pygame.key.get_pressed()
            # Mouse buttons held
            self.mouse_held = pygame.mouse.get_pressed()

            # Selection rect update
            upd_rel_sect = False

            # Pygame event polling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    # Inputting
                    if self.inputting:
                        if event.key == pygame.K_RETURN: # Enter - process input
                            inp_react = False
                            if self.input_action == "save": # Save map
                                self.map_save(self.text_input)
                            elif self.input_action == "load": # Load map
                                self.map_load(self.text_input)
                            elif self.input_action == "newmap_name": # New map name
                                self.text_input = self.text_input.strip()
                                if not self.text_input:
                                    print("New map - Invalid map name!")
                                else:
                                    self.input_data[self.input_action] = self.text_input
                                    self.set_inputmode(True, "newmap_x", "New map X size > ")
                                    inp_react = True
                            elif self.input_action == "newmap_x" or self.input_action == "newmap_y": # New map size data
                                try:
                                    tmp_mapsize_data = int(self.text_input)
                                except (TypeError, ValueError):
                                    print("New map - You must enter a number!")
                                else:
                                    if tmp_mapsize_data > 0:
                                        self.input_data[self.input_action] = tmp_mapsize_data
                                        if self.input_action == "newmap_x":
                                            self.set_inputmode(True, "newmap_y", "New map Y size > ")
                                            inp_react = True
                                        else: # New map done (if more flags are needed, add them here and continue processing)
                                            self.map_save()
                                            print("Creating new map \"" + self.input_data["newmap_name"] + "\"...")
                                            self.map_new(self.input_data["newmap_name"], self.input_data["newmap_x"], self.input_data["newmap_y"])
                                    else:
                                        print("New map - Invalid number!")

                            elif self.input_action == "resizemap_x" or self.input_action == "resizemap_y": # Resize map
                                try:
                                    tmp_newsize = int(self.text_input)
                                except (TypeError, ValueError):
                                    print("Resize map - You must enter a number!")
                                else:
                                    if tmp_newsize > 0:
                                        self.input_data[self.input_action] = tmp_newsize
                                        if self.input_action == "resizemap_x":
                                            self.set_inputmode(True, "resizemap_y", "Resize, new Y > ")
                                            inp_react = True
                                        else:
                                            print("Resizing map to " + str(self.input_data["resizemap_x"]) + " x " + str(self.input_data["resizemap_y"]) + "...")
                                            self.map_resize(self.input_data["resizemap_x"], self.input_data["resizemap_y"])
                                    else:
                                        print("Resize map - Invalid number!")

                            elif self.input_action == "setflag":
                                self.newtileflags = self.text_input.strip().split(':')

                            if not inp_react:
                                self.set_inputmode(False, "")

                        elif event.key == pygame.K_BACKSPACE:
                            self.text_input = self.text_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.set_inputmode(False, "")
                        else:
                            self.text_input += event.unicode

                    else: # Normal keypress
                        if self.keys_held[pygame.K_LSHIFT]: # Shift + key
                            if event.key == pygame.K_s: # SHIFT + S, save map
                                self.set_inputmode(True, "save", "Save map as > ", self.map.name)
                            elif event.key == pygame.K_l: # SHIFT + L, load map
                                self.set_inputmode(True, "load", "Load map > ")
                            elif event.key == pygame.K_n: # SHIFT + N, new map
                                self.set_inputmode(True, "newmap_name", "New map name > ")
                            elif event.key == pygame.K_r: # SHIFT + R, resize current map
                                self.set_inputmode(True, "resizemap_x", "Resize, new X > ")
                            elif event.key == pygame.K_f: # SHIFT + F, set flags for newly placed tiles
                                if not self.newtileflags:
                                    self.newtileflags = []
                                    self.set_inputmode(True, "setflag", "Flags > ")
                                else: # Toggle off if active
                                    self.newtileflags = []

                        elif event.key == pygame.K_f: # F, set foreground mode
                            self.foreg_mode = not self.foreg_mode
                        elif event.key == pygame.K_DOWN: # Down arrow, scroll palette down
                            self.palette_pad = max(0, min(self.palette_pad_av, self.palette_pad + 1))
                            upd_rel_sect = True
                        elif event.key == pygame.K_UP: # Up arrow, scroll palette up
                            self.palette_pad = max(0, min(self.palette_pad_av, self.palette_pad - 1))
                            upd_rel_sect = True

            # Camera movement
            mv_axis = [0, 0]
            cam_spd = 10
            if self.keys_held[pygame.K_LALT]: # fast movement (lalt)
                cam_spd = 25
            if self.keys_held[pygame.K_d]:  # right
                mv_axis[0] = cam_spd
            elif self.keys_held[pygame.K_a]:  # left
                mv_axis[0] = -cam_spd
            if self.keys_held[pygame.K_w]:  # up
                mv_axis[1] = -cam_spd
            elif self.keys_held[pygame.K_s]:  # down
                mv_axis[1] = cam_spd
            self.camera_pos -= mv_axis

            # Left/Right mouse button held
            for i in range(2):
                if self.mouse_held[i*2]: # get mouse held 0(left) and 2(right)
                    if self.palette_surface.get_rect().collidepoint(mouse_pos):  # Mouse in palette, selecting tile
                        try:
                            self.selected_tile[i] = self.map.tile_palette[mouse_pos32x + (mouse_pos32y + self.palette_pad) * self.map.palette_rowlen].tile_id
                            upd_rel_sect = True
                        except IndexError: pass
                    else:  # Mouse x > palette x, placing tile in map
                        # CTRL key - Tile picker
                        if self.keys_held[pygame.K_LCTRL]:
                            self.selected_tile[i] = self.map.map_data[mouse_tileposy][mouse_tileposx].tile_id
                            upd_rel_sect = True
                        else: # Place tile
                            if self.foreg_mode:
                                if i == 0:
                                    self.map_changetile(mouse_tileposx, mouse_tileposy, self.selected_tile[i], [], True)
                                else:
                                    self.map_changetile(mouse_tileposx, mouse_tileposy, -1, [], True)
                            else:
                                self.map_changetile(mouse_tileposx, mouse_tileposy, self.selected_tile[i], self.newtileflags, False)

            self.display.fill((0, 0, 0))

            self.spr_list_palette.draw(self.palette_surface) # Draw tiles to palette surface
            # Draw maptiles to map surface
            vis_tiles = pygame.sprite.LayeredDirty()
            # Visibility range in X axis
            vis_x_min = max(0, math.floor((self.palette_surface.get_width() - self.camera_pos.x) / 32))
            vis_x_max = max(0, math.ceil((self.display.get_width() - self.camera_pos.x) / 32))
            # Visibility range in Y axis
            vis_y_min = max(0, math.floor((-self.camera_pos.y) / 32))
            vis_y_max = max(0, math.ceil((self.display.get_height() - self.camera_pos.y) / 32))
            for i in range(vis_x_min, vis_x_max):
                if i > self.map.width:
                    break
                for j in range(vis_y_min, vis_y_max):
                    if j > self.map.height:
                        break
                    try:
                        tmp_maptile = self.map.map_data[j][i]
                        vis_tiles.add(tmp_maptile)
                        if tmp_maptile.foreg_tile:
                            vis_tiles.add(tmp_maptile.foreg_tile)
                    except IndexError:
                        pass

            vis_tiles.draw(self.tiles_surface)

            # Draw map surface
            self.display.blit(self.tiles_surface, self.camera_pos)

            # Draw palette surface
            self.display.blit(self.palette_surface, (0,-self.palette_pad * 32))
            pygame.draw.rect(self.display, (255,255,255), self.palette_surface.get_rect(), 1)

            # Draw settings surface
            self.settings_surface.fill((0,0,0))
            # Modes info text
            str_modes = ""
            if self.foreg_mode:
                str_modes += "Foreground / "

            tmp_textrender = self.font.render("Active modes: " + str_modes, False, self.font_color)
            self.settings_surface.blit(tmp_textrender, (4,4))

            # Flags info text
            if self.newtileflags:
                tmp_textrender = self.font.render("Flags: " + str(self.newtileflags), False, self.font_color)
                self.settings_surface.blit(tmp_textrender, (4, 36))

            # Selected tile info
            try:
                tmp_tile = self.map.map_data[mouse_tileposy][mouse_tileposx]
                if tmp_tile:
                    tmp_textrender = self.font.render("x: " + str(tmp_tile.pos[0]) + " y: " + str(tmp_tile.pos[1]) + " flags: " + str(tmp_tile.flags), False, self.font_color)
                    self.display.blit(tmp_textrender, (self.palette_surface.get_width() + 4, 0))
            except IndexError:
                pass

            # Save/load info text
            if self.inputting:
                tmp_textrender = self.font.render(self.text_info + self.text_input, False, self.font_color)
                self.settings_surface.blit(tmp_textrender, (4, self.settings_surface.get_height() - tmp_textrender.get_height() - 4))

            self.display.blit(self.settings_surface, (0, self.display.get_height() - self.settings_surface.get_height()))

            if self.map.loaded:
                # Selection rectangle
                # Mouse outside palette, editing map
                if not self.palette_surface.get_rect().collidepoint(mouse_pos):
                    pygame.draw.rect(self.display, (200, 127, 30), (self.camera_pos.x + mouse_tileposx * 32, self.camera_pos.y + mouse_tileposy * 32, 32, 32), 1)
                else: # Selecting tile
                    pygame.draw.rect(self.display, (220, 220, 50), (math.floor(mouse_pos[0] / 32) * 32, math.floor(mouse_pos[1] / 32) * 32, 32, 32), 1)

            # Selected tile rectangle (primary/secondary)
            if upd_rel_sect:
                for i in range(2):
                    rect_sel[i][1].topleft = (self.selected_tile[i] % self.map.palette_rowlen * 32 + i,
                                              math.floor((self.selected_tile[i] - self.palette_pad * self.map.palette_rowlen) / self.map.palette_rowlen) * 32 + i)
            for r in rect_sel:
                pygame.draw.rect(self.display, r[0], r[1], 1)

            pygame.display.update(self.display.get_rect())

            self.clock.tick(60)