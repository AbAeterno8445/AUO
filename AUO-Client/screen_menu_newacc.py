from class_screen_menu import ScreenMenu

class ScreenMenuNewacc(ScreenMenu):
    def __init__(self):
        ScreenMenu.__init__(self)

        # Input fields
        self.acc_name = ""
        self.acc_pw = ""

    def get_account_data(self):
        return [self.acc_name, self.acc_pw]

    def setup(self, display):
        ScreenMenu.setup(self, display)

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Create new account buttons
        # Account name
        tmp_button = self.create_button("acc_name", "Account name: ", True)
        tmp_button.set_pos(disp_centerx, disp_centery - 36)

        # Account password
        tmp_button = self.create_button("acc_pw", "Account password: ", True)
        tmp_button.input_hidden = True
        tmp_button.set_pos(disp_centerx, disp_centery)

        # Create
        tmp_button = self.create_button("menu_connect", "Create")
        tmp_button.set_pos(disp_centerx, disp_centery + 36)

        # Return
        tmp_button = self.create_button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 85)
        # endregion

        self.update_backg_size()