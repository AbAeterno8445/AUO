import json


class Client(object):
    def __init__(self, id, conn):
        self.id = id
        self.conn = conn

        self.acc_name = ""
        self.acc_pw = ""

        self.current_map = None

        # Server-side stats shared with client
        self.mult_stats = ["id", "name", "char", "maxhp", "hp", "atk", "atkspd", "speed", "xp", "level", "sightrange", "light"]

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

    # Returns list of shared stats [(stat1 name, value), (stat2 name, value), ...]
    def get_shared_stats(self):
        tmp_statlist = []
        for s in self.mult_stats:
            tmp_statlist.append((s, getattr(self, s, 0)))
        return tmp_statlist

    def get_json_data(self):
        json_dict = {}
        for s in self.mult_stats:
            json_dict[s] = getattr(self, s, 0)
        return json.dumps(json_dict)

    def load_json_data(self, json_data):
        json_dict = json.loads(json_data)
        for d in json_dict:
            setattr(self, d, json_dict[d])