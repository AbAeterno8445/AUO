from class_player import *
from class_map import GameMap
from patcher import *
from Mastermind import *
from math import *
from pygame.math import Vector2
import pygame
import os.path

class GameSystem(object):
    def __init__(self):
        self.conn = MastermindClientUDP(10.0)
        self.patcher = Patcher(self.conn)
        self.map = GameMap()

        self.display = None
        self.game_surface = None
        self.camera_pos = Vector2(0, 0)
        self.clock = pygame.time.Clock()

        self.keys_held = []

        self.playerlist = []

        self.spritelist = pygame.sprite.LayeredDirty()

    def init_display(self, disp_w, disp_h):
        self.display = pygame.display.set_mode((disp_w, disp_h))
        self.disp_size = (disp_w, disp_h)
        self.game_surface = pygame.Surface((disp_w, disp_h))
        pygame.display.set_icon(pygame.image.load("assets/AUOicon.png"))
        pygame.display.set_caption("AUO Client")

    # Update camera to player position
    def update_camera_plpos(self):
        # Camera X axis
        if self.player.x * 32 > self.display.get_width() / 2:
            self.camera_pos.x = -self.player.x * 32 + self.display.get_width() / 2
        else:
            self.camera_pos.x = 0
        # Camera Y axis
        if self.player.y * 32 > self.display.get_height() / 2:
            self.camera_pos.y = -self.player.y * 32 + self.display.get_height() / 2
        else:
            self.camera_pos.y = 0

    # Update tile surface size to map size
    def updatesize_tilesurface(self):
        self.game_surface = pygame.transform.scale(self.game_surface, (self.map.width * 32, self.map.height * 32))

    def connect(self, host, port):
        print("Connected to " + host + " using port " + str(port) + ".")
        self.conn.connect(host, port)

        print("Running patcher...")
        self.patcher.check_uptodate()
        print("Patching process done.")

        self.create_player()

    def create_player(self):
        self.player = Player(-1, (1,1), randint(0, 63) * 4)
        self.spritelist.add(self.player)
        self.spritelist.change_layer(self.player, 1)
        self.conn.send("join|" + str(self.player.char))
        self.conn.send("pl_move|" + str(self.player.x) + "|" + str(self.player.y))

    def load_map(self, mapname):
        map_path = "data/maps/" + mapname
        map_tiles = self.map.load(map_path)

        self.updatesize_tilesurface()

    def main_loop(self):
        ping_ticker = 300

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        newlevel_data = self.map.transfer_level(self.player.x, self.player.y)
                        if newlevel_data:
                            self.conn.send("xfer_map|" + newlevel_data[1])
                            self.load_map(newlevel_data[1])
                            self.player.set_pos(int(newlevel_data[2]), int(newlevel_data[3]))
                            self.update_camera_plpos()

            self.server_listener()

            self.keys_held = pygame.key.get_pressed()
            self.player_loop()

            self.spritelist.update()

            self.display.fill((0,0,0))
            self.game_surface.fill((0,0,0))

            # Draw map
            vis_tiles = pygame.sprite.LayeredDirty()
            vis_walls = pygame.sprite.LayeredDirty()
            # Visibility range in X axis
            vis_x_min = max(0, floor(-self.camera_pos.x / 32))
            vis_x_max = max(0, ceil((self.display.get_width() - self.camera_pos.x) / 32))
            # Visibility range in Y axis
            vis_y_min = max(0, floor(-self.camera_pos.y / 32))
            vis_y_max = max(0, ceil((self.display.get_height() - self.camera_pos.y) / 32))
            # Rendering walls and shadows in order
            walls_list = []
            for i in range(vis_x_min, vis_x_max):
                if i > self.map.width:
                    break
                for j in range(vis_y_min, vis_y_max):
                    if j > self.map.height:
                        break
                    try:
                        tmp_maptile = self.map.map_data[j][i]

                        if tmp_maptile.light_visible:
                            tmp_maptile.toggle_grayscale(False)
                            tmp_maptile.set_lightlevel(16)
                        elif tmp_maptile.explored:
                            tmp_maptile.toggle_grayscale(True)
                            tmp_maptile.set_lightlevel(8)

                        if tmp_maptile.light_visible or tmp_maptile.explored:
                            if tmp_maptile.has_flag("wall"):
                                walls_list.append(tmp_maptile)
                                vis_walls.add(tmp_maptile.get_wallshadow())
                            else:
                                vis_tiles.add(tmp_maptile)
                            if tmp_maptile.foreg_tile:  # Foreground tile
                                vis_tiles.add(tmp_maptile.foreg_tile)

                    except IndexError:
                        pass

            for w in walls_list:
                vis_walls.add(w)

            vis_tiles.draw(self.game_surface)
            vis_walls.draw(self.game_surface)

            # Draw sprites
            self.spritelist.draw(self.game_surface)
            self.display.blit(self.game_surface, self.camera_pos)

            pygame.display.update()
            self.clock.tick(60)

            # Keep connection alive
            if ping_ticker > 0:
                ping_ticker -= 1
            else:
                self.conn.send("ping")
                ping_ticker = 300

        self.conn.send("disconnect")
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
            if self.player.move_axis(mv_axis, self.map):
                self.conn.send("pl_move|" + str(self.player.x) + "|" + str(self.player.y))

        # Update player's map visibility
        if self.player.moved:
            self.update_camera_plpos()
            self.map.cast_light(self.player.x, self.player.y, 6, True)
            self.player.moved = False

    def server_listener(self):
        server_data = self.conn.receive(False)
        if server_data:
            #print(server_data)
            server_data = server_data.split('|')
            if server_data[0] == "assign_id": # ID assignment
                self.player.id = int(server_data[1])

            elif server_data[0] == "loadmap": # Map loading / set player pos
                self.load_map(server_data[1])
                if server_data[2] == "spawn":
                    self.player.set_pos(self.map.spawnpos[0], self.map.spawnpos[1])
                else:
                    pl_pos = server_data[2].split('/')
                    self.player.set_pos(int(pl_pos[0]), int(pl_pos[1]))
                self.conn.send("pl_move|" + str(self.player.x) + "|" + str(self.player.y))

            elif server_data[0] == "new_pl": # Create new player
                newplayer = Player(int(server_data[1]), self.map.spawnpos, int(server_data[2]))
                self.playerlist.append(newplayer)
                self.spritelist.add(newplayer)

            elif server_data[0] == "remove_pl": # Remove player
                for pl in self.playerlist:
                    if pl.id == int(server_data[1]):
                        self.spritelist.remove(pl)
                        self.playerlist.remove(pl)
                        break

            elif server_data[0] == "update_pl": # Update player position
                for pl in self.playerlist:
                    if pl.id == int(server_data[1]):
                        pl.set_pos(float(server_data[2]), float(server_data[3]))
                        break