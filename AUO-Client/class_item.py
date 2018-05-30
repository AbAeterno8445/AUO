from math import floor
import pygame

class Item(pygame.sprite.DirtySprite):
    texture = pygame.image.load("assets/itemset.png")

    def __init__(self, item, pos=(0,0)):
        pygame.sprite.DirtySprite.__init__(self)
        self.set_item(item)

        self.name = ""
        self.x = pos[0]
        self.y = pos[1]

        self.blocks = False

    def set_item(self, item):
        self.item_id = item
        self.image = Item.texture.subsurface(((item % 16) * 32, floor(item / 16) * 32, 32, 32))
        self.rect = self.image.get_rect()

    def set_position(self, x, y):
        self.x, self.y = x, y