from class_screen_menu import ScreenMenu

class ScreenMenuMain(ScreenMenu):
    def __init__(self):
        ScreenMenu.__init__(self)

        self.quit = False

    def setup(self, display):
        ScreenMenu.setup(self, display)

        disp_centerx = self.display.get_width() / 2
        disp_centery = self.display.get_height() / 2

        #region Main menu buttons
        # Continue with character
        tmp_button = self.create_button("menu_continuechar", "Continue with character")
        tmp_button.set_pos(disp_centerx, disp_centery - 36)

        # Create new character
        tmp_button = self.create_button("menu_newchar", "Create new character")
        tmp_button.set_pos(disp_centerx, disp_centery)

        # Create new account
        tmp_button = self.create_button("menu_newacc", "Create new account")
        tmp_button.set_pos(disp_centerx, disp_centery + 36)

        # Quit
        tmp_button = self.create_button("quit", "Quit")
        tmp_button.set_pos(disp_centerx, disp_centery + 72)
        #endregion

        self.update_backg_size()

    def button_press(self):
        pressed_button = self.menu_buttons[self.menu_selected]
        if pressed_button.action == "quit":
            self.quit = True
        else:
            ScreenMenu.button_press(self)

    def loop(self, framerate):
        if self.quit:
            return False

        return ScreenMenu.loop(self, framerate)