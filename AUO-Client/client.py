from class_gamesystem import GameSystem
import pygame

def main():
    gamesys = GameSystem()
    gamesys.init_display(800, 600)
    gamesys.main_loop()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()