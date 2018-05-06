import socket, queue, threading, struct, traceback

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
        conn_broken = False
        while not conn_broken:
            try:
                size = struct.unpack("i", self.sock.recv(struct.calcsize("i")))[0]
                data = b""
                while len(data) < size:
                    msg = self.sock.recv(size - len(data))
                    if not msg:
                        conn_broken = True
                        break
                    data += msg
                self.rec_queue.put(data.decode('utf-8'))
            except:
                print(traceback.print_exc())
                print("An exception occured in listener thread.")
                break

    def sender(self):
        while True:
            try:
                send_data = self.send_queue.get()
                send_data = send_data.encode('utf-8')
                self.sock.sendall(struct.pack("i", len(send_data)) + send_data)
            except:
                print(traceback.print_exc())
                print("An exception occured in sender thread.")
                break

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