import select, socket, sys, traceback, os, base64
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
            disc_client_name = disc_client.name

            print("Lost connection to client " + str(disc_client.id))
            if disc_client.current_map:
                disc_client.current_map.player_leave(disc_client)
            self.id_table.remove(disc_client.id)
            self.client_list.pop(conn, None)

            for cl in self.client_list:
                if disc_client_name:
                    self.client_send_message(cl, disc_client_name + " has left the game.", (100,100,100))

        return super(MastermindServerUDP, self).callback_disconnect_client(conn)

    def account_exists(self, name, pw=None):
        with open("data/accounts", "r") as acc_file:
            for line in acc_file:
                line = line.strip().split(':')
                if (line[0] == name and line[1] == pw) or (line[0] == name and pw == None):
                    return True
        return False

    def character_in_account(self, acc_name, char_name):
        with open("data/account-chars", "r") as acc_file:
            for line in acc_file:
                line = line.strip().split(':')
                if line[0] == acc_name and line[1] == char_name:
                    return True
        return False

    # Process incoming client messages
    def callback_client_handle(self, conn, data):
        if conn not in self.client_list:
            return super(MastermindServerUDP, self).callback_client_handle(conn, data)

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

        elif data[0] == "acc_create": # Client account creation
            cl_acc_name = data[1]
            cl_acc_pw = data[2]

            if self.account_exists(cl_acc_name):
                self.callback_client_send(conn, "acc_create_fail")
            else:
                with open("data/accounts", "a") as acc_file:
                    acc_file.write(cl_acc_name + ":" + cl_acc_pw + "\n")
                self.callback_client_send(conn, "acc_create_ok")

        elif data[0] == "login": # Client account login
            cl_acc_name = data[1]
            cl_acc_pw = data[2]

            if self.account_exists(cl_acc_name, cl_acc_pw):
                logged = False
                for cl in self.client_list:
                    if self.client_list[cl].acc_name == cl_acc_name:
                        logged = True
                        break

                if logged:
                    self.callback_client_send(conn, "login_logged")
                else:
                    inc_client.acc_name = cl_acc_name
                    inc_client.acc_pw = cl_acc_pw
                    self.callback_client_send(conn, "login_ok")
            else:
                self.callback_client_send(conn, "login_noacc")

        elif data[0] == "newchar": # New player character
            if data[1] not in os.listdir("players"):
                inc_client.name = data[1]
                inc_client.char = data[2]
                inc_client.save_to_file()

                with open("data/account-chars", "a") as acc_file:
                    acc_file.write(inc_client.acc_name + ":" + inc_client.name + "\n")

                self.callback_client_send(conn, "newchar_ok")
            else:
                self.callback_client_send(conn, "newchar_fail")

        elif data[0] == "continuechar": # Continues with existing character
            if self.character_in_account(inc_client.acc_name, data[1]):
                inc_client.name = data[1]
                inc_client.load_from_file()

                self.callback_client_send(conn, "continuechar_ok")
            else:
                self.callback_client_send(conn, "continuechar_fail")

        elif data[0] == "join": # Player joins
            # Assign id to joining player
            self.callback_client_send(conn, "setstat_pl|-1|id/" + str(inc_client.id))

            inc_client.current_map = self.map_list["town"]
            self.callback_client_send(conn, "loadmap|town|spawn")
            inc_client.current_map.player_enter(inc_client)

            for cl in self.client_list:
                if not cl == inc_client.conn:
                    self.client_send_message(cl, inc_client.name + " has joined the game.", (100,100,100))
                    self.callback_client_send(inc_client.conn, "setstat_pl|" + str(self.client_list[cl].id) + self.client_statsmsg(self.client_list[cl]))

            self.client_update_stats(inc_client, inc_client.get_shared_stats())

        elif data[0] == "disconnect": # Player disconnection
            self.callback_disconnect_client(conn)

        elif data[0] == "xfer_map": # Map transfer
            inc_client.current_map.player_leave(inc_client)
            inc_client.current_map = self.map_list[data[1]]
            inc_client.current_map.player_enter(inc_client)

        elif data[0] == "pl_move": # Player movement
            self.client_setposition(inc_client.conn, int(data[1]), int(data[2]))

        elif data[0] == "pl_chat": # Player chat
            if data[1].startswith("/"): # Commands
                cmd_success = False
                cmd_sub = data[1].split(" ")

                try:
                    if cmd_sub[0] == "/who":  # Check who's online
                        cmd_success = True
                        onlinepl_msg = ""
                        for cl in self.client_list:
                            if self.client_list[cl].name:
                                onlinepl_msg += self.client_list[cl].name + " "
                        onlinepl_msg = onlinepl_msg.strip().replace(" ", ", ")
                        self.client_send_message(inc_client.conn, "Online players: " + onlinepl_msg)

                    elif cmd_sub[0] == "/g": # Global chat
                        cmd_success = True
                        for cl in self.client_list:
                            self.callback_client_send(cl, "pl_chat|" + inc_client.name + "|global|" + " ".join(cmd_sub[1:]))

                    elif cmd_sub[0] == "/msg": # Whisper message
                        cmd_success = True
                        if len(cmd_sub) > 2:
                            whisp_plname = cmd_sub[1].replace('_', ' ')
                            whisp_msg = " ".join(cmd_sub[2:])

                            if whisp_plname == inc_client.name:
                                self.client_send_message(inc_client.conn, "You mutter to yourself: " + whisp_msg, (102,102,255))
                            else:
                                pl_found = False
                                for cl in self.client_list:
                                    if self.client_list[cl].name == whisp_plname and not cl == inc_client.conn:
                                        pl_found = True
                                        self.client_send_message(inc_client.conn, "Sent message to " + whisp_plname + ": " + whisp_msg, (102,102,255))
                                        self.callback_client_send(self.client_list[cl].conn, "pl_chat|" + inc_client.name + "|whisper|" + whisp_msg)
                                        break
                                if not pl_found:
                                    self.client_send_message(inc_client.conn, "Player " + whisp_plname + " not found.", (220,50,50))
                        else:
                            self.client_send_message(inc_client.conn, "Usage: /msg <player name> <message>", (220,50,50))
                except IndexError:
                    cmd_success = False

                if not cmd_success:
                    self.client_send_message(inc_client.conn, "Unknown command.", (220,50,50))
            elif inc_client.current_map: # Local chat
                inc_client.current_map.player_localchat(inc_client, data[1])

        elif data[0] == "ping": # Maintain connection alive
            self.callback_client_send(conn, "pong")

        return super(MastermindServerUDP, self).callback_client_handle(conn, data)

    def client_send_message(self, cl_sock, message, color=(255,255,255)):
        self.callback_client_send(cl_sock, "msg|" + message + "|" + str(color[0]) + "," + str(color[1]) + "," + str(color[2]))

    def client_setposition(self, cl_sock, x, y):
        inc_client = self.client_list[cl_sock]
        inc_client.x = x
        inc_client.y = y
        if inc_client.current_map:
            inc_client.current_map.send_all("update_pl|" + str(inc_client.id) + "|" + str(x) + "|" + str(y), inc_client)

    # Changes server-side stats then updates
    # Stats is a list of sub-lists [(<stat name>, <new value>), ...]
    def client_set_stats(self, client, stats, update):
        for s in stats:
            setattr(client, s[0], s[1])
        if update:
            self.client_update_stats(client, stats)

    # Update clients with server-side stats
    def client_update_stats(self, client, stats, upd_self=True):
        if upd_self:
            self.callback_client_send(client.conn, "setstat_pl|-1" + self.client_statsmsg(client))
        if client.current_map:
            client.current_map.send_all("setstat_pl|" + str(client.id) + self.client_statsmsg(client), client)

    def client_statsmsg(self, client):
        stat_upd_msg = ""
        for s in client.get_shared_stats():
            stat_upd_msg += "|" + s[0] + "/" + str(s[1])
        return stat_upd_msg