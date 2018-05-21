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
        self.maxhp = 0
        self.hp = 0
        self.atk = 0
        self.atkspd = 0
        self.speed = 0.4

        self.xp = 0
        self.xp_req = 100
        self.level = 1

        self.tickers = {}
        self.tickers["move"] = 0
        self.tickers["char_anim"] = 0
        self.tickers["attack"] = 0

        self.sightrange = 6
        self.light = 3

        self.set_char(char)

        self.moved = False

    def set_stat(self, stat, value):
        if stat == "char":
            self.set_char(value)
        else:
            setattr(self, stat, value)

    def get_char_texture(self):
        return floor(self.char / 256)

    def set_char(self, char):
        self.char = char
        self.char_frames = 4  # Add check for 2-frame characters in the future

        self.ogimage = Entity.ent_textures[self.get_char_texture()]
        self.ogimage.set_colorkey((255, 0, 255))
        char_tile = self.char % 256
        self.image = self.ogimage.subsurface(((char_tile % 16) * 32 + (char_tile % 16) * 2, floor(char_tile / 16) * 32 + floor(char_tile / 16) * 2, 32, 32))
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
            char_rand = self.char % 256 + randint(0, self.char_frames - 1)
            self.image = self.ogimage.subsurface(((char_rand % 16) * 32 + (char_rand % 16) * 2,
                                                  floor(char_rand / 16) * 32 + floor(char_rand / 16) * 2, 32, 32))
            self.tickers["char_anim"] = 20