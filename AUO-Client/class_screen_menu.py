from class_screen import Screen
import pygame

class ScreenMenu(Screen):
    def __init__(self):
        Screen.__init__(self)

        self.font = pygame.font.Font("assets/fonts/monobit.ttf", 32)
        self.fontcol_normal = pygame.Color(230,230,230)
        self.fontcol_sel = pygame.Color(50,200,200)
        self.fontcol_input = pygame.Color(50,50,200)

        self.menu_buttons = []
        self.menu_selected = 0

        self.inputting = False

        self.backg_rect = (0, 0, 0, 0)

    def reset(self):
        Screen.reset(self)
        self.inputting = False
        self.menu_selected = 0

    # Creates a menu button - action is name of screen to switch to if not input, or attribute name to set if input
    def create_button(self, action, text, is_input=False):
        tmp_button = MenuButton(action, text, is_input)
        tmp_button.connect_input(self, action)
        self.menu_buttons.append(tmp_button)
        return tmp_button

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
                self.button_press()

        return Screen.handle_event(self, event)

    def button_press(self):
        pressed_button = self.menu_buttons[self.menu_selected]
        if pressed_button.input:
            self.inputting = not self.inputting
            if not self.inputting:
                pressed_button.input_done()

        else:
            self.newscreen = pressed_button.action

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

    def loop(self):
        for event in pygame.event.get():
            if not self.handle_event(event):
                return False

        pygame.draw.rect(self.display, (0, 0, 0), self.backg_rect)
        pygame.draw.rect(self.display, (255, 255, 255), self.backg_rect, 2)
        for i, button in enumerate(self.menu_buttons):
            tmp_color = self.fontcol_normal
            if i == self.menu_selected:
                if self.inputting and button.input:
                    tmp_color = self.fontcol_input
                else:
                    tmp_color = self.fontcol_sel

            button.render(self.font, self.display, tmp_color)

        return Screen.loop(self)

class MenuButton(object):
    def __init__(self, action, text, input=False):
        self.action = action
        self.text = text

        self.input = input
        self.input_hidden = False  # Converts input text to asterisks (for passwords)
        self.input_number = False  # Accepts only numbers for input
        self.input_maxlen = 20
        self.input_text = ""

        # Input attribute connection - sets a target object's attribute to this button's input text
        self.input_target = None  # Target object to change
        self.input_target_val = None # Name of attribute to change

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def connect_input(self, target, value):
        self.input_target = target
        self.input_target_val = value

    def input_done(self):
        setattr(self.input_target, self.input_target_val, self.input_text)

    def render(self, font, tgt_surface, color):
        inp = self.input_text
        if self.input_hidden: # Hide input for passwords
            tmp_txt_len = len(inp)
            inp = ""
            for i in range(tmp_txt_len):
                inp += "*"

        tmp_text = font.render(self.text + inp, False, color)
        text_rect = tmp_text.get_rect(center=(self.x, self.y))
        tgt_surface.blit(tmp_text, text_rect)