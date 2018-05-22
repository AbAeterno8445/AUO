from class_screen import *
from random import randint
import pygame

class Screen_Menu_Newchar(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.font = pygame.font.Font("assets/fonts/monobit.ttf", 32)
        self.fontcol_normal = pygame.Color(230,230,230)
        self.fontcol_sel = pygame.Color(50,200,200)
        self.fontcol_input = pygame.Color(50,50,200)

        self.title_font = pygame.font.Font("assets/fonts/Dimitriswank.TTF", 96)
        self.title_col = [255,255,255]
        self.title_mode = randint(0,2)

        self.menu_buttons = []
        self.menu_selected = 0

        self.inputting = False

        self.backg_rect = (0,0,0,0)

        # Input fields
        self.acc_name = ""
        self.acc_pw = ""
        self.char_name = ""

        # Available character avatars [texture id, character id]
        # Character id as list represents a range of available avatars [id from, id to]
        tmp_available_avs = [
            [1, [0, 9]],
            [1, [12, 13]],
            [1, [15, 18]],
            [1, 24],
            [1, 28],
            [1, [31, 32]]
        ]

        self.available_avs = []
        for av_list in tmp_available_avs:
            if type(av_list[1]) is list:
                for j in range(av_list[1][0], av_list[1][1]):
                    self.available_avs.append(256 * av_list[0] + j * 4)
            else:
                self.available_avs.append(256 * av_list[0] + av_list[1] * 4)

    def reset(self):
        self.menu_selected = 0
        self.newscreen = ""
        self.update_backg_size()

    def get_account_data(self):
        return [self.acc_name, self.acc_pw]

    def setup(self, display, player):
        Screen.setup(self, display)
        self.player = player

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Create new character buttons
        # Character name
        tmp_button = Menu_Button("input char_name", "Character name: ", True)
        tmp_button.set_pos(disp_centerx, disp_centery - 36)
        self.menu_buttons.append(tmp_button)

        # Character avatar
        tmp_button = Menu_Button("", "Avatar:")
        tmp_button.set_pos(disp_centerx, disp_centery)
        self.menu_buttons.append(tmp_button)

        # Account name
        tmp_button = Menu_Button("input acc_name", "Account name: ", True)
        tmp_button.input_text = self.acc_name
        tmp_button.set_pos(disp_centerx, disp_centery + 72)
        self.menu_buttons.append(tmp_button)

        # Account password
        tmp_button = Menu_Button("input acc_pw", "Account password: ", True)
        tmp_button.input_hidden = True
        tmp_button.set_pos(disp_centerx, disp_centery + 108)
        self.menu_buttons.append(tmp_button)

        # Create
        tmp_button = Menu_Button("menu_connect", "Create and join")
        tmp_button.set_pos(disp_centerx, disp_centery + 144)
        self.menu_buttons.append(tmp_button)

        # Return
        tmp_button = Menu_Button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 195)
        self.menu_buttons.append(tmp_button)
        # endregion

        self.update_backg_size()

    def button_press(self, action):
        if action[:5] == "input":
            self.inputting = not self.inputting
            if not self.inputting:
                setattr(self, action[6:], self.menu_buttons[self.menu_selected].input_text)
                if action[6:] == "char_name": # Set player name
                    self.player.name = self.menu_buttons[self.menu_selected].input_text

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

                # Avatar creation, switch chosen avatar
                av_switch = 0
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    av_switch = -1
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    av_switch = 1

                if not av_switch == 0:
                    new_av = self.player.char + av_switch
                    highest_av = max(self.available_avs)
                    while True:
                        if new_av in self.available_avs:
                            self.player.set_char(new_av)
                            break

                        new_av += av_switch
                        if new_av < 0:
                            self.player.set_char(highest_av)
                            break
                        elif new_av > highest_av:
                            new_av = 0

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

        display_centerx = self.display.get_width() / 2
        display_centery = self.display.get_height() / 2

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

        # Player avatar
        self.player.update()
        self.display.blit(self.player.image, self.player.image.get_rect(center=(display_centerx, display_centery + 32)))

        if self.newscreen:
            return self.newscreen
        return True