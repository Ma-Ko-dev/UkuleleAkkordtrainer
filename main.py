import customtkinter as ctk
import tkinter as tk
import config
import utils
import version
from gui import LegacyChordTrainerGUI, DefaultChordTrainerGUI


def create_menubar(root, app, lang, config_data):
    menubar = tk.Menu(root)

    # File menu
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_file"], menu=filemenu)
    filemenu.add_command(label=lang["submenu_reload_chords"], command=lambda: app.reload_chords(lang))
    filemenu.add_command(label=lang["submenu_exit"], command=root.quit)

    # Options menu
    optionmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_options"], menu=optionmenu)

    # Layout submenu
    layout_submenu = tk.Menu(optionmenu, tearoff=0)
    optionmenu.add_cascade(label=lang["submenu_layouts"], menu=layout_submenu)

    # layout form config
    current_layout = config_data.get("layout", "default")

    for layout_key, label, gui_class in [
        ("default", "Default", DefaultChordTrainerGUI),
        ("legacy", "Legacy", LegacyChordTrainerGUI),
    ]:
        state = "disabled" if layout_key == current_layout else "normal"
        def on_select(layout=layout_key):
            if layout != current_layout:
                # Layout in config speichern
                config_data["layout"] = layout
                utils.save_config(config_data)
                tk.messagebox.showinfo(lang["restart_info_title"], lang["restart_info_text"])
        layout_submenu.add_command(label=label, state=state, command=on_select)

    # Difficulty submenu
    difficulty_submenu = tk.Menu(optionmenu, tearoff=0)
    optionmenu.add_cascade(label=lang["difficulty"], menu=difficulty_submenu)

    difficulty_labels = {
        "easy": lang["difficulty_easy"],
        "medium": lang["difficulty_medium"],
        "hard": lang["difficulty_hard"]
    }

    # load difficulty from file or set easy as default
    current_difficulty = config_data.get("difficulty", "easy")

    def set_difficulty(level):
        nonlocal current_difficulty
        if level != current_difficulty:
            config_data["difficulty"] = level
            utils.save_config(config_data)
            current_difficulty = level
            config.DIFFICULTY = level
            app.reload_chords(lang)
            if hasattr(app, "set_difficulty"):
                app.set_difficulty(level)
            # refresh menu
            update_difficulty_menu()

    def update_difficulty_menu():
        difficulty_submenu.delete(0, "end")
        for level in difficulty_labels:
            state = "disabled" if level == current_difficulty else "normal"
            difficulty_submenu.add_command(
                label=difficulty_labels[level],
                state=state,
                command=lambda lvl=level: set_difficulty(lvl)
            )

    update_difficulty_menu()

    # Help menu
    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_help"], menu=helpmenu)
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: utils.show_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: utils.show_tutorial(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=utils.open_github)

    return menubar


def main():
    ctk.set_appearance_mode("System")  # Optional: "Dark", "Light", "System"
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()

    config_data = utils.load_config()
    layout = config_data.get("layout", "default")
    
    lang = utils.load_language(utils.get_system_language())
    utils.set_font(config.LANG_CODE)

    config.DIFFICULTY = config_data.get("difficulty", "easy")
    chords = utils.load_chords(utils.get_chord_file(), lang)

    # Fenstergröße je Layout
    if layout == "default":
        root.geometry("450x500")
        app_class = DefaultChordTrainerGUI
    else:
        root.geometry("900x400")
        app_class = LegacyChordTrainerGUI

    root.title(f"{lang['title']} Version: {version.__VERSION__}")

    app = app_class(root, chords, lang)

    root.config(menu=create_menubar(root, app, lang, config_data))

    root.mainloop()

if __name__ == "__main__":
    main()
