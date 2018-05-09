import select, socket, sys, traceback, os
from class_client import Client
from class_map import GameMap
from random import randint
from Mastermind import *

class Server(MastermindServerUDP):
    client_list = {}
    id_table = []
    map_list = {}

    def __init__(self):
        MastermindServerUDP.__init__(self, time_connection_timeout=10.0)

        for i, map in enumerate(os.listdir("data/maps")):
            newmap = GameMap(self, i, map)
            self.map_list[map] = newmap

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

        return super(MastermindServerUDP, self).callback_connect_client(conn)

    # Close existing client connection
    def callback_disconnect_client(self, conn):
        if conn in self.client_list:
            disc_client = self.client_list[conn]

            print("Lost connection to client " + str(disc_client.id))
            disc_client.current_map.player_leave(disc_client)
            self.id_table.remove(disc_client.id)
            self.client_list.pop(conn, None)

        return super(MastermindServerUDP, self).callback_disconnect_client(conn)

    # Process incoming client messages
    def callback_client_handle(self, conn, data):
        try:
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
                inc_client.filedl_current = open(data[1], "r")

            elif data[0] == "filedl_next": # Send file data on request
                line = inc_client.filedl_current.read(1450)
                if line:
                    self.callback_client_send(conn, "filedl|" + data[1] + "|" + line)
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

                inc_client.current_map = self.map_list["town"]
                self.callback_client_send(conn, "loadmap|town|spawn")
                inc_client.current_map.player_enter(inc_client)

            elif data[0] == "disconnect": # Player disconnection
                self.callback_disconnect_client(conn)

            elif data[0] == "xfer_map": # Map transfer
                inc_client.current_map.player_leave(inc_client)
                inc_client.current_map = self.map_list[data[1]]
                inc_client.current_map.player_enter(inc_client)

            elif data[0] == "pl_move": # Player movement
                inc_client.pos.x = float(data[1])
                inc_client.pos.y = float(data[2])
                for cl in self.client_list:
                    if cl is not conn:
                        self.callback_client_send(cl, "update_pl|" + str(self.client_list[conn].id) + "|" + str(data[1]) + "|" + str(data[2]))

            elif data[0] == "ping": # Maintain connection alive
                self.callback_client_send(conn, "pong")
        except:
            print("An exception occured while handling data from client " + str(conn.address))

        return super(MastermindServerUDP, self).callback_client_handle(conn, data)
