import select, socket, sys, queue, traceback, os, struct
from random import randint
from class_client import Client

class Server(object):
    buff_size = 2048

    inputs = []
    outputs = []
    client_list = {}
    id_table = []

    def __init__(self, addr, port, maxclients=10):
        self.sv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.inputs.append(self.sv_sock)
        self.sv_sock.setblocking(0)

        if addr == "gethost":
            addr = socket.gethostbyname(socket.gethostname())
        self.sv_sock.bind((addr, port))
        print("Server started, address " + addr + ", port " + str(port))
        self.sv_sock.listen(maxclients)

    def run(self):
        print("Running...")
        try:
            while self.inputs:
                readable, writable, exceptional = select.select(
                    self.inputs, self.outputs, self.inputs)
                for s in readable:
                    if s is self.sv_sock:
                        connection, client_address = s.accept()
                        connection.setblocking(0)

                        self.newClient(connection, client_address)
                    else:
                        try:
                            size = struct.unpack("i", s.recv(struct.calcsize("i")))[0]
                            data = b""
                            while len(data) < size:
                                msg = s.recv(size - len(data))
                                if not msg:
                                    print("Disconnected client while reading incoming message.")
                                    self.removeClient(s)
                                data += msg
                            self.processClientData(s, data.decode('utf-8'))
                        except struct.error:
                            print("Could not read struct data from client. May be caused by client disconnection.")
                            self.removeClient(s)
                        except:
                            print("An exception occured while receiving data from client " + str(self.client_list[s].id) + str(self.client_list[s].address))
                            print(traceback.print_exc())
                            self.removeClient(s)

                for s in writable:
                    try:
                        next_msg = self.client_list[s].queue_get()
                    except queue.Empty:
                        self.outputs.remove(s)
                    else:
                        s.sendall(struct.pack("i", len(next_msg)) + next_msg)

                for s in exceptional:
                    self.removeClient(s)
        except:
            print(traceback.print_exc())
            print("An exception has occured, server shutting down...")
            self.sv_sock.close()
            return False

    # Get unique id #, used for client id assignment
    def get_unique_id(self):
        i = 0
        while True:
            if i not in self.id_table:
                self.id_table.append(i)
                return i
            i += 1

    # Accept new client
    def newClient(self, cl_sock, client_address):
        print("Received connection from " + str(client_address))

        tmp_client = Client(self.get_unique_id(), cl_sock, client_address)
        self.client_list[cl_sock] = tmp_client
        print("Assigned id " + str(tmp_client.id))

        self.sendDataToClient(cl_sock, "Welcome! Your id is " + str(tmp_client.id))

        self.inputs.append(cl_sock)

    # Close existing client connection
    def removeClient(self, cl_sock):
        if cl_sock in self.outputs:
            self.outputs.remove(cl_sock)
        self.inputs.remove(cl_sock)

        if cl_sock in self.client_list:
            left_id = self.client_list[cl_sock].id

            print("Lost connection to client " + str(left_id))
            self.id_table.remove(left_id)
            del self.client_list[cl_sock]

            # Inform other players this one left
            for cl in self.client_list:
                self.sendDataToClient(cl, "remove_pl|" + str(left_id))

        cl_sock.close()

    # Send data to a client
    def sendDataToClient(self, cl_sock, data):
        self.client_list[cl_sock].queue_data(data.encode('utf-8'))

        if cl_sock not in self.outputs:
            self.outputs.append(cl_sock)

    # Process incoming client messages
    def processClientData(self, cl_sock, data):
        print("Received data from client " + str(self.client_list[cl_sock].id) + ": " + data)

        inc_client = self.client_list[cl_sock] # Incoming client

        data = data.split('|')
        if data[0] == "filedl_check": # Check for outdated files from client
            try:
                fpath = next(iter(inc_client.filedl_list))
                self.sendDataToClient(cl_sock, "filedl_begin|" + fpath + "|" + str(os.path.getsize(fpath)))
            except StopIteration:
                self.sendDataToClient(cl_sock, "filedl_end")

        elif data[0] == "filedl_ok": # Outdated file in client, send current one
            with open(data[1], "r") as f:
                for l in f:
                    self.sendDataToClient(cl_sock, "filedl|" + data[1] + "|" + l)
            self.sendDataToClient(cl_sock, "filedl_done|" + data[1])
            inc_client.filedl_list.pop(data[1], None)

        elif data[0] == "filedl_uptodate": # File is updated, keep iterating
            inc_client.filedl_list.pop(data[1], None)

        elif data[0] == "join": # New player joins
            # Assign id to joining player
            self.sendDataToClient(cl_sock, "assign_id|" + str(inc_client.id))

            inc_client.char = int(data[1])

            for cl, other_cl in self.client_list.items():
                if cl is not cl_sock:
                    # Send other players info about joining player
                    self.sendDataToClient(cl, "new_pl|" + str(inc_client.id) + "|" + str(inc_client.char))
                    # Send joining player info about other players
                    self.sendDataToClient(cl_sock, "new_pl|" + str(other_cl.id) + "|" + str(other_cl.char))
                    self.sendDataToClient(cl_sock, "update_pl|" + str(other_cl.id) + "|" + str(other_cl.pos.x) + "|" + str(other_cl.pos.y))

        elif data[0] == "pl_move": # Player movement
            inc_client.pos.x = float(data[1])
            inc_client.pos.y = float(data[2])
            for cl in self.client_list:
                if cl is not cl_sock:
                    self.sendDataToClient(cl, "update_pl|" + str(self.client_list[cl_sock].id) + "|" + str(data[1]) + "|" + str(data[2]))