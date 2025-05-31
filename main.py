import tkinter as tk
import config
import utils
from gui import LegacyChordTrainerGUI, DefaultChordTrainerGUI


def create_menubar(root, app_ref, chords, lang):
    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_file"], menu=filemenu)
    filemenu.add_command(label=lang["submenu_reload_chords"], command=lambda: app_ref[0].reload_chords(lang))
    filemenu.add_command(label=lang["submenu_exit"], command=root.quit)

    optionmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Options", menu=optionmenu)

    layout_submenu = tk.Menu(optionmenu, tearoff=0)

    def switch_to_default():
        switch_layout(DefaultChordTrainerGUI, root, app_ref, chords, lang)

    def switch_to_legacy():
        switch_layout(LegacyChordTrainerGUI, root, app_ref, chords, lang)

    # Layout menu with choices, disables current layout
    if isinstance(app_ref[0], DefaultChordTrainerGUI):
        layout_submenu.add_command(label="Default Layout", state="disabled")
        layout_submenu.add_command(label="Legacy Layout", command=switch_to_legacy)
    else:
        layout_submenu.add_command(label="Default Layout", command=switch_to_default)
        layout_submenu.add_command(label="Legacy Layout", state="disabled")

    optionmenu.add_cascade(label="Layout", menu=layout_submenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_help"], menu=helpmenu)
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: utils.show_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: utils.show_tutorial(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=utils.open_github)

    return menubar

def switch_layout(gui_class, root, app_ref, chords, lang):
    # Stop GUI thread if running
    if app_ref[0] is not None:
        app_ref[0].stop()

    # Remove all widgets from root
    for widget in root.winfo_children():
        widget.destroy()

    # Set window size based on layout
    if gui_class == DefaultChordTrainerGUI:
        root.geometry("450x500")
    elif gui_class == LegacyChordTrainerGUI:
        root.geometry("900x400")

    # Create new GUI and save reference
    app_ref[0] = gui_class(root, chords, lang)

    # Reset the menu
    root.config(menu=create_menubar(root, app_ref, chords, lang))

def main():
    root = tk.Tk()
    root.geometry("450x500")

    lang = utils.load_language(utils.get_system_language())
    utils.set_font(config.LANG_CODE)

    chords = utils.load_chords(config.CHORD_FILE, lang)

    root.title(f"{lang['title']}")

    # Store app in list to modify in nested funcs
    app = [DefaultChordTrainerGUI(root, chords, lang)]

    root.config(menu=create_menubar(root, app, chords, lang))

    root.mainloop()

if __name__ == "__main__":
    main()
