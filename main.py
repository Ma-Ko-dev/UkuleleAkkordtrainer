import tkinter as tk
import config
import utils
from gui import ChordTrainerGUI


def main():
    root = tk.Tk()

    lang = utils.load_language(utils.get_system_language())
    utils.set_font(config.LANG_CODE)

    chords = utils.load_chords(config.CHORD_FILE, lang)

    root.title(f"{lang['title']}")

    app = ChordTrainerGUI(root, chords, lang)

    # menubar etc.
    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_file"], menu=filemenu)
    filemenu.add_command(label=lang["submenu_reload_chords"], command=lambda: app.reload_chords(lang))
    filemenu.add_command(label=lang["submenu_exit"], command=root.quit)

    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_help"], menu=helpmenu)
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: utils.show_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: utils.show_tutorial(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=utils.open_github)

    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    main()
