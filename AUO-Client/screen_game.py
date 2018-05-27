from class_screen import Screen
from class_gui import GameGUI
from class_player import Player
from class_map import GameMap
from class_chatlog import ChatLog
from patcher import *

from math import *
from pygame.math import Vector2
import pygame, base64

class ScreenGame(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.conn = None

        # GUI variables
        self.gui = GameGUI((1,1))  # GameGUI object, loaded on setup
        self.gui_color = pygame.Color(20,20,20)
        self.gui_alpha = 255
        self.gui_font = pygame.font.Font("assets/fonts/monobit.ttf", 32)
        self.gui_font_small = pygame.font.Font("assets/fonts/monobit.ttf", 20)
        # Stats area
        self.gui_stats_width = 0
        self.gui_stats_x = 0
        # Chatlog
        self.chatlog = ChatLog(self.gui_font)
        self.chatlog.surface_col = self.gui_color

        self.chatting = False
        self.chat_input = ""

        self.game_surface = pygame.Surface((1,1))
        self.entity_surface = pygame.Surface((1,1))
        self.entity_surface.set_colorkey((255, 0, 255))

        self.player = None
        self.map = GameMap()

        self.camera_pos = Vector2(0, 0)

        self.keys_held = []

        self.playerlist = {}

        self.acc_name = ""
        self.acc_pw = ""

        self.ping_ticker = 300  # Ping (keeps connection alive)
        self.ping_timeout = 0
        self.anim_ticker = 30  # Tile animations

        # Map drawing layers
        self.updatelayers = False
        self.vis_tiles = pygame.sprite.LayeredDirty()
        self.spritelist = pygame.sprite.LayeredDirty()

        # Used for "press enter to continue". 1 when waiting for press, 2 when about to return to menu
        self.return_mode = 0

    def reset(self):
        Screen.reset(self)
        self.return_mode = 0
        self.chat_input = ""
        self.chatting = False
        self.chatlog.msg_log = []

    def setup(self, conn, display, player):
        Screen.setup(self, display)

        self.conn = conn

        self.player = player
        self.spritelist.empty()
        self.spritelist.add(self.player)
        self.spritelist.change_layer(self.player, 1)

        self.resize_screen(self.display.get_width(), self.display.get_height())

    def resize_screen(self, new_w, new_h):
        self.game_surface = pygame.transform.scale(self.game_surface, (new_w, new_h))
        self.entity_surface = pygame.transform.scale(self.entity_surface, (new_w, new_h))
        # Adjust GUI
        self.gui = GameGUI((new_w, new_h))
        # Adjust stats screen
        self.gui_stats_width = floor(new_w * 0.2)
        self.gui_stats_x = new_w - self.gui_stats_width
        # Adjust chatlog
        self.chatlog.set_line_width(floor(self.gui_stats_x / 9))
        self.chatlog.lines = max(4, ceil(floor(new_h * 0.15) / 16))
        self.chatlog.line_size = 16
        self.chatlog.surface_resize(self.gui_stats_x)

    def get_all_players(self):
        return [self.playerlist[pl] for pl in self.playerlist] + [self.player]

    def update_account_data(self, name, pw):
        self.acc_name = name
        self.acc_pw = pw

    def connect(self, host, port, mode=None):
        conn_success = False

        self.chat_log("Connecting to " + host + " using port " + str(port) + "...")
        try:
            self.conn.connect(host, port)
            conn_success = True
        except OSError as err:
            print(err)
            self.chat_log("Could not reach server.")

        if conn_success:
            try:
                if mode == "connect_newacc": # Connect to create new account
                    self.conn.send("acc_create|" + self.acc_name + "|" + base64.b64encode(self.acc_pw.encode('utf-8')).decode('utf-8'))

                    acc_creation = self.conn.receive(True)
                    self.chat_log("Connected. Creating account \"" + self.acc_name + "\"...")
                    if acc_creation == "acc_create_fail":
                        self.chat_log("Account creation failed. An account with that name already exists!")
                        conn_success = False
                    else:
                        self.chat_log("Account created successfully! You may now create characters with it.")
                        self.conn.send("disconnect")
                        self.conn.disconnect()
                        self.return_mode = 1

                elif mode == "connect_newchar" or mode == "connect_continuechar": # Connect with new character
                    self.conn.send("login|" + self.acc_name + "|" + base64.b64encode(self.acc_pw.encode('utf-8')).decode('utf-8'))

                    login_attempt = self.conn.receive(True)
                    self.chat_log("Connected. Authenticating...")
                    if login_attempt == "login_noacc" or login_attempt == "login_logged":
                        if login_attempt == "login_noacc":
                            self.chat_log("Authentication failed. Wrong credentials!")
                        else:
                            self.chat_log("Authentication failed. That account is already logged in!")
                        conn_success = False
                    else:
                        if mode == "connect_newchar":  # New character creation
                            self.conn.send("newchar|" + self.player.name + "|" + str(self.player.char))
                            char_creation = self.conn.receive(True)
                            if char_creation == "newchar_fail":
                                self.chat_log("Could not create new character. Name is already taken!")
                                conn_success = False
                            else:
                                self.chat_log("Created new character \"" + self.player.name + "\".")

                        else:  # Continue with existing character
                            self.conn.send("continuechar|" + self.player.name)
                            char_continue = self.conn.receive(True)
                            if char_continue == "continuechar_fail":
                                self.chat_log("Character not found!")
                                conn_success = False
                            else:
                                self.chat_log("Loaded character \"" + self.player.name + "\".")

                        if conn_success:
                            patcher = Patcher(self.conn)
                            self.chat_log("Running patcher...")
                            patcher.check_uptodate()
                            self.chat_log("Patching process done.")

                            self.conn.send("join")

            except ConnectionResetError:
                conn_success = False
                self.chat_log("Could not connect to server. Connection reset.")

        if not conn_success:
            self.return_mode = 1

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
        self.game_surface.fill((0,0,0))
        self.vis_tiles.empty()
        # Visibility range in X axis
        vis_x_min = max(0, floor(-self.camera_pos.x / 32))
        vis_x_max = max(0, ceil((self.display.get_width() - self.camera_pos.x) / 32))
        # Visibility range in Y axis
        vis_y_min = max(0, floor(-self.camera_pos.y / 32))
        vis_y_max = max(0, ceil((self.display.get_height() - self.camera_pos.y) / 32))
        # Visibility rectangle
        vis_rect = (vis_x_min, vis_x_max, vis_y_min, vis_y_max)

        # Update field of view
        self.map.cast_fov(self.player.x, self.player.y, self.player.sightrange, True, vis_rect)
        # Update illumination
        self.map.lighting_update(self.get_all_players(), vis_rect)

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
                        tmp_maptile.set_lightlevel(self.map.default_light)
                    else:
                        tmp_maptile.toggle_grayscale(False)

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
                    self.vis_tiles.change_layer(light_overlay, 5)

                except IndexError:
                    pass

    # Draws players over visible tiles
    def update_drawplayers(self):
        for pl_id, pl_obj in self.playerlist.items():
            try:
                if self.map.map_data[int(pl_obj.y)][int(pl_obj.x)].light_visible:
                    # Update illumination with player light
                    if pl_obj.moved:
                        self.map.lighting_update(self.get_all_players())
                        pl_obj.moved = False

                    pl_obj.update()
                    if not self.vis_tiles.has(pl_obj):
                        self.vis_tiles.add(pl_obj)
                        self.vis_tiles.change_layer(pl_obj, 4)
                elif self.vis_tiles.has(pl_obj):
                    self.remove_player_sprite(pl_obj)
            except IndexError:
                pass

    def remove_player_sprite(self, player):
        if self.vis_tiles.has(player):
            self.vis_tiles.remove(player)

            tmp_plist = self.get_all_players()
            if player in tmp_plist:
                tmp_plist.remove(player)
            self.map.lighting_update(tmp_plist)

    # GUI Interface
    def update_drawGUI(self, stats=True):
        self.gui.fill((0, 0, 0))

        if not self.gui.get_alpha() == self.gui_alpha:
            self.gui.set_alpha(self.gui_alpha)

        # Right-hand player stats area
        pygame.draw.rect(self.gui, self.gui_color,
                         (self.gui_stats_x, 0, self.gui_stats_width, self.display.get_height()))
        if stats:
            area_stats_text = []
            # Health
            area_stats_text.append(
                [self.gui_stats_x + 4, 0, "Health: " + str(self.player.hp) + " / " + str(self.player.maxhp)])
            area_stats_text.append("\n")
            self.gui.draw_healthbar(self.player.hp, self.player.maxhp, self.gui_stats_x + 4, 14,
                                    self.gui_stats_width - 8, 6, (50, 220, 50), (10, 10, 10))
            # Exp / Level
            area_stats_text.append([self.gui_stats_x + 4, 0, "Level: " + str(self.player.level)])
            area_stats_text.append(
                [self.gui_stats_x + 4, 0, "Exp: " + str(self.player.xp) + " / " + str(self.player.xp_req)])
            area_stats_text.append("\n")
            self.gui.draw_healthbar(self.player.xp, self.player.xp_req, self.gui_stats_x + 4, 62,
                                    self.gui_stats_width - 8, 6, (102, 0, 255), (10, 10, 10))

            # Attack / attack speed
            area_stats_text.append([self.gui_stats_x + 4, 8, "Atk: " + str(self.player.atk)])
            area_stats_text.append([self.gui_stats_x + 4, 8, "Atk spd: " + str(self.player.atkspd)])
            area_stats_text.append("\n")

            for i, txt in enumerate(area_stats_text):
                if txt == "\n":
                    continue
                self.gui.draw_text((txt[0], 4 + 16 * i + txt[1]), self.gui_font_small, txt[2], halign=0, valign=1)
        
        self.update_drawchatlog()

    def update_drawchatlog(self):
        chat_y = self.display.get_height() - self.chatlog.surface.get_height()
        self.chatlog.draw_chat()
        self.gui.blit(self.chatlog.surface, (0, chat_y))

        self.display.blit(self.gui, (0, 0))

    def chat_toggle(self, mode):
        if mode:
            self.chatting = True
            self.chatlog.inputting = True
        else:
            self.chatting = False
            self.chatlog.inputting = False
            self.chat_input = ""

    def chat_log(self, msg, color=(255,255,255)):
        self.chatlog.log_msg(msg, color)
        self.update_drawchatlog()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.chatting:
                if self.keys_held[pygame.K_LSHIFT]:  # Shift + key
                    if event.key == pygame.K_q:
                        self.return_mode = 2
                else:
                    if event.key == pygame.K_SPACE:
                        newlevel_data = self.map.transfer_level(self.player.x, self.player.y)
                        if newlevel_data:
                            self.conn.send("xfer_map|" + newlevel_data[1])
                            self.load_map(newlevel_data[1])
                            self.player.set_pos(int(newlevel_data[2]), int(newlevel_data[3]))
                            self.update_camera_plpos()

                    elif event.key == pygame.K_RETURN:
                        if self.return_mode == 0:
                            self.chat_toggle(True)
                        else:
                            self.return_mode = 2
            else:
                # Player chat
                if event.key == pygame.K_RETURN:  # Enter - send message
                    tmp_chat = self.chat_input.strip()
                    if tmp_chat:
                        self.conn.send("pl_chat|" + tmp_chat)
                    self.chat_toggle(False)

                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.chat_toggle(False)
                else:
                    self.chat_input += event.unicode

                self.chatlog.msg_input = self.chat_input

        return Screen.handle_event(self, event)

    def loop(self):
        if not self.chatting:
            self.keys_held = pygame.key.get_pressed()

        for event in pygame.event.get():
            if not self.handle_event(event):
                return False

        if self.return_mode == 1:
            self.update_drawchatlog()  # Only update chat
            return True
        elif self.return_mode == 2:
            if self.conn.is_connected():
                self.conn.send("disconnect")
                self.conn.disconnect()
            return "menu_main"

        if not self.conn.is_connected():
            self.chat_log("Could not connect to server.")
            self.return_mode = 1
            return True

        self.server_listener()

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

        self.update_drawplayers()
        self.vis_tiles.draw(self.game_surface)

        if self.map.loaded:
            # Draw game surface (tiles)
            self.display.blit(self.game_surface, self.camera_pos)
            # Draw sprites
            self.spritelist.update()
            self.spritelist.draw(self.entity_surface)
            self.display.blit(self.entity_surface, self.camera_pos)
        # Draw GUI
        self.update_drawGUI(self.map.loaded)

        # Keep connection alive
        if self.ping_ticker > 0:
            self.ping_ticker -= 1
        else:
            self.ping_timeout += 1
            if self.ping_timeout >= 2:
                self.chat_log("Lost connection to server.")
                self.ping_timeout = 0
                self.return_mode = 1
                return True
            else:
                self.conn.send("ping")

            self.ping_ticker = 300

        return Screen.loop(self)

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
            if server_data[0] == "loadmap": # Map loading / set player pos
                self.load_map(server_data[1])
                if server_data[2] == "spawn":
                    self.player.set_pos(self.map.spawnpos[0], self.map.spawnpos[1])
                else:
                    pl_pos = server_data[2].split('/')
                    self.player.set_pos(int(pl_pos[0]), int(pl_pos[1]))
                self.conn.send("pl_move|" + str(self.player.x) + "|" + str(self.player.y))

            elif server_data[0] == "new_pl": # Create new player
                newplayer = Player(int(server_data[1]), self.map.spawnpos, int(server_data[2]))
                self.playerlist[int(server_data[1])] = newplayer

            elif server_data[0] == "remove_pl": # Remove player
                try:
                    tmp_player = self.playerlist[int(server_data[1])]
                except NameError:
                    pass
                else:
                    self.playerlist.pop(int(server_data[1]), None)
                    self.remove_player_sprite(tmp_player)

            elif server_data[0] == "update_pl": # Update player position
                try: self.playerlist[int(server_data[1])].set_pos(int(server_data[2]), int(server_data[3]))
                except KeyError: pass

            elif server_data[0] == "pl_chat": # Player chats
                plname = server_data[1]
                if server_data[2] == "local":
                    self.chat_log(plname + ": " + server_data[3], (255,255,102))
                elif server_data[2] == "global":
                    self.chat_log(plname + " [global]: " + server_data[3], (255,102,0))
                elif server_data[2] == "whisper":
                    self.chat_log(plname + " [whisper]: " + server_data[3], (153,102,255))

            elif server_data[0] == "msg": # Basic message from server
                self.chat_log(server_data[1])

            elif server_data[0] == "setstat_pl": # Update player stat
                pl_id = int(server_data[1])
                values = server_data[2:]
                for val in values:
                    val = val.split('/')
                    try: val[1] = int(val[1])
                    except ValueError:
                        try: val[1] = float(val[1])
                        except ValueError: pass

                    if pl_id == -1:
                        self.player.set_stat(val[0], val[1])
                    else:
                        try: self.playerlist[pl_id].set_stat(val[0], val[1])
                        except KeyError: pass

            elif server_data[0] == "pong": # Keeps connection alive
                self.ping_timeout = 0