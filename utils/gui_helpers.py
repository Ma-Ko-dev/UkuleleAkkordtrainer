import json
import os
from tkinter import messagebox
import webbrowser
from version import __VERSION__


def load_chords(file_path, lang):
    if not os.path.exists(file_path):
        print(f"{lang['error_missing_chords_file']}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

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
