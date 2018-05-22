from class_screen_menu import ScreenMenu

class ScreenMenuConnect(ScreenMenu):
    def __init__(self):
        ScreenMenu.__init__(self)

        self.connect_mode = ""

        self.acc_name = ""
        self.acc_pw = ""

        # Input fields
        self.server_ip = ""
        self.server_port = "6000"

    def update_account_data(self, name, pw):
        self.acc_name = name
        self.acc_pw = pw

    def get_account_data(self):
        return [self.acc_name, self.acc_pw]

    def get_server_data(self):
        return [self.server_ip, int(self.server_port), self.connect_mode]

    def setup(self, display):
        ScreenMenu.setup(self, display)

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        # region Connect to server buttons
        # Server IP
        tmp_button = self.create_button("server_ip", "Server IP: ", True)
        tmp_button.input_text = self.server_ip
        tmp_button.set_pos(disp_centerx, disp_centery - 36)

        # Server port
        tmp_button = self.create_button("server_port", "Port: ", True)
        tmp_button.input_text = self.server_port
        tmp_button.input_number = True
        tmp_button.set_pos(disp_centerx, disp_centery)

        # Connect
        tmp_button = self.create_button("game", "Connect")
        tmp_button.set_pos(disp_centerx, disp_centery + 36)

        # Return
        tmp_button = self.create_button("menu_main", "Return to main menu")
        tmp_button.set_pos(disp_centerx, disp_centery + 85)
        # endregion

        self.update_backg_size()