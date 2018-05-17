import pygame
from math import floor

class Tile(pygame.sprite.DirtySprite):
    def __init__(self, tile_id, texture, texture_gs, pos, flags=None):
        pygame.sprite.DirtySprite.__init__(self)
        self.texture = texture
        self.texture_gs = texture_gs
        self.grayscaled = False

        self.pos = pos
        self.draw_pos = (pos[0] * 32, pos[1] * 32)
        self.tile_id = tile_id
        self.set_tile(tile_id)
        if not flags:
            flags = []
        self.flags = flags

        self.rect = self.image.get_rect(topleft=self.draw_pos)

        self.foreg_tile = None
        foreg_tile_data = self.find_subflag("fg")
        if foreg_tile_data:
            self.set_foreg(int(foreg_tile_data[1]))

        self.dirty = 1

        # Illumination/visibility
        self.light_visible = False
        self.explored = False
        self.lightlevel = 0

        self.wallshadow = None

    def get_wallshadow(self):
        if self.wallshadow is None:
            self.wallshadow = pygame.sprite.DirtySprite()
            self.wallshadow.image = pygame.image.load("assets/wallshadow.png")
            self.wallshadow.rect = self.wallshadow.image.get_rect(topleft=(self.draw_pos[0] - 8, self.draw_pos[1] - 8))
        return self.wallshadow

    def toggle_grayscale(self, gs=None):
        if self.foreg_tile:
            self.foreg_tile.toggle_grayscale(gs)
        if gs is None:
            self.set_tile(self.tile_id, not self.grayscaled)
        else:
            if not self.grayscaled == gs:
                self.grayscaled = gs
                self.set_tile(self.tile_id, self.grayscaled)

    def set_tile(self, new_tile, grayscale=False):
        self.tile_id = new_tile
        tmp_texture = self.texture
        if grayscale:
            tmp_texture = self.texture_gs
        self.image = tmp_texture.subsurface(((self.tile_id % 16) * 32 + (self.tile_id % 16) * 2, floor(self.tile_id / 16) * 32 + floor(self.tile_id / 16) * 2, 32, 32))

    def set_lightlevel(self, newlevel):
        if self.foreg_tile:
            self.foreg_tile.set_lightlevel(newlevel)
        self.lightlevel = newlevel
        self.update_lightlevel()

    def update_lightlevel(self):
        self.image.set_alpha(max(0, min(255, self.lightlevel * 16)))

    # Set foreground tile. -1 removes current foreground
    def set_foreg(self, foreg_tile):
        foreg_flag = self.find_subflag("fg")
        if foreg_tile == -1:
            self.foreg_tile = None
            self.flags.remove(foreg_flag)
            return False

        # Alter foreground tile object
        if not self.foreg_tile: # New foreground tile
            self.foreg_tile = Tile(foreg_tile, self.texture, self.texture_gs, self.pos)
            self.foreg_tile.dirty = 2
        else:
            self.foreg_tile.set_tile(foreg_tile)

        # Alter flag
        if not foreg_flag:
            self.flags.append(["fg", str(foreg_tile)])
        else:
            foreg_flag[1] = str(foreg_tile)
        return True

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