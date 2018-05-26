class Client(object):
    def __init__(self, id, conn):
        self.id = id
        self.conn = conn

        self.acc_name = ""
        self.acc_pw = ""
        self.acc_characters = []

        self.current_map = None

        # Server-side stats shared with client
        self.mult_stats = ["char", "maxhp", "hp", "atk", "atkspd", "speed", "xp", "level", "sightrange", "light"]

        self.name = ""
        self.x = 0
        self.y = 0
        self.char = 0
        self.maxhp = 20
        self.hp = 20
        self.atk = 1
        self.atkspd = 0.5
        self.speed = 0.4
        self.sightrange = 16
        self.light = 3

        self.xp = 0
        self.xp_req = 0
        self.level = 1

        # File download list for patcher
        self.filedl_list = []
        with open("filetransfer_list", "r") as xferfile:
            for l in xferfile:
                l = l.strip('\n')
                self.filedl_list.append(l)

    def get_shared_stats(self):
        tmp_statlist = []
        for s in self.mult_stats:
            tmp_statlist.append((s, getattr(self, s, 0)))
        return tmp_statlist

    def load_from_file(self):
        if self.name:
            with open("players/" + self.name, "r") as char_file:
                for l in char_file:
                    l = l.strip().split(':')
                    if len(l) > 1:
                        try: l[1] = int(l[1])
                        except ValueError:
                            try: l[1] = float(l[1])
                            except ValueError: pass

                        setattr(self, l[0], l[1])

    def save_to_file(self):
        if self.name:
            with open("players/" + self.name, "w") as char_file:
                for s in self.mult_stats:
                    char_file.write(s + ":" + str(getattr(self, s, 0)) + "\n")