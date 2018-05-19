from pygame.math import Vector2
from math import floor
from random import randint
import pygame

class Entity(pygame.sprite.DirtySprite):
    # Character textures
    ent_textures = [
        pygame.image.load("assets/charset_1.png"),
        pygame.image.load("assets/charset_2.png"),
        pygame.image.load("assets/charset_3.png"),
        pygame.image.load("assets/charset_4.png"),
        pygame.image.load("assets/charset_5.png"),
        pygame.image.load("assets/charset_6.png"),
        pygame.image.load("assets/charset_7.png")
    ]

    def __init__(self, id, pos, char):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 2

        self.id = id
        self.name = ""
        self.x = pos[0]
        self.y = pos[1]
        self.maxhp = 100
        self.hp = 100
        self.atk = 1
        self.atkspd = 0.5
        self.speed = 0.4

        self.tickers = {}
        self.tickers["move"] = 0
        self.tickers["char_anim"] = 0
        self.tickers["attack"] = 0

        self.sightrange = 6
        self.light = 3

        self.ogchar = char
        self.char = self.ogchar[0]

        self.moved = False

        self.ogimage = Entity.ent_textures[2]
        self.ogimage.set_colorkey((255,0,255))
        self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16)*2, floor(self.char / 16) * 32 + floor(self.char / 16)*2, 32, 32))
        self.rect = self.image.get_rect()

    def move_axis(self, axes, map):
        if self.tickers["move"] <= 0:
            newpos_x = self.x + axes[0]
            newpos_y = self.y + axes[1]
            if map.freetile(newpos_x, newpos_y):
                self.tickers["move"] = floor(self.speed * 60)
                self.x = newpos_x
                self.y = newpos_y
                self.moved = True
                return True
        return False

    def set_pos(self, px, py):
        self.x, self.y = px, py
        self.moved = True
        self.update()

    def update(self):
        self.rect.x = self.x * 32
        self.rect.y = self.y * 32

        # Update tickers
        for ticker,tick_val in self.tickers.items():
            if tick_val > 0:
                self.tickers[ticker] = max(0, tick_val - 1)

        # Character animation
        if self.tickers["char_anim"] == 0:
            self.char = self.ogchar[0] + randint(0, self.ogchar[1] - 1)
            self.image = self.ogimage.subsurface(((self.char % 16) * 32 + (self.char % 16) * 2,
                                                  floor(self.char / 16) * 32 + floor(self.char / 16) * 2, 32, 32))
            self.tickers["char_anim"] = 20