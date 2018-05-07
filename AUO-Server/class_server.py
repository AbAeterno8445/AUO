import select, socket, sys, queue, traceback, os, struct
from random import randint
from class_client import Client
from Mastermind import *

class Server(MastermindServerTCP):
    client_list = {}
    id_table = []

    def __init__(self):
        MastermindServerTCP.__init__(self, time_connection_timeout=30.0)

    # Get unique id #, used for client id assignment
    def get_unique_id(self):
        i = 0
        while True:
            if i not in self.id_table:
                self.id_table.append(i)
                return i
            i += 1

    # Client connects - create new client obj
    def callback_connect_client(self, conn):
        print("Received connection from " + str(conn.address))

        tmp_client = Client(self.get_unique_id(), conn)
        self.client_list[conn] = tmp_client
        print("Assigned id " + str(tmp_client.id))

        return super(MastermindServerTCP, self).callback_connect_client(conn)

    # Close existing client connection
    def callback_disconnect_client(self, conn):
        if conn in self.client_list:
            left_id = self.client_list[conn].id

            print("Lost connection to client " + str(left_id))
            self.id_table.remove(left_id)
            self.client_list.pop(conn, None)

            # Inform other players this one left
            for cl in self.client_list:
                self.callback_client_send(cl, "remove_pl|" + str(left_id))

        return super(MastermindServerTCP, self).callback_disconnect_client(conn)

    # Process incoming client messages
    def callback_client_handle(self, conn, data):
        print("Received data from client " + str(self.client_list[conn].id) + ": " + data)

        inc_client = self.client_list[conn] # Incoming client object

        data = data.split('|')
        if data[0] == "filedl_check": # Check for outdated files from client
            try:
                fpath = next(iter(inc_client.filedl_list))
                self.callback_client_send(conn, "filedl_begin|" + fpath + "|" + str(os.path.getsize(fpath)))
            except StopIteration:
                self.callback_client_send(conn, "filedl_end")

        elif data[0] == "filedl_ok": # Outdated file in client, send current one
            inc_client.filedl_current = open(data[1], "rb")

        elif data[0] == "filedl_next": # Send file data on request
            line = inc_client.filedl_current.read(1400)
            if line:
                self.callback_client_send(conn, "filedl|" + data[1] + "|" + line.decode('utf-8'))
            else:
                self.callback_client_send(conn, "filedl_done|" + data[1])
                inc_client.filedl_current.close()
                inc_client.filedl_list.remove(data[1])

        elif data[0] == "filedl_uptodate": # File is updated, keep iterating
            inc_client.filedl_list.remove(data[1])

        elif data[0] == "join": # New player joins
            # Assign id to joining player
            self.callback_client_send(conn, "assign_id|" + str(inc_client.id))

            inc_client.char = int(data[1])

            for cl, other_cl in self.client_list.items():
                if cl is not conn:
                    # Send other players info about joining player
                    self.callback_client_send(cl, "new_pl|" + str(inc_client.id) + "|" + str(inc_client.char))
                    # Send joining player info about other players
                    self.callback_client_send(conn, "new_pl|" + str(other_cl.id) + "|" + str(other_cl.char))
                    self.callback_client_send(conn, "update_pl|" + str(other_cl.id) + "|" + str(other_cl.pos.x) + "|" + str(other_cl.pos.y))

        elif data[0] == "pl_move": # Player movement
            inc_client.pos.x = float(data[1])
            inc_client.pos.y = float(data[2])
            for cl in self.client_list:
                if cl is not conn:
                    self.callback_client_send(cl, "update_pl|" + str(self.client_list[conn].id) + "|" + str(data[1]) + "|" + str(data[2]))

        elif data[0] == "ping": # Maintain connection alive
            self.callback_client_send(conn, "pong")

        return super(MastermindServerTCP, self).callback_client_handler(conn, data)