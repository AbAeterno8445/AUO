from class_tile import Tile
import pygame
from math import floor

class GameMap(object):
    def __init__(self):
        self.name = "N/A"
        self.width = 0
        self.height = 0

        self.default_light = 0

        self.tile_texture = pygame.image.load("tileset.png")
        self.tile_texture.set_colorkey((255,0,255))

        self.palette_rowlen = 10
        self.tile_palette = []
        for i in range(256):
            self.tile_palette.append(Tile(i, self.tile_texture, (i % self.palette_rowlen, floor(i / self.palette_rowlen))))

        self.loaded = False
        self.map_data = []

    # Create new map given size
    def newmap(self, newname, size_x, size_y):
        self.loaded = False
        self.name = newname
        self.width = size_x
        self.height = size_y

        self.map_data = []
        for h in range(size_y):
            self.map_data.append([])
            for w in range(size_x):
                tmp_tile = Tile(0, self.tile_texture, (w,h))
                self.map_data[h].append(tmp_tile)
        self.loaded = True

    # Resize currently loaded map
    def resize(self, newsize_x, newsize_y):
        if self.loaded:
            # Resize Y axis
            if newsize_y > self.height:
                for i in range(newsize_y - self.height):
                    self.map_data.append([])
                    for j in range(self.width):
                        tmp_tile = Tile(0, self.tile_texture, (j,len(self.map_data)-1))
                        self.map_data[-1].append(tmp_tile)
            elif newsize_y < self.height:
                for i in range(self.height - newsize_y):
                    self.map_data.remove(self.map_data[-1])
            self.height = newsize_y

            # Resize X axis
            if newsize_x > self.width:
                for i in range(self.height):
                    for j in range(newsize_x - self.width):
                        tmp_tile = Tile(0, self.tile_texture, (len(self.map_data[i]), i))
                        self.map_data[i].append(tmp_tile)
            elif newsize_x < self.width:
                for i in range(self.height):
                    for j in range(self.width - newsize_x):
                        self.map_data[i].remove(self.map_data[i][-1])
            self.width = newsize_x

    # Saves currently loaded map to the given path
    def save(self, map_path=None):
        if map_path is None:
            map_path = "../data/maps/" + self.name
        if self.loaded:
            with open(map_path, "w+") as mapfile:
                # Save map name
                mapfile.write(self.name + "\n")

                # Save map size
                mapfile.write(str(self.width) + "," + str(self.height) + "\n")

                # Save map default light level
                mapfile.write(str(self.default_light) + "\n")

                # Save map tile data
                for row in self.map_data:
                    for i, tile in enumerate(row):
                        mapfile.write(str(tile.tile_id))
                        for f in tile.flags:
                            mapfile.write(":")
                            if type(f) is list:
                                mapfile.write("/".join(f))
                            else:
                                mapfile.write(f)
                        if i < len(row) - 1:
                            mapfile.write(",")
                    mapfile.write("\n")
            return True
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