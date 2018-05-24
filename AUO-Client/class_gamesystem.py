from class_entity import *

from screen_menu_main import ScreenMenuMain
from screen_menu_continuechar import ScreenMenuContinuechar
from screen_menu_newchar import ScreenMenuNewchar
from screen_menu_newacc import ScreenMenuNewacc
from screen_menu_connect import ScreenMenuConnect
from screen_game import ScreenGame

from types import MethodType
from Mastermind import *
import pygame

class GameSystem(object):
    def __init__(self):
        self.conn = MastermindClientUDP(10.0, 10.0)
        self.conn_ip = ""
        self.conn_port = ""
        self.player = Entity(-1, (1,1), 256)

        self.title_font = pygame.font.Font("assets/fonts/Dimitriswank.TTF", 96)
        self.title_col = [255, 255, 255]
        self.title_mode = randint(0, 2)

        self.screens = {
            "menu_main": ScreenMenuMain(),
            "menu_continuechar": ScreenMenuContinuechar(),
            "menu_newchar": ScreenMenuNewchar(),
            "menu_newacc": ScreenMenuNewacc(),
            "menu_connect": ScreenMenuConnect(),
            "game": ScreenGame()
        }
        self.screen_transitions = Screen_Transitions()
        self.current_screen = "menu_main"

        self.display = None
        self.clock = pygame.time.Clock()

    def init_display(self, disp_w, disp_h):
        self.display = pygame.display.set_mode((disp_w, disp_h))
        pygame.display.set_icon(pygame.image.load("assets/AUOicon.png"))
        pygame.display.set_caption("AUO Client")

    def save_screen_options(self):
        with open("data/options", "w") as opt_file:
            opt_file.write("menu_continuechar:char_name:" + self.player.name + "\n")
            opt_file.write("menu_continuechar:acc_name:" + self.screens["menu_continuechar"].acc_name + "\n")

            opt_file.write("menu_newchar:acc_name:" + self.screens["menu_newchar"].acc_name + "\n")

            opt_file.write("menu_connect:server_ip:" + self.screens["menu_connect"].server_ip + "\n")

    def load_screen_options(self):
        with open("data/options", "r") as opt_file:
            for line in opt_file:
                line = line.strip().split(':')
                if len(line) == 3:
                    setattr(self.screens[line[0]], line[1], line[2])

    def title_loop(self):
        for i in range(3):
            if self.title_mode == i:
                if self.title_col[i] == 0:
                    self.title_mode = randint(0,2)
                else:
                    self.title_col[i] -= 1
            else:
                if self.title_col[i] < 255:
                    self.title_col[i] += 1

    def main_loop(self):
        done = False

        self.load_screen_options()

        # Initialize screens
        self.screens["menu_main"].setup(self.display)
        self.screens["menu_continuechar"].setup(self.display, self.player)
        self.screens["menu_newchar"].setup(self.display, self.player)
        self.screens["menu_newacc"].setup(self.display)
        self.screens["menu_connect"].setup(self.display)
        self.screens["game"].setup(self.conn, self.display, self.player)

        # Screen transitions
        # Continue char -> Connect, set connection mode to continue character (lets server know we will load a character)
        scr_fro = self.screens["menu_continuechar"]
        scr_to = self.screens["menu_connect"]
        self.screen_transitions.add_interaction(scr_fro, scr_to, "set", "connect_mode", "connect_continuechar")
        self.screen_transitions.add_interaction(scr_fro, scr_to, "call", "update_account_data", scr_fro.get_account_data)

        # New char -> Connect, set connection mode to new character (lets server know we will create a new character)
        scr_fro = self.screens["menu_newchar"]
        self.screen_transitions.add_interaction(scr_fro, scr_to, "set", "connect_mode", "connect_newchar")
        self.screen_transitions.add_interaction(scr_fro, scr_to, "call", "update_account_data", scr_fro.get_account_data)

        # New account -> Connect, set connection mode to new account (lets server know we will create a new account)
        scr_fro = self.screens["menu_newacc"]
        self.screen_transitions.add_interaction(scr_fro, scr_to, "set", "connect_mode", "connect_newacc")
        self.screen_transitions.add_interaction(scr_fro, scr_to, "call", "update_account_data", scr_fro.get_account_data)

        # Connect -> Game, connect to server
        scr_fro = self.screens["menu_connect"]
        scr_to = self.screens["game"]
        self.screen_transitions.add_interaction(scr_fro, scr_to, "call", "update_account_data", scr_fro.get_account_data)
        self.screen_transitions.add_interaction(scr_fro, scr_to, "call", "connect", scr_fro.get_server_data)

        # Menu background
        menu_background = pygame.image.load("assets/titlebg.png").convert_alpha()
        menu_background = pygame.transform.scale(menu_background, self.display.get_size())

        while not done:
            self.display.fill((0, 0, 0))

            # Title and background for menus
            if not self.current_screen == "game":
                self.display.blit(menu_background, (0,0))

                self.title_loop()
                tmp_title = self.title_font.render("A U O", True, self.title_col)
                tmp_title_rect = tmp_title.get_rect(center=(self.display.get_width() / 2, 128))
                self.display.blit(tmp_title, tmp_title_rect)

            # Process screen loop. If it returns false, end the application. If it returns a string, change to screen with that string as name
            newscreen = self.screens[self.current_screen].loop()
            pygame.display.update()
            self.clock.tick(60)

            if not newscreen:
                done = True
            elif type(newscreen) is str:
                self.screen_transitions.transfer(self.screens[self.current_screen], self.screens[newscreen])
                self.current_screen = newscreen
                self.screens[self.current_screen].reset()

        if self.conn.is_connected():
            self.conn.send("disconnect")
            self.conn.disconnect()

        self.save_screen_options()

""" Screen Transitions Usage:
    Used for interactions between different screens (data sharing)
        -add_interaction: 
            from_scr/to_scr: relevant screen objects
            action: can be "call", if calling a target method, or "set" if setting a target attribute
            target: target method/attribute, relative to action parameter
            value: list of method arguments/variable to set, relative to action parameter
            If value is a method, it must return a list of variables to be used as arguments for the target method
"""
class Screen_Transitions(object):
    def __init__(self):
        self.interactions = {}

    def add_interaction(self, from_scr, to_scr, action, target, value=None):
        if from_scr not in self.interactions:
            self.interactions[from_scr] = {to_scr: []}
        self.interactions[from_scr][to_scr].append([action, target, value])

    def transfer(self, from_scr, to_scr):
        if from_scr in self.interactions:
            if to_scr in self.interactions[from_scr]:
                for inter in self.interactions[from_scr][to_scr]:
                    if inter[0] == "call":
                        tgt_method = getattr(to_scr, inter[1], inter[2])
                        if not inter[2]:
                            tgt_method()
                        elif type(inter[2]) is MethodType:
                            tgt_method(*inter[2]())
                        else:
                            tgt_method(*inter[2])
                    elif inter[0] == "set":
                        setattr(to_scr, inter[1], inter[2])