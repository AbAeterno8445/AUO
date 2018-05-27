from class_entity import Entity
from math import floor

class Player(Entity):
    def __init__(self, id, pos, char):
        Entity.__init__(self, id, pos, char)

        self.xp = 0
        self.xp_req = 0
        self.level = 1
        self.calc_xp_req()

    def calc_xp_req(self):
        lv = self.level + 1
        self.xp_req = int(floor((lv ** 2 + lv) / 2 * 100 - (lv * 100)))

    def set_stat(self, stat, value):
        Entity.set_stat(self, stat, value)
        if stat == "level":
            self.calc_xp_req()