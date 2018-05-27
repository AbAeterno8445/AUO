import pygame

class GameGUI(pygame.Surface):
    def __init__(self, *args, **kwargs):
        pygame.Surface.__init__(self, *args, **kwargs)
        self.set_colorkey((0,0,0))

    # Draw healthbar (value, max value, x pos, y pos, width, height, front color, backg color, is outlined, outline color)
    def draw_healthbar(self, val, val_max, x, y, w, h, col, col_back, outl=False, col_outl=(255,255,255)):
        if not val_max == 0:
            fill_perc = max(0, min(1, val / val_max))
        else:
            fill_perc = 0
        # Background rect
        pygame.draw.rect(self, col_back, (x, y, w, h))
        # Front rect
        if not val == 0:
            pygame.draw.rect(self, col, (x, y, w * fill_perc, h))
        # Outline
        if outl:
            pygame.draw.rect(self, col_outl, (x, y, w, h), 1)

    def draw_text(self, pos, font, text, color=(255,255,255), halign=0, valign=0):
        tmp_text = font.render(text, True, color)
        text_rect = tmp_text.get_rect()
        # Horizontal alignment
        if halign == 0:
            text_rect.left = pos[0]
        elif halign == 1:
            text_rect.centerx = pos[0]
        else:
            text_rect.right = pos[0]
        # Vertical alignment
        if valign == 0:
            text_rect.top = pos[1]
        elif valign == 1:
            text_rect.centery = pos[1]
        else:
            text_rect.bottom = pos[1]

        self.blit(tmp_text, text_rect)