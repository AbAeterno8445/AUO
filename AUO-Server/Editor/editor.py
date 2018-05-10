from class_editor import Editor
import pygame

def main():
    editor = Editor()
    editor.init_display(1280, 720)

    editor.main_loop()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()