import customtkinter as ctk
import tkinter as tk
import config
import utils
from gui import LegacyChordTrainerGUI, DefaultChordTrainerGUI, ChordEditor



def create_menubar(root, app, lang, config_data):
    """
    Creates and returns the main menu bar for the application window.

    Includes file actions, layout and theme settings, difficulty levels, and help options.
    """
    
    root.theme_var = tk.StringVar()
    root.theme_var.set(ctk.get_appearance_mode())
    chord_editor_ref = None 

    
    def set_difficulty(level):
        """
        Changes the current difficulty level, reloads chords, updates the config and menu.

        Args:
            level (str): The difficulty level to set ("easy", "medium", or "hard").
        """
        nonlocal current_difficulty
        if level != current_difficulty:
            config_data["difficulty"] = level
            utils.save_config(config_data)
            current_difficulty = level
            config.DIFFICULTY = level
            app.logic.reload_chords(lang)
            if hasattr(app, "set_difficulty"):
                app.set_difficulty(level)
            # refresh menu
            update_difficulty_menu()
            app.logic.clear_history()

    def update_difficulty_menu():
        """
        Rebuilds the difficulty submenu with the correct enabled/disabled states.
        """
        difficulty_submenu.delete(0, "end")
        for level in difficulty_labels:
            state = "disabled" if level == current_difficulty else "normal"
            difficulty_submenu.add_command(
                label=difficulty_labels[level],
                state=state,
                command=lambda lvl=level: set_difficulty(lvl)
            )

    def switch_theme(mode):
        """
        Switches the application's theme between Light and Dark.

        Args:
            mode (str): The theme to switch to ("Light" or "Dark").
        """
        if mode == ctk.get_appearance_mode():
            return
        ctk.set_appearance_mode(mode)
        config_data["theme"] = mode
        root.update()
        if hasattr(app, "update_theme"):
            app.update_theme()
        utils.save_config(config_data)

    def open_chord_editor():
        """
        Opens the Chord Editor window, or brings it to focus if it's already open.

        On closing the editor, chords are reloaded if changes were saved.
        """
        nonlocal chord_editor_ref

        def on_editor_close():
            if chord_editor_ref.saved:
                app.logic.clear_history()
                app.logic.reload_chords(lang)

        if chord_editor_ref is None or not chord_editor_ref.winfo_exists():
            chord_editor_ref = ChordEditor(
                lang = lang, 
                master = root,
                on_close = on_editor_close
            )
            chord_editor_ref.after(25, chord_editor_ref.focus)
        else:
            chord_editor_ref.focus()


    menubar = tk.Menu(root)

    # File menu
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_file"], menu=filemenu)
    filemenu.add_command(label=lang["submenu_reload_chords"], command=lambda: app.logic.reload_chords(lang))
    filemenu.add_command(label=lang["submenu_exit"], command=root.quit)

    # Options menu
    optionmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_options"], menu=optionmenu)

    # Layout submenu
    layout_submenu = tk.Menu(optionmenu, tearoff=0)
    optionmenu.add_cascade(label=lang["submenu_layouts"], menu=layout_submenu)

    # layout from config
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
        layout_submenu.add_command(label=label, state="disabled", command=on_select)

    # theme submenu
    theme_submenu = tk.Menu(optionmenu, tearoff=0)
    optionmenu.add_cascade(label=lang["submenu_colortheme"], menu=theme_submenu)
    theme_submenu.add_radiobutton(label=lang["theme_light"], variable=root.theme_var, value="Light", command=lambda: switch_theme("light"))
    theme_submenu.add_radiobutton(label=lang["theme_dark"], variable=root.theme_var, value="Dark", command=lambda: switch_theme("dark"))

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
    update_difficulty_menu()

    # chord editor entry
    optionmenu.add_command(label=f"{lang['editor_title']}", command=open_chord_editor)

    # Help menu
    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_help"], menu=helpmenu)
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: utils.show_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: utils.show_tutorial(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=utils.open_github)

    return menubar
