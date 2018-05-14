import traceback
from class_editor import Editor
import pygame

def main():
    editor = Editor()

    try:
        editor.init_display(int(input("Resolution X > ")), int(input("Resolution Y > ")))
    except:
        editor.init_display(1280, 720)

    print("Running editor at " + str(editor.display.get_width()) + " x " + str(editor.display.get_height()))
    try:
        editor.main_loop()
    except:
        print(traceback.print_exc())
        if editor.map.loaded:
            save_prompt = input("Editor crashed. Save map progress? (Y to save) > ")
            if save_prompt.lower() == "y":
                if editor.map.save():
                    print("Map saved.")

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()