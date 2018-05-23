from class_tile import Tile
import pygame
from math import floor

class GameMap(object):
    def __init__(self):
        self.name = "N/A"
        self.width = 0
        self.height = 0

        self.spawnpos = (1, 1)

        self.default_light = 16
        self.animated_tiles = []
        self.anim_state = 0

        self.tile_texture = pygame.image.load("assets/tileset.png")
        self.tile_texture.set_colorkey((255,0,255))
        self.tile_texture_gs = pygame.image.load("assets/tileset_gs.png")
        self.tile_texture_gs.set_colorkey((255,0,255))
        self.loaded = False
        self.map_data = []

    # Check if a tile at (x,y) is walkable
    def freetile(self, x, y):
        try:
            if self.map_data[y][x].has_flag("wall"):
                return False
            return True
        except:
            return False

    def transfer_level(self, x, y):
        try:
            return self.map_data[y][x].find_subflag("xfer")
        except:
            return False

    # Loads a map given a map file, returns list of tiles loaded
    def load(self, map_path):
        self.loaded = False
        try:
            with open(map_path, "r") as mapfile:
                # Load map name
                self.name = mapfile.readline().strip()

                # Load map size
                size = mapfile.readline().split(',')
                self.width, self.height = [int(i) for i in size]

                # Load map default light level
                self.default_light = int(mapfile.readline().strip())

                # Load map tile data
                self.map_data = []
                self.animated_tiles = []
                for y in range(self.height):
                    row = mapfile.readline().strip().split(',')
                    self.map_data.append([])
                    for x, tile_string in enumerate(row):
                        tile_data = tile_string.split(':')

                        tile_flags = []
                        for flag in tile_data[1:]:
                            flag = flag.split('/') # Sub-flags
                            if len(flag) == 1:
                                tile_flags.append(flag[0])
                            else:
                                tile_flags.append(flag)
                        newtile = Tile(int(tile_data[0]), self.tile_texture, self.tile_texture_gs, (x,y), tile_flags)
                        # Tile is spawnpoint
                        if newtile.has_flag("spawn"):
                            self.spawnpos = (x, y)

                        # Animated tile
                        if newtile.tile_id >= 84 and newtile.tile_id <= 95:
                            self.animated_tiles.append(newtile)

                        self.map_data[y].append(newtile)
            self.loaded = True

        except ValueError:
            print("Error while loading map [" + map_path + "]: wrong format!")
            return False

        return self.map_data

    def get_visible_tiles(self):
        tmp_tilelist = []
        for row in self.map_data:
            for tile in row:
                if tile.light_visible:
                    tmp_tilelist.append(tile)

        return tmp_tilelist

    def anim_tiles(self):
        self.anim_state = (self.anim_state + 1) % 4
        for tile in self.animated_tiles:
            tile.anim(self.anim_state)

    def do_fov(self, x, y, radius, row, start_slope, end_slope, xx, xy, yx, yy):
        if start_slope < end_slope: return

        next_start_slope = start_slope
        for i in range(row, radius + 1):
            blocked = False
            for dx in range(-i, 1):
                dy = -i
                l_slope = (dx - 0.5) / (dy + 0.5)
                r_slope = (dx + 0.5) / (dy - 0.5)

                if start_slope < r_slope: continue
                elif end_slope > l_slope: break

                sax = dx * xx + dy * xy
                say = dx * yx + dy * yy
                if (sax < 0 and abs(sax) > x) or (say < 0 and abs(say) > y): continue

                ax = x + sax
                ay = y + say
                if ax >= self.width or ay >= self.height: continue

                try:
                    tmp_tile = self.map_data[ay][ax]
                except IndexError:
                    continue
                else:
                    # Tile is visible
                    if dx ** 2 + dy ** 2 < radius ** 2:
                        tmp_tile.light_visible = True
                        tmp_tile.explored = True

                    if blocked:
                        if tmp_tile.has_flag("bv"):
                            next_start_slope = r_slope
                            continue
                        else:
                            blocked = False
                            start_slope = next_start_slope
                    elif tmp_tile.has_flag("bv"):
                        blocked = True
                        next_start_slope = r_slope
                        self.do_fov(x, y, radius, i + 1, start_slope, l_slope, xx, xy, yx, yy)
            if blocked: break

    def cast_fov(self, x, y, radius, player=False, x_min=None, x_max=None, y_min=None, y_max=None):
        multipliers = [
            [1, 0, 0, -1, -1, 0, 0, 1],
            [0, 1, -1, 0, 0, -1, 1, 0],
            [0, 1, 1, 0, 0, -1, -1, 0],
            [1, 0, 0, 1, -1, 0, 0, -1]
        ]

        if not x_min or not x_max or not y_min or not y_max:
            for row in self.map_data:
                for tile in row:
                    tile.light_visible = False
        else:
            for i in range(x_min, x_max):
                if i > self.width:
                    break
                for j in range(y_min, y_max):
                    if j > self.height:
                        break
                    try:
                        self.map_data[j][i].light_visible = False
                    except IndexError:
                        pass

        if player:
            self.map_data[y][x].light_visible = True

        for i in range(8):
            self.do_fov(x, y, radius, 1, 1.0, 0.0, multipliers[0][i], multipliers[1][i], multipliers[2][i], multipliers[3][i])

    # Casts a light at a position
    def lighting_cast(self, source_x, source_y, strength):
        for tile in self.get_visible_tiles():
            dist = abs(tile.pos[0] - source_x) + abs(tile.pos[1] - source_y)

            newlevel = min(16, floor(tile.lightlevel + 16 - 16 * dist / strength))
            if newlevel > tile.lightlevel:
                tile.set_lightlevel(newlevel)

    def lighting_update(self, players):
        vis_tiles = self.get_visible_tiles()
        # Reset tile lighting
        for tile in vis_tiles:
            tile.set_lightlevel(self.default_light, True)

        # Player lights
        for pl in players:
            self.lighting_cast(pl.x, pl.y, pl.light)

        # Light emitting tiles
        for tile in vis_tiles:
            lightflag = tile.find_subflag("light")
            if lightflag:
                self.lighting_cast(tile.pos[0], tile.pos[1], int(lightflag[1]))