from class_screen import *
from random import randint
import pygame

class Screen_Menu_Main(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.font = pygame.font.Font("assets/fonts/monobit.ttf", 32)
        self.fontcol_normal = pygame.Color(230,230,230)
        self.fontcol_sel = pygame.Color(50,200,200)

        self.menu_buttons = []
        self.menu_selected = 0

        self.backg_rect = (0,0,0,0)

        self.quit = False

    def reset(self):
        self.menu_selected = 0
        self.newscreen = ""
        self.update_backg_size()

    def setup(self, display):
        Screen.setup(self, display)

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        #region Main menu buttons
        # Continue with character
        tmp_button = Menu_Button("menu_continuechar", "Continue with character")
        tmp_button.set_pos(disp_centerx, disp_centery - 36)
        self.menu_buttons.append(tmp_button)

        # Create new character
        tmp_button = Menu_Button("menu_newchar", "Create new character")
        tmp_button.set_pos(disp_centerx, disp_centery)
        self.menu_buttons.append(tmp_button)

        # Create new account
        tmp_button = Menu_Button("menu_newacc", "Create new account")
        tmp_button.set_pos(disp_centerx, disp_centery + 36)
        self.menu_buttons.append(tmp_button)

        # Quit
        tmp_button = Menu_Button("quit", "Quit")
        tmp_button.set_pos(disp_centerx, disp_centery + 72)
        self.menu_buttons.append(tmp_button)
        #endregion

        self.update_backg_size()

    def button_press(self, action):
        if action == "quit":
            self.quit = True
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
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.menu_selected -= 1
                if self.menu_selected < 0:
                    self.menu_selected = len(self.menu_buttons) - 1

            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.menu_selected += 1
                if self.menu_selected > len(self.menu_buttons) - 1:
                    self.menu_selected = 0

            elif event.key == pygame.K_RETURN:
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
                tmp_color = self.fontcol_sel

            button.render(self.font, self.display, tmp_color)

        if self.newscreen:
            return self.newscreen
        elif self.quit:
            return False
        return True