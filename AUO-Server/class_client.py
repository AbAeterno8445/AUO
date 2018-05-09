from pygame.math import Vector2

class Client(object):
    def __init__(self, id, conn):
        self.id = id
        self.conn = conn

        self.pos = Vector2(0, 0)
        self.char = 0

        # File download list for patcher
        self.filedl_list = []
        with open("filetransfer_list", "r") as xferfile:
            for l in xferfile:
                l = l.strip('\n')
                self.filedl_list.append(l)