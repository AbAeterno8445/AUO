import pygame, textwrap

class ChatLog(object):
    def __init__(self, font):
        self.txt_wrapper = textwrap.TextWrapper()

        self.lines = 0
        self.line_size = 0

        self.font = font

        self.surface = pygame.Surface((1,1))
        self.surface_col = (255,255,255)

        self.msg_log = []

        self.inputting = False
        self.msg_input = ""

    def set_line_width(self, chars):
        self.txt_wrapper.width = chars

    def surface_resize(self, width, height=None):
        if not height:
            height = self.lines * self.line_size + 26
        self.surface = pygame.transform.scale(self.surface, (width, height))

    def draw_chat(self):
        self.surface.fill(self.surface_col)

        chat_drawn = 0
        chat_drawn_sub = 0
        while chat_drawn < self.lines and chat_drawn < len(self.msg_log):
            msg_line, msg_color = self.msg_log[-1-chat_drawn]

            for msg_wrap in reversed(self.txt_wrapper.wrap(msg_line.strip())):
                if chat_drawn > self.lines:
                    break
                line_y = self.surface.get_height() - 20 - self.line_size * (chat_drawn + chat_drawn_sub)

                msg_render = self.font.render(msg_wrap, False, msg_color)
                msg_rect = msg_render.get_rect(left=4, bottom=line_y)

                self.surface.blit(msg_render, msg_rect)

                chat_drawn_sub += 1
            chat_drawn_sub -= 1

            chat_drawn += 1

        tmp_input = self.msg_input
        if self.inputting:
            tmp_input += "_"
        inp_render = self.font.render(tmp_input, False, (255,255,255))
        inp_rect = inp_render.get_rect(left=4, bottom=self.surface.get_height() - 4)

        self.surface.blit(inp_render, inp_rect)

    def log_msg(self, msg, msg_color=(255,255,255)):
        self.msg_log.append((msg, msg_color))
        with open("client_log.txt", "a") as log_file:
            log_file.write(msg + "\n")