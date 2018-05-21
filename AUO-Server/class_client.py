from pygame.math import Vector2

class Client(object):
    def __init__(self, id, conn):
        self.id = id
        self.conn = conn

        self.acc_name = ""
        self.acc_pw = ""
        self.acc_characters = []

        self.current_map = None

        self.name = ""

        self.pos = Vector2(0, 0)
        self.char = 0

        # File download list for patcher
        self.filedl_list = []
        with open("filetransfer_list", "r") as xferfile:
            for l in xferfile:
                l = l.strip('\n')
                self.filedl_list.append(l)

    def load_from_file(self):
        if self.name:
            with open("players/" + self.name, "r") as char_file:
                self.char = int(char_file.readline().strip())

    def save_to_file(self):
        if self.name:
            with open("players/" + self.name, "w") as char_file:
                char_file.write(str(self.char) + "\n")