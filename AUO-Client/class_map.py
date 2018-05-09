import pygame
from math import floor

class GameMap(object):
    def __init__(self):
        self.name = "N/A"
        self.width = 0
        self.height = 0

        self.spawnpos = (1, 1)

        self.tile_texture = pygame.image.load("assets/tileset.png")
        self.tile_texture = pygame.transform.scale2x(self.tile_texture)
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

                # Load map tile data
                self.map_data = []
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
                        newtile = Tile(int(tile_data[0]), self.tile_texture, (x,y), tile_flags)
                        # Tile is spawnpoint
                        if newtile.has_flag("spawn"):
                            self.spawnpos = (x, y)

                        self.map_data[y].append(newtile)
            self.loaded = True

        except ValueError:
            print("Error while loading map [" + map_path + "]: wrong format!")
            return False

        return self.map_data

class Tile(pygame.sprite.DirtySprite):
    def __init__(self, tile_id, texture, pos, flags=[]):
        pygame.sprite.DirtySprite.__init__(self)

        self.pos = [pos[0] * 32, pos[1] * 32]
        self.tile_id = tile_id
        self.flags = flags

        self.texture = texture
        self.image = self.get_tile_from_texture(self.tile_id)
        self.rect = self.image.get_rect(topleft=self.pos)

        self.foreg_tile = None
        foreg_tile_data = self.find_subflag("fg")
        if foreg_tile_data:
            self.foreg_tile = Tile(int(foreg_tile_data[1]), texture, pos)

        self.dirty = 1

    # Returns a 32x32 surface positioned at the given tile for the texture loaded by the tile
    # Texture must be loaded beforehand and have 16 tiles per row. Tiles must be 32x32
    def get_tile_from_texture(self, tile):
        return self.texture.subsurface(((tile % 16) * 32 + (tile % 16)*2, floor(tile / 16) * 32 + floor(tile / 16)*2, 32, 32))

    def has_flag(self, flag):
        if type(flag) is list:
            for f in flag:
                if f in self.flags:
                    return True
        else:
            if flag in self.flags:
                return True
        return False

    def find_subflag(self, flag):
        for f in self.flags:
            if type(f) is list:
                if f[0] == flag:
                    return f
        return False