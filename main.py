import tkinter as tk
from tkinter import Canvas, messagebox
import tkinter.font as tkfont
import random
import json
import os
import speech_recognition as sr
import threading
import webbrowser
import locale
import time

__VERSION__ = "1.1.1"

CHORD_FILE = "chords.json"
PAST_CHORDS = []
MAX_HISTORY = 4
LANG_CODE = ""
BASE_FONT = ""

class Fretboard(Canvas):
    def __init__(self, master, width=800, height=200, **kwargs):
        self.string_label_width = 40
        super().__init__(master, width=width + self.string_label_width, height=height, bg='#F3E9D2', **kwargs)  # light wood
        self.fret_count = 12
        self.string_count = 4
        self.fret_spacing = width / self.fret_count
        self.string_spacing = height / (self.string_count + 1)
        self.markers = []
        self.string_names = ["G", "C", "E", "A"]
        self.draw_base_lines()

    def draw_base_lines(self):
        self.delete("all")
        # Stringnames left
        for i, name in enumerate(self.string_names):
            y = (i + 1) * self.string_spacing
            self.create_text(12, y, text=name, font=(BASE_FONT, 16, "bold"), anchor="w", fill="#3B3B3B")

        # Frets (vertical) - brown, realistic like metal rods
        for i in range(self.fret_count + 1):
            x = self.string_label_width + i * self.fret_spacing
            line_color = "#6B4C3B"  # dunkles braun
            line_style = (2, 4) if i != 0 else None
            line_width = 3 if i == 0 else 1
            self.create_line(x, 0, x, self.winfo_reqheight(), fill=line_color, dash=line_style, width=line_width)

        # Strings (horizontal) - dark gray, slightly thicker for a realistic feel
        for i in range(1, self.string_count + 1):
            y = i * self.string_spacing
            start_x = self.string_label_width
            end_x = self.string_label_width + self.fret_spacing * self.fret_count
            self.create_line(start_x, y, end_x, y, fill="#4A4A4A", width=3)

    def draw_chord(self, fretboard):
        for m in self.markers:
            self.delete(m)
        self.markers.clear()

        for string_idx, fret in enumerate(fretboard):
            try:
                fret_num = int(fret)
                if 1 <= fret_num <= self.fret_count:
                    x = self.string_label_width + self.fret_spacing * (fret_num - 0.5)
                    y = (string_idx + 1) * self.string_spacing
                    circle = self.create_oval(x - 12, y - 12, x + 12, y + 12, fill="#8B0000") 
                    number = self.create_text(x, y, text=str(fret), fill="white", font=(BASE_FONT, 12, "bold"))
                    self.markers.extend([circle, number])
            except ValueError:
                continue

class ChordTrainerGUI:
    def __init__(self, master, chords, lang):
        self.master = master
        self.chords = chords
        self.lang = lang
        self.speech_enabled = True
        self.chord_label = tk.Label(master, text="", font=(BASE_FONT, 24))
        self.chord_label.pack(pady=10)
        self.fretboard = Fretboard(master)
        self.fretboard.pack()
        self.timer_active = False
        self.timer_interval = 10000 # in ms ca. 10 seconds
        self.timer_id = None
        self.timer_display = tk.Label(master, text="", font=(BASE_FONT, 14))
        self.timer_display.pack()

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.next_chord_button = tk.Button(button_frame, text=f"{lang['next_chord_button']}", command=lambda: self.next_chord(lang))
        self.next_chord_button.pack(side="left", pady=10)

        self.timer_button = tk.Button(button_frame, text=f"{lang['timer_button_start']}", command=lambda: self.toggle_timer(lang))
        self.timer_button.pack(side="left", pady=5)

        self.running = True
        self.lang_s = "en_US"

        self.next_chord(lang)
        threading.Thread(target=self.speech_recognition, args=(lang,), daemon=True).start()

    def next_chord(self, lang):
        past_names = [n.strip().lower() for n in PAST_CHORDS]

        possible = [
            a for a in self.chords
            if a["name"].strip().lower() not in past_names
        ]

        if not possible:
            PAST_CHORDS.clear()
            possible = self.chords[:]

        chord = random.choice(possible)
        PAST_CHORDS.append(chord["name"].strip())

        if len(PAST_CHORDS) > MAX_HISTORY:
            PAST_CHORDS.pop(0)

        try:
            with open("last_chords.txt", "w", encoding="utf-8") as f:
                f.write(" - ".join(PAST_CHORDS))
        except IOError as e:
            print(lang["error_write_file"], e)

        self.chord_label.config(text=chord["name"])
        self.fretboard.draw_chord(chord["fingering"])

    def speech_recognition(self, lang):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.running:
                try:
                    if not self.speech_enabled:
                        time.sleep(0.5)
                        continue
                    print(lang["speech_info"])
                    audio = recognizer.listen(source, timeout=5)
                    if not self.speech_enabled:
                        continue
                    audio_command = recognizer.recognize_google(audio, language=LANG_CODE).lower()
                    print(f"{lang['speech_recognized'].format(command=audio_command)}")
                    
                    if lang["speech_next"] in audio_command:
                        self.next_chord(lang)
                    elif lang["speech_stop"] in audio_command:
                        self.running = False
                        self.master.quit()
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print(f"{lang['error_api']}")
                    break

    def reload_chords(self, lang):
        new_chords = load_chords(CHORD_FILE, lang)
        if new_chords:
            self.chords = new_chords
        else:
            print(f"{lang['error_reloading_chords']}")

    def toggle_timer(self, lang):
        if self.timer_active:
            self.timer_active = False
            if self.timer_id:
                self.master.after_cancel(self.timer_id)
                self.timer_id = None
            
            self.next_chord_button.config(state="normal")
            self.speech_enabled = True
            self.timer_display.config(text="")
        else:
            self.timer_active = True
            self.next_chord_button.config(state="disabled")
            self.speech_enabled = False
            self.schedule_next_timer()

        self.timer_button.config(text=lang["timer_button_stop"] if self.timer_active else lang["timer_button_start"])
    
    def schedule_next_timer(self):
        if self.timer_active:
            self.countdown(self.timer_interval // 1000)
            #self.next_chord(self.lang)
            #self.timer_id = self.master.after(self.timer_interval, self.schedule_next_timer)

    def update_timer_display(self, seconds_left):
        self.timer_display.config(text=f"Noch {seconds_left} Sekunden bis zum nächsten Akkord")
        self.timer_display.config(text=f"{self.lang['timer_text'].format(seconds_left=seconds_left)}")

    def countdown(self, seconds_left):
        if not self.timer_active:
            self.timer_display.config(text="")
            return
        
        self.update_timer_display(seconds_left)

        if seconds_left <= 0:
            self.next_chord(self.lang)
            self.countdown(self.timer_interval // 1000)
        else:
            self.timer_id = self.master.after(1000, lambda: self.countdown(seconds_left - 1))


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

def set_font(lang_code):
    global BASE_FONT
    fonts = tkfont.families()

    if lang_code == "jp_JP":
        preferred_fonts = ["Yu Gothic UI", "Meiryo", "MS UI Gothic"]

        for font_name in preferred_fonts:
            if font_name in fonts:
                print(f"Using font: {font_name}")
                BASE_FONT = font_name
                break
        else:
            raise RuntimeError("No suitable Japanese font found. Please install a Japanese font.")
    else:
        BASE_FONT = "Arial"

def get_system_language():
    global LANG_CODE
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

    LANG_CODE = lang_map.get(lang, lang)
    return LANG_CODE

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

def main():
    root = tk.Tk()

    lang = load_language(get_system_language())
    set_font(LANG_CODE)

    chords = load_chords(CHORD_FILE, lang)

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
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: show_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: show_tutorial(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=open_github)

    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    main()
