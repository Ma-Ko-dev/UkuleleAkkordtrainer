import tkinter as tk
from tkinter import Canvas, messagebox
import random
import json
import os
import speech_recognition as sr
import threading
import webbrowser
import locale

__VERSION__ = "1.0.2"

CHORD_FILE = "akkorde.json"
PAST_CHORDS = []
MAX_HISTORY = 4

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
            self.create_text(12, y, text=name, font=("Arial", 16, "bold"), anchor="w", fill="#3B3B3B")

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
                    number = self.create_text(x, y, text=str(fret), fill="white", font=("Arial", 12, "bold"))
                    self.markers.extend([circle, number])
            except ValueError:
                continue

class ChordTrainerGUI:
    def __init__(self, master, chords, lang):
        self.master = master
        self.chords = chords
        self.lang = lang
        self.label = tk.Label(master, text="", font=("Arial", 24))
        self.label.pack(pady=10)
        self.fretboard = Fretboard(master)
        self.fretboard.pack()
        self.button = tk.Button(master, text=f"{lang['next_chord_button']}", command=lambda: self.next_chord(lang))
        self.button.pack(pady=10)
        self.running = True

        self.next_chord(lang)
        threading.Thread(target=self.speech_recognition, args=(lang,), daemon=True).start()

    def next_chord(self, lang):
        # Normalize names
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
            with open("letzte_akkorde.txt", "w", encoding="utf-8") as f:
                f.write(" - ".join(PAST_CHORDS))
        except IOError as e:
            print(lang["error_write_file"], e)

        self.label.config(text=chord["name"])
        self.fretboard.draw_chord(chord["griff"])

    def speech_recognition(self, lang):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.running:
                try:
                    print(lang["speech_info"])
                    audio = recognizer.listen(source, timeout=5)
                    audio_command = recognizer.recognize_google(audio, language="de-DE").lower()
                    print(f"{lang['speech_recognized'].format(command=audio_command)}")
                    
                    # spracherkennung ist noch nicht multilingual
                    # speech recognition is not multilingual yet
                    if "weiter" in audio_command:
                        self.next_chord()
                    elif "stop" in audio_command:
                        print("Beendet.")
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

def load_language(lang_code):
    path = os.path.join("lang", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Speech file not found: {path}.")
        # load failsafe
        return load_language("en_US")

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

def get_system_language():
    locale.setlocale(locale.LC_ALL, '') 
    lang, _ = locale.getlocale()
    if not lang:
        lang = "en_US" #fallback
    return lang

def main():
    # load language
    lang = load_language(get_system_language())

    chords = load_chords(CHORD_FILE, lang)

    root = tk.Tk()
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
