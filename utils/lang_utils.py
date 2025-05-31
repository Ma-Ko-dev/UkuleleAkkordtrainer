import json
import locale
import os
import config


def get_system_language():
    locale.setlocale(locale.LC_ALL, '') 
    lang, _ = locale.getlocale()

    # fallback if lang is None
    if not lang:
        lang = "en_US"

    lang_map = {
        "Japanese_Japan": "jp_JP",
        "German_Germany": "de_DE",
        "English_United States": "en_US",
        "Italian_Italy": "it_IT"
    }

    config.LANG_CODE = lang_map.get(lang, lang)
    return config.LANG_CODE


def load_language(lang_code):
    path = os.path.join("lang", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if lang_code != "en_US":
            print(f"Speech file not found: {path}. Falling back to English.")
            return load_language("en_US")
        else:
            print("Critical error: English language file missing.")
            raise FileNotFoundError("English language file missing. Cannot continue.")
