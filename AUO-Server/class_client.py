from pygame.math import Vector2
import queue

class Client(object):
    def __init__(self, id, sock=None, address=None):
        self.id = id
        self.connect(sock, address)

        self.pos = Vector2(0, 0)
        self.char = 0

        self.msg_queue = queue.Queue()

        # File download list for patcher
        self.filedl_list = {}
        with open("filetransfer_list", "r") as xferfile:
            for l in xferfile:
                l = l.strip('\n')
                with open(l, "r") as f:
                    self.filedl_list[l] = f.readlines()

    def connect(self, sock, address):
        self.sock = sock
        self.address = address

    def queue_get(self, nowait=True):
        if nowait:
            return self.msg_queue.get_nowait()
        return self.msg_queue.get()

    def queue_data(self, data):
        self.msg_queue.put(data)