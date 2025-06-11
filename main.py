import customtkinter as ctk
import tkinter as tk
import config
import utils
from gui import LegacyChordTrainerGUI 
from gui import DefaultChordTrainerGUI
from gui import create_menubar
from version import __VERSION__



def main():
    root = ctk.CTk()

    config_data = utils.load_config()
    layout = config_data.get("layout", "default")

    # set color theme
    ctk.set_appearance_mode(config_data["theme"])  # "Dark" (standard), "Light", "System"
    ctk.set_default_color_theme("dark-blue")  # "blue" (standard), "green", "dark-blue"
    
    lang = utils.load_language(utils.get_system_language())
    utils.set_font(config.LANG_CODE)

    config.DIFFICULTY = config_data.get("difficulty", "easy")
    chords = utils.load_chords(utils.get_chord_file(), lang)

    # windowsize by layout
    if layout == "default":
        root.minsize(700, 750)
        app_class = DefaultChordTrainerGUI
    else:
        root.minsize(900, 400)
        app_class = LegacyChordTrainerGUI


    root.title(f"{lang['title']} - {lang['info_version'].format(version=__VERSION__)}")
    root.resizable(True, False)

    app = app_class(root, chords, lang)

    root.config(menu=create_menubar(root, app, lang, config_data))

    # debug
    # root.update()  # Layout erzwingen
    # print(f"Fenstergröße nach update(): {root.winfo_width()}x{root.winfo_height()}")


    root.mainloop()

if __name__ == "__main__":
    main()
