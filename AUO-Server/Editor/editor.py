from class_editor import Editor
import pygame

def main():
    editor = Editor()

    try:
        resol = (int(input("Resolution X > ")), int(input("Resolution Y > ")))
        editor.init_display(*resol)
    except:
        editor.init_display(1280, 720)

    print("Running editor at " + str(editor.display.get_width()) + " x " + str(editor.display.get_height()))
    # Add try/except with error printing when map saving is implemented. Map save prompt on except
    editor.main_loop()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()