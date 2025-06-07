import customtkinter as ctk
import tkinter as tk
import config
import utils
from version import __VERSION__
from gui import LegacyChordTrainerGUI, DefaultChordTrainerGUI
from gui import create_menubar


def main():
    # set color theme
    # TODO save and load theme from file
    ctk.set_appearance_mode("Dark")  # Optional: "Dark", "Light", "System"
    ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

    root = ctk.CTk()

    config_data = utils.load_config()
    layout = config_data.get("layout", "default")
    
    lang = utils.load_language(utils.get_system_language())
    utils.set_font(config.LANG_CODE)

    config.DIFFICULTY = config_data.get("difficulty", "easy")
    chords = utils.load_chords(utils.get_chord_file(), lang)

    # windowsize by layout
    if layout == "default":
        root.minsize(600, 725)
        app_class = DefaultChordTrainerGUI
    else:
        root.minsize(900, 400)
        app_class = LegacyChordTrainerGUI

    root.title(f"{lang['title']} - {lang['info_version'].format(version=__VERSION__)}")
    root.resizable(False, False)

    app = app_class(root, chords, lang)

    root.config(menu=create_menubar(root, app, lang, config_data))

    root.mainloop()

if __name__ == "__main__":
    main()
