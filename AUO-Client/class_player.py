from pygame.math import Vector2
from math import floor
from random import randint
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, id, pos, char):
        pygame.sprite.Sprite.__init__(self)

        self.id = id

        self.pos = Vector2(pos[0],pos[1])
        self.vel = [0, 0]
        self.speed = 5

        self.ogchar = char
        self.char = self.ogchar
        self.char_anim = 0

        self.ogimage = pygame.image.load("assets/charset_1.png")
        self.ogimage = pygame.transform.scale2x(self.ogimage)
        self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16)*2, floor(self.char / 16) * 32 + floor(self.char / 16)*2, 32, 32))

        self.rect = self.image.get_rect()

    def move_axis(self, axes):
        self.vel = [axes[0] * self.speed, axes[1] * self.speed]

    def set_pos(self, px, py):
        self.pos.x, self.pos.y = px, py
        self.update()

    def update(self):
        self.pos += self.vel
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

        self.char_anim += 1
        if self.char_anim == 20:
            self.char = self.ogchar + randint(0,3)
            self.updatechar()
            self.char_anim = 0

    def updatechar(self):
        self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16)*2, floor(self.char / 16) * 32 + floor(self.char / 16)*2, 32, 32))