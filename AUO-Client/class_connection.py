import socket, queue, threading

class Connection(object):
    buff_size = 2048

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.rec_queue = queue.Queue()
        self.send_queue = queue.Queue()

        self.conn_broken = False

    def connect(self, host_addr, port):
        self.sock.connect((host_addr, port))
        self.conn_broken = False

        threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.sender, daemon=True).start()

    def shutdown(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def listener(self):
        while not self.conn_broken:
            msg = self.sock.recv(self.buff_size)
            if msg:
                self.rec_queue.put(msg.decode('utf-8'))
            else:
                self.conn_broken = True

    def sender(self):
        while not self.conn_broken:
            send_data = self.send_queue.get()
            self.sock.sendall(send_data.encode('utf-8'))

    def get_data(self, wait=False):
        if wait:
            return self.rec_queue.get(True, 30)
        else:
            try:
                data = self.rec_queue.get_nowait()
            except queue.Empty:
                return False
            else:
                return data

    def send_data(self, data):
        self.send_queue.put(data)