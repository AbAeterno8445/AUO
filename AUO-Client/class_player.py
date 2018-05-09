from pygame.math import Vector2
from math import floor
from random import randint
import pygame

class Player(pygame.sprite.DirtySprite):
    def __init__(self, id, pos, char):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 2

        self.id = id
        self.name = ""
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 0.4
        self.speed_cd = 0

        self.ogchar = char
        self.char = self.ogchar
        self.char_anim = 0

        self.ogimage = pygame.image.load("assets/charset_1.png")
        self.ogimage = pygame.transform.scale2x(self.ogimage)
        self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16)*2, floor(self.char / 16) * 32 + floor(self.char / 16)*2, 32, 32))
        self.rect = self.image.get_rect()

    def move_axis(self, axes, map):
        if self.speed_cd <= 0:
            newpos_x = self.x + axes[0]
            newpos_y = self.y + axes[1]
            if map.freetile(newpos_x, newpos_y):
                self.speed_cd = floor(self.speed * 60)
                self.x = newpos_x
                self.y = newpos_y
                return True
        return False

    def set_pos(self, px, py):
        self.x, self.y = px, py
        self.update()

    def update(self):
        self.rect.x = self.x * 32
        self.rect.y = self.y * 32

        if self.speed_cd > 0:
            self.speed_cd = self.speed_cd - 1

        # Character animation
        self.char_anim += 1
        if self.char_anim == 20:
            self.char = self.ogchar + randint(0,3)
            self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16) * 2,
                                                  floor(self.char / 16) * 32 + floor(self.char / 16) * 2, 32, 32))
            self.char_anim = 0