from class_screen_menu import ScreenMenu
import pygame

class ScreenMenuNewchar(ScreenMenu):
    def __init__(self):
        ScreenMenu.__init__(self)

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

    def get_account_data(self):
        return [self.acc_name, self.acc_pw]

    def reset(self):
        ScreenMenu.reset(self)
        self.player.set_char(self.available_avs[0])

    def setup(self, display, player):
        ScreenMenu.setup(self, display)
        self.player = player

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Create new character buttons
        # Character name
        tmp_button = self.create_button("char_name", "Character name: ", True)
        tmp_button.connect_input(self.player, "name")
        tmp_button.set_pos(disp_centerx, disp_centery - 36)

        # Character avatar
        tmp_button = self.create_button("", "Avatar:")
        tmp_button.set_pos(disp_centerx, disp_centery)

        # Account name
        tmp_button = self.create_button("acc_name", "Account name: ", True)
        tmp_button.input_text = self.acc_name
        tmp_button.set_pos(disp_centerx, disp_centery + 72)

        # Account password
        tmp_button = self.create_button("acc_pw", "Account password: ", True)
        tmp_button.input_hidden = True
        tmp_button.set_pos(disp_centerx, disp_centery + 108)

        # Create
        tmp_button = self.create_button("menu_connect", "Create and join")
        tmp_button.set_pos(disp_centerx, disp_centery + 144)

        # Return
        tmp_button = self.create_button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 195)
        # endregion

        self.update_backg_size()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.inputting:
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

        return ScreenMenu.handle_event(self, event)

    def loop(self, framerate):
        orig_loop = ScreenMenu.loop(self, framerate)

        display_centerx = self.display.get_width() / 2
        display_centery = self.display.get_height() / 2

        # Player avatar
        self.player.update()
        self.display.blit(self.player.image, self.player.image.get_rect(center=(display_centerx, display_centery + 32)))

        return orig_loop