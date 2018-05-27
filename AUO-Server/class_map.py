class GameMap(object):
    def __init__(self, server, id, name):
        self.server = server
        self.id = id
        self.name = name
        self.client_list = []

    def player_enter(self, client):
        self.client_list.append(client)
        for other_cl in self.client_list:
            if other_cl is not client:
                # Send other players info about joining player
                self.server.callback_client_send(other_cl.conn, "new_pl|" + str(client.id) + "|" + str(client.char))
                self.server.callback_client_send(other_cl.conn, "update_pl|" + str(client.id) + "|" + str(client.x) + "|" + str(client.y))
                # Send joining player info about other players
                self.server.callback_client_send(client.conn, "new_pl|" + str(other_cl.id) + "|" + str(other_cl.char))
                self.server.callback_client_send(client.conn, "update_pl|" + str(other_cl.id) + "|" + str(other_cl.x) + "|" + str(other_cl.y))

    def player_leave(self, client):
        for cl in self.client_list:
            if cl is not client:
                # Remove leaving player for other players
                self.server.callback_client_send(cl.conn, "remove_pl|" + str(client.id))
                # Remove other players for leaving player
                self.server.callback_client_send(client.conn, "remove_pl|" + str(cl.id))
        self.client_list.remove(client)

    # Sends a message from chatter player to everyone nearby (8 tile radius)
    def player_localchat(self, chatter, msg):
        if not chatter in self.client_list:
            return

        self.server.callback_client_send(chatter.conn, "pl_chat|" + chatter.name + "|local|" + msg)
        for cl in self.client_list:
            if not cl == chatter:
                dist = abs(chatter.x - cl.x) + abs(chatter.y - cl.y)
                if dist <= 8:
                    self.server.callback_client_send(cl.conn, "pl_chat|" + chatter.name + "|local|" + msg)

    def send_all(self, data, exc=None):
        for cl in self.client_list:
            if cl == exc:
                continue
            self.server.callback_client_send(cl.conn, data)