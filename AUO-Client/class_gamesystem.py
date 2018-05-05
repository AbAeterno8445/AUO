from class_connection import *
from class_player import *
from patcher import *
import pygame
import os.path

class GameSystem(object):
    def __init__(self):
        self.conn = Connection()
        self.patcher = Patcher(self.conn)

        self.display = None
        self.clock = pygame.time.Clock()

        self.keys_held = []

        self.playerlist = []

        self.spritelist = pygame.sprite.Group()

    def connect(self, host, port):
        print("Connected to " + host + " using port " + str(port) + ".")
        self.conn.connect(host, port)

        print("Running patcher...")
        self.patcher.check_uptodate()
        print("Patching process done.")

        self.create_player()

    def create_player(self):
        self.player = Player(-1, (400, 300), randint(0, 63) * 4)
        self.spritelist.add(self.player)
        self.conn.send_data("join|" + str(self.player.char))
        self.conn.send_data("pl_move|" + str(self.player.pos.x) + "|" + str(self.player.pos.y))

    def init_display(self, disp_w, disp_h):
        self.display = pygame.display.set_mode((disp_w, disp_h))

    def main_loop(self):
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            self.data_handler()

            self.keys_held = pygame.key.get_pressed()
            self.player_loop()

            self.display.fill((0,0,0))

            self.spritelist.update()
            self.spritelist.draw(self.display)

            pygame.display.update()
            self.clock.tick(60)

        self.conn.shutdown()

    def player_loop(self):
        # Player movement
        mv_axis = [0, 0]
        if self.keys_held[pygame.K_d]:  # left
            mv_axis[0] = 1
        elif self.keys_held[pygame.K_a]:  # right
            mv_axis[0] = -1
        if self.keys_held[pygame.K_w]:  # up
            mv_axis[1] = -1
        elif self.keys_held[pygame.K_s]:  # down
            mv_axis[1] = 1
        self.player.move_axis(mv_axis)

        if not mv_axis[0] == 0 or not mv_axis[1] == 0:
            self.conn.send_data("pl_move|" + str(self.player.pos.x) + "|" + str(self.player.pos.y))

    def data_handler(self):
        server_data = self.conn.get_data()
        if server_data:
            # print(server_data)
            server_data = server_data.split('|')
            if server_data[0] == "assign_id": # ID assignment
                self.player.id = int(server_data[1])

            elif server_data[0] == "new_pl": # Create new player
                newplayer = Player(int(server_data[1]), (400, 300), int(server_data[2]))
                self.playerlist.append(newplayer)
                self.spritelist.add(newplayer)
                print("Player " + str(newplayer.id) + " has joined!")

            elif server_data[0] == "remove_pl": # Remove player
                for pl in self.playerlist:
                    if pl.id == int(server_data[1]):
                        print("Player " + str(pl.id) + " has left!")
                        self.spritelist.remove(pl)
                        self.playerlist.remove(pl)
                        break

            elif server_data[0] == "update_pl": # Update player position
                for pl in self.playerlist:
                    if pl.id == int(server_data[1]):
                        pl.set_pos(float(server_data[2]), float(server_data[3]))
                        break