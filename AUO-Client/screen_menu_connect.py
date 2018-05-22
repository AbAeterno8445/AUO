from class_screen import *
from random import randint
import pygame

class Screen_Menu_Connect(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.font = pygame.font.Font("assets/fonts/monobit.ttf", 32)
        self.fontcol_normal = pygame.Color(230,230,230)
        self.fontcol_sel = pygame.Color(50,200,200)
        self.fontcol_input = pygame.Color(50,50,200)

        self.menu_buttons = []
        self.menu_selected = 0

        self.inputting = False

        self.connect_mode = False

        self.backg_rect = (0,0,0,0)

        self.acc_name = ""
        self.acc_pw = ""

        # Input fields
        self.server_ip = ""
        self.server_port = "6000"

    def reset(self):
        self.menu_selected = 0
        self.newscreen = ""
        self.update_backg_size()

    def update_account_data(self, name, pw):
        self.acc_name = name
        self.acc_pw = pw
    def get_account_data(self):
        return [self.acc_name, self.acc_pw]
    def get_server_data(self):
        return [self.server_ip, int(self.server_port), self.connect_mode]

    def setup(self, display):
        Screen.setup(self, display)

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Connect to server buttons
        # Server IP
        tmp_button = Menu_Button("input server_ip", "Server IP: ", True)
        tmp_button.input_text = self.server_ip
        tmp_button.set_pos(disp_centerx, disp_centery - 36)
        self.menu_buttons.append(tmp_button)

        # Server port
        tmp_button = Menu_Button("input server_port", "Port: ", True)
        tmp_button.input_text = self.server_port
        tmp_button.input_number = True
        tmp_button.set_pos(disp_centerx, disp_centery)
        self.menu_buttons.append(tmp_button)

        # Connect
        tmp_button = Menu_Button("game", "Connect", True)
        tmp_button.set_pos(disp_centerx, disp_centery + 36)
        self.menu_buttons.append(tmp_button)

        # Return
        tmp_button = Menu_Button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 85)
        self.menu_buttons.append(tmp_button)
        # endregion

        self.update_backg_size()

    def button_press(self, action):
        if action[:5] == "input":
            self.inputting = not self.inputting
            if not self.inputting:
                setattr(self, action[6:], self.menu_buttons[self.menu_selected].input_text)

        else:
            self.newscreen = action

    # Update buttons' background rectangle size
    def update_backg_size(self):
        # Width is based on longest text string in current menu's buttons
        tmp_width = 0
        # Height is measured between first and last buttons' Y coordinates
        tmp_height_min, tmp_height_max = None, None

        for button in self.menu_buttons:
            # Width
            tmp_len = len(button.text + button.input_text)
            if tmp_len > tmp_width:
                tmp_width = len(button.text + button.input_text)
            # Height
            button_y = button.y + 4
            if tmp_height_min is None:
                tmp_height_min = button_y
                tmp_height_max = button_y

            if button_y < tmp_height_min:
                tmp_height_min = button_y
            elif button_y > tmp_height_max:
                tmp_height_max = button_y

        backg_width = tmp_width * 12
        backg_height = tmp_height_max - tmp_height_min + 48
        backg_x = self.display.get_width() / 2 - backg_width / 2
        backg_y = tmp_height_min - 24
        self.backg_rect = (backg_x, backg_y, backg_width, backg_height)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.inputting:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.menu_selected -= 1
                    if self.menu_selected < 0:
                        self.menu_selected = len(self.menu_buttons) - 1

                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.menu_selected += 1
                    if self.menu_selected > len(self.menu_buttons) - 1:
                        self.menu_selected = 0

            else:
                # Currently selected button
                sel_button = self.menu_buttons[self.menu_selected]

                if not event.key == pygame.K_RETURN:
                    if event.key == pygame.K_BACKSPACE:
                        sel_button.input_text = sel_button.input_text[:-1]
                        self.update_backg_size()

                    elif event.key == pygame.K_ESCAPE:
                        self.inputting = False

                    elif len(sel_button.input_text) < sel_button.input_maxlen:
                        if not sel_button.input_number:
                            sel_button.input_text += event.unicode
                        else:
                            try: sel_button.input_text += str(int(event.unicode))
                            except ValueError: pass

                        self.update_backg_size()

            if event.key == pygame.K_RETURN:
                self.button_press(self.menu_buttons[self.menu_selected].action)

        return Screen.handle_event(self, event)

    def loop(self):
        for event in pygame.event.get():
            if not self.handle_event(event):
                return False

        pygame.draw.rect(self.display, (0,0,0), self.backg_rect)
        pygame.draw.rect(self.display, (255,255,255), self.backg_rect, 2)
        for i, button in enumerate(self.menu_buttons):
            tmp_color = self.fontcol_normal
            if i == self.menu_selected:
                if self.inputting and button.input:
                    tmp_color = self.fontcol_input
                else:
                    tmp_color = self.fontcol_sel

            button.render(self.font, self.display, tmp_color)

        if self.newscreen:
            return self.newscreen
        return True