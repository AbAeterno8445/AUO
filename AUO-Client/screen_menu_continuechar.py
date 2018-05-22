from class_screen_menu import ScreenMenu

class ScreenMenuContinuechar(ScreenMenu):
    def __init__(self):
        ScreenMenu.__init__(self)

        # Input fields
        self.acc_name = ""
        self.acc_pw = ""
        self.char_name = ""

    def get_account_data(self):
        return [self.acc_name, self.acc_pw]

    def reset(self):
        ScreenMenu.reset(self)
        self.player.name = self.char_name

    def setup(self, display, player):
        ScreenMenu.setup(self, display)
        self.player = player

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Continue with character buttons
        # Character name
        tmp_button = self.create_button("char_name", "Character name: ", True)
        tmp_button.connect_input(self.player, "name")
        tmp_button.input_text = self.char_name
        tmp_button.set_pos(disp_centerx, disp_centery - 36)

        # Account name
        tmp_button = self.create_button("acc_name", "Account name: ", True)
        tmp_button.input_text = self.acc_name
        tmp_button.set_pos(disp_centerx, disp_centery)

        # Account password
        tmp_button = self.create_button("acc_pw", "Account password: ", True)
        tmp_button.input_text = self.acc_pw
        tmp_button.input_hidden = True
        tmp_button.set_pos(disp_centerx, disp_centery + 36)

        # Join game
        tmp_button = self.create_button("menu_connect", "Join Game")
        tmp_button.set_pos(disp_centerx, disp_centery + 72)

        # Return
        tmp_button = self.create_button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 130)
        # endregion

        self.update_backg_size()