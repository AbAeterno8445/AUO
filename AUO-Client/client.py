from class_gamesystem import GameSystem
import pygame

def main():
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_icon(pygame.image.load("assets/AUOicon.png"))
    pygame.display.set_caption("AUO Client")

    gamesys = GameSystem(display)
    gamesys.main_loop()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()