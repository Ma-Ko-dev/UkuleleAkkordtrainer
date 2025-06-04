import json
import os
import webbrowser
import config
from tkinter import messagebox
from version import __VERSION__


def load_chords(file_path, lang):
    if not os.path.exists(file_path):
        print(f"{lang['error_missing_chords_file']}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def get_chord_file():
    # TODO dont use global difficulty
    return f"chords/chords_{config.DIFFICULTY}.json"


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
    # TODO check this. we already have a config.py
    if not os.path.exists(config.CONFIG_PATH):
        # create default config
        default_config = {"layout": "default", "difficulty": "easy"}
        save_config(default_config)
        return default_config
    with open(config.CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(config.CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)
