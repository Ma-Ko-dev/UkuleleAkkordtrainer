import json
import os
import webbrowser
import config
from tkinter import messagebox
from version import __VERSION__


def load_chords(lang, filter_by_difficulty=True):
    if not os.path.exists(config.CHORD_PATH):
        print(f"{lang['error_missing_chords_file']}")
        return [] if filter_by_difficulty else {}
    
    with open(config.CHORD_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

        if filter_by_difficulty:
            chords = data.get(config.DIFFICULTY, [])
            if not chords:
                print(f"{lang['error_no_chords_for_difficulty'] ({config.DIFFICULTY})}")
            return data.get(config.DIFFICULTY, [])
        
    return data


def show_info(lang):
    info_text = (
        f"{lang['info_title']}\n"
        f"{lang['info_version'].format(version=__VERSION__)}\n\n"
        f"{lang['info_author']}\n\n"
        f"{lang['info_description_heading']}:\n"
        f"{lang['info_description']}"
    )
    messagebox.showinfo(lang["submenu_info"], info_text)


def show_tutorial(lang):
    text = "\n".join(lang["short_manual_text"])
    messagebox.showinfo(lang["short_manual_title"], text)
    

def open_github():
    webbrowser.open("https://github.com/Ma-Ko-dev/UkuleleAkkordtrainer")


def load_config():
    if not os.path.exists(config.CONFIG_PATH):
        # create default config
        default_config = {
            "layout": "default", 
            "difficulty": "easy",
            "theme": "dark"
            }
        save_config(default_config)
        return default_config
    with open(config.CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(config.CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)
