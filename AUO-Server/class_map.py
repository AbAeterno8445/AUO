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
                self.server.callback_client_send(other_cl.conn, "update_pl|" + str(client.id) + "|" + str(client.pos.x) + "|" + str(client.pos.y))
                # Send joining player info about other players
                self.server.callback_client_send(client.conn, "new_pl|" + str(other_cl.id) + "|" + str(other_cl.char))
                self.server.callback_client_send(client.conn, "update_pl|" + str(other_cl.id) + "|" + str(other_cl.pos.x) + "|" + str(other_cl.pos.y))

    def player_leave(self, client):
        for cl in self.client_list:
            if cl is not client:
                # Remove leaving player for other players
                self.server.callback_client_send(cl.conn, "remove_pl|" + str(client.id))
                # Remove other players for leaving player
                self.server.callback_client_send(client.conn, "remove_pl|" + str(cl.id))
        self.client_list.remove(client)

    def send_all(self, data, exc=None):
        for cl in self.client_list:
            if cl == exc:
                continue
            self.server.callback_client_send(cl.conn, data)