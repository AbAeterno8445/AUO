from class_screen import Screen
from class_entity import Entity
from patcher import *

from class_map import GameMap
from math import *
from pygame.math import Vector2
import pygame, os.path, base64

class Screen_Game(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.conn = None

        self.player = None
        self.map = GameMap()

        self.game_surface = None
        self.entity_surface = None
        self.camera_pos = Vector2(0, 0)

        self.keys_held = []

        self.playerlist = {}

        self.acc_name = ""
        self.acc_pw = ""

        self.ping_ticker = 300  # Ping (keeps connection alive)
        self.anim_ticker = 30  # Tile animations

        # Map drawing layers
        self.updatelayers = False
        self.vis_tiles = pygame.sprite.LayeredDirty()
        self.spritelist = pygame.sprite.LayeredDirty()

    def setup(self, conn, display, player):
        Screen.setup(self, display)

        self.conn = conn

        self.player = player
        self.spritelist.empty()
        self.spritelist.add(self.player)
        self.spritelist.change_layer(self.player, 1)

        self.game_surface = pygame.Surface(self.display.get_size())
        self.entity_surface = pygame.Surface(self.display.get_size()).convert()
        self.entity_surface.set_colorkey((255, 0, 255))

    def update_account_data(self, name, pw):
        self.acc_name = name
        self.acc_pw = pw

    def connect(self, host, port, mode=None):
        print("Connecting to " + host + " using port " + str(port) + "...")
        try: self.conn.connect(host, port)
        except OSError as err:
            print(err)
            return False

        try:
            if mode == "connect_newacc": # Connect to create new account
                self.conn.send("acc_create|" + self.acc_name + "|" + base64.b64encode(self.acc_pw.encode('utf-8')).decode('utf-8'))

                acc_creation = self.conn.receive(True)
                print("Connected. Creating account \"" + self.acc_name + "\"...")
                if acc_creation == "acc_create_fail":
                    print("Account creation failed. An account with that name already exists!")
                    self.conn.send("disconnect")
                    self.conn.disconnect()
                    return False

                print("Account created successfully! You may now create characters with it.")
                self.conn.send("disconnect")
                self.conn.disconnect()
                return True

            elif mode == "connect_newchar" or mode == "connect_continuechar": # Connect with new character
                self.conn.send("login|" + self.acc_name + "|" + base64.b64encode(self.acc_pw.encode('utf-8')).decode('utf-8'))

                login_attempt = self.conn.receive(True)
                print("Connected. Authenticating...")
                if login_attempt == "login_fail":
                    print("Authentication failed. Wrong credentials!")
                    self.conn.send("disconnect")
                    self.conn.disconnect()
                    return False

                if mode == "connect_newchar":  # New character creation
                    self.conn.send("newchar|" + self.player.name + "|" + str(self.player.char))
                    char_creation = self.conn.receive(True)
                    if char_creation == "newchar_fail":
                        print("Could not create new character. Name is already taken!")
                        self.conn.send("disconnect")
                        self.conn.disconnect()
                        return False
                    print("Created new character \"" + self.player.name + "\".")

                else:  # Continue with existing character
                    self.conn.send("continuechar|" + self.player.name)
                    char_continue = self.conn.receive(True)
                    if char_continue == "continuechar_fail":
                        print("Character not found!")
                        self.conn.send("disconnect")
                        self.conn.disconnect()
                        return False
                    print("Loaded character \"" + self.player.name + "\".")

                patcher = Patcher(self.conn)
                print("Running patcher...")
                patcher.check_uptodate()
                print("Patching process done.")

                self.conn.send("join")
                return True

        except ConnectionResetError:
            self.conn.disconnect()
            return False

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
        tmp_newsize = (self.map.width * 32, self.map.height * 32)
        self.game_surface = pygame.transform.scale(self.game_surface, tmp_newsize)
        self.entity_surface = pygame.transform.scale(self.game_surface, tmp_newsize).convert()
        self.entity_surface.set_colorkey((255, 0, 255))

    def load_map(self, mapname):
        map_path = "data/maps/" + mapname
        map_tiles = self.map.load(map_path)

        self.updatesize_tilesurface()
        self.update_drawlayers()

    def update_drawlayers(self):
        # Update field of view
        self.map.cast_fov(self.player.x, self.player.y, self.player.sightrange, True)
        # Update illumination
        self.map.lighting_update(self.player.x, self.player.y, self.player.light)

        self.game_surface.fill((0,0,0))
        self.vis_tiles.empty()
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

                    if not tmp_maptile.light_visible and tmp_maptile.explored:
                        tmp_maptile.toggle_grayscale(True)
                        tmp_maptile.set_lightlevel(3)
                    else:
                        tmp_maptile.toggle_grayscale(False)
                        tmp_maptile.update_lightlevel()

                    if tmp_maptile.light_visible or tmp_maptile.explored:
                        if tmp_maptile.has_flag("wall"):
                            self.vis_tiles.add(tmp_maptile)
                            self.vis_tiles.change_layer(tmp_maptile, 2)
                        else:
                            self.vis_tiles.add(tmp_maptile)
                            self.vis_tiles.change_layer(tmp_maptile, 0)

                        if tmp_maptile.has_flag("shadow"):  # Emit shadow
                            tmp_wallshadow = tmp_maptile.get_wallshadow()
                            self.vis_tiles.add(tmp_wallshadow)
                            self.vis_tiles.change_layer(tmp_wallshadow, 1)

                        if tmp_maptile.foreg_tile:  # Foreground tile
                            tmp_foreg = tmp_maptile.foreg_tile
                            self.vis_tiles.add(tmp_foreg)
                            self.vis_tiles.change_layer(tmp_foreg, 3)

                    # Illumination overlay
                    light_overlay = tmp_maptile.get_light_overlay()
                    self.vis_tiles.add(light_overlay)
                    self.vis_tiles.change_layer(light_overlay, 4)

                except IndexError:
                    pass

    # Draws players over visible tiles
    def update_drawplayers(self):
        for pl_id, pl_obj in self.playerlist.items():
            if self.spritelist.has(pl_obj):
                self.spritelist.remove(pl_obj)
            try:
                if self.map.map_data[int(pl_obj.y)][int(pl_obj.x)].light_visible:
                    self.spritelist.add(pl_obj)
                    self.spritelist.change_layer(pl_obj, 0)
            except IndexError:
                pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                newlevel_data = self.map.transfer_level(self.player.x, self.player.y)
                if newlevel_data:
                    self.conn.send("xfer_map|" + newlevel_data[1])
                    self.load_map(newlevel_data[1])
                    self.player.set_pos(int(newlevel_data[2]), int(newlevel_data[3]))
                    self.update_camera_plpos()

        return Screen.handle_event(self, event)

    def loop(self):
        if not self.conn.is_connected():
            print("Could not connect to server.")
            return "menu_main"

        for event in pygame.event.get():
            if not self.handle_event(event):
                return False

        self.server_listener()

        self.keys_held = pygame.key.get_pressed()
        self.player_loop()

        self.entity_surface.fill((255,0,255))

        # Tile animations
        if self.anim_ticker > 0:
            self.anim_ticker -= 1
        else:
            self.map.anim_tiles()
            self.anim_ticker = 30

        if self.updatelayers:
            self.update_drawlayers()
            self.updatelayers = False

        self.vis_tiles.draw(self.game_surface)

        if self.map.loaded:
            # Draw game surface (tiles)
            self.display.blit(self.game_surface, self.camera_pos)
            # Draw sprites
            self.update_drawplayers()
            self.spritelist.update()
            self.spritelist.draw(self.entity_surface)
            self.display.blit(self.entity_surface, self.camera_pos)

        # Keep connection alive
        if self.ping_ticker > 0:
            self.ping_ticker -= 1
        else:
            self.conn.send("ping")
            self.ping_ticker = 300

        if self.newscreen:
            return self.newscreen
        return True

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
            self.updatelayers = True
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
                newplayer = Entity(int(server_data[1]), self.map.spawnpos, (int(server_data[2]), 4))
                self.playerlist[int(server_data[1])] = newplayer
                self.spritelist.add(newplayer)

            elif server_data[0] == "remove_pl": # Remove player
                try:
                    tmp_player = self.playerlist[int(server_data[1])]
                except NameError:
                    pass
                else:
                    self.spritelist.remove(tmp_player)
                    self.playerlist.pop(int(server_data[1]), None)

            elif server_data[0] == "update_pl": # Update player position
                try: self.playerlist[int(server_data[1])].set_pos(float(server_data[2]), float(server_data[3]))
                except KeyError: pass

            elif server_data[0] == "setstat_pl": # Update player stat
                try:
                    value = server_data[3]
                    try:
                        value = int(value)
                    except ValueError:
                        pass

                    if not int(server_data[1]) == -1:
                        setattr(self.playerlist[int(server_data[1])], server_data[2], value)
                    else:
                        setattr(self.player, server_data[2], value)
                except KeyError: pass