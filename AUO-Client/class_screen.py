import pygame
from random import randint

class Screen(object):
    def __init__(self):
        self.display = None
        self.newscreen = ""
        
    def setup(self, display):
        self.display = display

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        return True

    def reset(self):
        self.newscreen = ""
        pass

    def loop(self):
        if self.newscreen:
            return self.newscreen

        return True

class Menu_Button(object):
    def __init__(self, action, text, input=False):
        self.action = action
        self.text = text

        self.input = input
        self.input_hidden = False
        self.input_number = False
        self.input_maxlen = 20
        self.input_text = ""

    def set_pos(self, x, y):
        self.x, self.y = x, y

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