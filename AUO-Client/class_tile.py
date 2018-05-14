import pygame
from math import floor

class Tile(pygame.sprite.DirtySprite):
    def __init__(self, tile_id, texture, pos, flags=[]):
        pygame.sprite.DirtySprite.__init__(self)

        self.pos = pos
        self.draw_pos = [pos[0] * 32, pos[1] * 32]
        self.tile_id = tile_id
        self.flags = flags

        self.texture = texture
        self.image = self.texture.subsurface(((self.tile_id % 16) * 32 + (self.tile_id % 16)*2, floor(self.tile_id / 16) * 32 + floor(self.tile_id / 16)*2, 32, 32))
        self.rect = self.image.get_rect(topleft=self.draw_pos)

        self.foreg_tile = None
        foreg_tile_data = self.find_subflag("fg")
        if foreg_tile_data:
            self.foreg_tile = Tile(int(foreg_tile_data[1]), texture, pos)

        self.dirty = 1

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