from tkinter import font as tkfont
import config

def set_font(lang_code):
    fonts = tkfont.families()

    if lang_code == "jp_JP":
        preferred_fonts = ["Yu Gothic UI", "Meiryo", "MS UI Gothic"]

        for font_name in preferred_fonts:
            if font_name in fonts:
                print(f"Using font: {font_name}")
                config.BASE_FONT = font_name
                break
        else:
            raise RuntimeError("No suitable Japanese font found. Please install a Japanese font.")
    else:
        config.BASE_FONT = "Arial"
