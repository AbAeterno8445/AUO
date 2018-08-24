from math import floor
from random import randint
import pygame

class Item(pygame.sprite.DirtySprite):
    texture = pygame.image.load("assets/itemset.png")

    def __init__(self, item, pos=(0,0)):
        pygame.sprite.DirtySprite.__init__(self)

        self.name = ""
        self.x = pos[0]
        self.y = pos[1]
        self.anim_frames = 0
        self.set_item(item)

        self.tickers = {
            "anim": [0, 0]
        }

        self.block_movement = False

    def set_subsurf(self, item):
        self.image = Item.texture.subsurface(((item % 16) * 32 + (item % 16) * 2, floor(item / 16) * 32 + floor(item / 16) * 2, 32, 32))
        self.image.set_colorkey((255, 0, 255))

    def set_item(self, item):
        self.item_id = item
        self.set_subsurf(item)
        self.rect = self.image.get_rect(topleft=(self.x * 32, self.y * 32))

    def set_position(self, x, y):
        self.x, self.y = x, y

    def anim(self):
        if self.anim_frames > 0:
            item_rand = self.item_id + randint(0, self.anim_frames)
            self.set_subsurf(item_rand)