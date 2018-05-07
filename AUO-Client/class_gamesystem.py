from class_player import *
from patcher import *
from Mastermind import *
import pygame
import os.path

class GameSystem(object):
    def __init__(self):
        self.conn = MastermindClientTCP(30.0)
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
        self.conn.send("join|" + str(self.player.char))
        self.conn.send("pl_move|" + str(self.player.pos.x) + "|" + str(self.player.pos.y))

    def init_display(self, disp_w, disp_h):
        self.display = pygame.display.set_mode((disp_w, disp_h))

    def main_loop(self):
        done = False

        ping_ticker = 300
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            self.server_listener()

            self.keys_held = pygame.key.get_pressed()
            self.player_loop()

            self.display.fill((0,0,0))

            self.spritelist.update()
            self.spritelist.draw(self.display)

            pygame.display.update()
            self.clock.tick(60)

            if ping_ticker > 0:
                ping_ticker -= 1
            else:
                self.conn.send("ping")
                ping_ticker = 300

        self.conn.disconnect()

    def player_loop(self):
        # Player movement
        mv_axis = [0, 0]
        if self.keys_held[pygame.K_KP6] or self.keys_held[pygame.K_KP9] or self.keys_held[pygame.K_KP3]:  # right
            mv_axis[0] = 1
        elif self.keys_held[pygame.K_KP4] or self.keys_held[pygame.K_KP1] or self.keys_held[pygame.K_KP7]:  # left
            mv_axis[0] = -1
        if self.keys_held[pygame.K_KP8] or self.keys_held[pygame.K_KP7] or self.keys_held[pygame.K_KP9]:  # up
            mv_axis[1] = -1
        elif self.keys_held[pygame.K_KP2] or self.keys_held[pygame.K_KP1] or self.keys_held[pygame.K_KP3]:  # down
            mv_axis[1] = 1

        if not (mv_axis[0] == 0 and mv_axis[1] == 0):
            if self.player.move_axis(mv_axis):
                self.conn.send("pl_move|" + str(self.player.pos.x) + "|" + str(self.player.pos.y))

    def server_listener(self):
        server_data = self.conn.receive(False)
        if server_data:
            #print(server_data)
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