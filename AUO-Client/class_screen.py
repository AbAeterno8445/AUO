import pygame

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

    def loop(self, framerate=60):
        if self.newscreen:
            return self.newscreen

        return True