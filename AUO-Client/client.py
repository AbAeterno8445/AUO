from class_gamesystem import GameSystem
import pygame

def main():
    gamesys = GameSystem()
    host = input("Server hostname or ip? ")
    port = int(input("Server port? "))
    gamesys.connect(host, port)

    gamesys.init_display(800, 600)

    gamesys.main_loop()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()