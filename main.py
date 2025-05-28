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

AKKORD_DATEI = "akkorde.json"
VERGANGENE_AKKORDE = []
MAX_HISTORY = 4

class Griffbrett(Canvas):
    def __init__(self, master, breite=800, hoehe=200, **kwargs):
        self.string_label_breite = 40
        super().__init__(master, width=breite + self.string_label_breite, height=hoehe, bg='#F3E9D2', **kwargs)  # helles Holz
        self.bundanzahl = 12
        self.saitenanzahl = 4
        self.bund_abstand = breite / self.bundanzahl
        self.saiten_abstand = hoehe / (self.saitenanzahl + 1)
        self.markierungen = []
        self.saitennamen = ["G", "C", "E", "A"]
        self.zeichne_grundlinien()

    def zeichne_grundlinien(self):
        self.delete("all")
        # Saitennamen links - dunkelgrau, schlicht
        for i, name in enumerate(self.saitennamen):
            y = (i + 1) * self.saiten_abstand
            self.create_text(12, y, text=name, font=("Arial", 16, "bold"), anchor="w", fill="#3B3B3B")

        # Bünde (senkrecht) - braun, realistisch wie Metallstifte
        for i in range(self.bundanzahl + 1):
            x = self.string_label_breite + i * self.bund_abstand
            linienfarbe = "#6B4C3B"  # dunkles braun
            linienstil = (2, 4) if i != 0 else None
            linienbreite = 3 if i == 0 else 1
            self.create_line(x, 0, x, self.winfo_reqheight(), fill=linienfarbe, dash=linienstil, width=linienbreite)

        # Saiten (waagerecht) - dunkelgrau, etwas dicker für realistisches Gefühl
        for i in range(1, self.saitenanzahl + 1):
            y = i * self.saiten_abstand
            start_x = self.string_label_breite
            end_x = self.string_label_breite + self.bund_abstand * self.bundanzahl
            self.create_line(start_x, y, end_x, y, fill="#4A4A4A", width=3)

    def zeichne_akkord(self, griff):
        for m in self.markierungen:
            self.delete(m)
        self.markierungen.clear()

        for saite_idx, bund in enumerate(griff):
            try:
                bund_num = int(bund)
                if 1 <= bund_num <= self.bundanzahl:
                    x = self.string_label_breite + self.bund_abstand * (bund_num - 0.5)
                    y = (saite_idx + 1) * self.saiten_abstand
                    kreis = self.create_oval(x - 12, y - 12, x + 12, y + 12, fill="#8B0000")  # dunkles rot
                    nummer = self.create_text(x, y, text=str(bund), fill="white", font=("Arial", 12, "bold"))
                    self.markierungen.extend([kreis, nummer])
            except ValueError:
                continue

class AkkordTrainerGUI:
    def __init__(self, master, akkorde, lang):
        self.master = master
        self.akkorde = akkorde
        self.lang = lang
        self.label = tk.Label(master, text="", font=("Arial", 24))
        self.label.pack(pady=10)
        self.griffbrett = Griffbrett(master)
        self.griffbrett.pack()
        self.button = tk.Button(master, text=f"{lang['next_chord_button']}", command=lambda: self.naechster_akkord(lang))
        self.button.pack(pady=10)
        self.running = True

        self.naechster_akkord(lang)
        threading.Thread(target=self.spracherkennung, args=(lang,), daemon=True).start()

    def naechster_akkord(self, lang):
        # Namen vereinheitlichen
        vergangene_namen = [n.strip().lower() for n in VERGANGENE_AKKORDE]

        moegliche = [
            a for a in self.akkorde
            if a["name"].strip().lower() not in vergangene_namen
        ]

        if not moegliche:
            VERGANGENE_AKKORDE.clear()
            moegliche = self.akkorde[:]

        akkord = random.choice(moegliche)
        VERGANGENE_AKKORDE.append(akkord["name"].strip())

        if len(VERGANGENE_AKKORDE) > MAX_HISTORY:
            VERGANGENE_AKKORDE.pop(0)

        try:
            with open("letzte_akkorde.txt", "w", encoding="utf-8") as f:
                f.write(" - ".join(VERGANGENE_AKKORDE))
        except IOError as e:
            print(lang["error_write_file"], e)

        self.label.config(text=akkord["name"])
        self.griffbrett.zeichne_akkord(akkord["griff"])

    def spracherkennung(self, lang):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.running:
                try:
                    print(lang["speech_info"])
                    audio = recognizer.listen(source, timeout=5)
                    befehl = recognizer.recognize_google(audio, language="de-DE").lower()
                    print(f"{lang['speech_recognized'].format(command=befehl)}")
                    
                    # spracherkennung ist noch nicht multilingual
                    if "weiter" in befehl:
                        self.naechster_akkord()
                    elif "stopp" in befehl:
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

    def akkorde_neu_laden(self, lang):
        neue_akkorde = lade_akkorde(AKKORD_DATEI, lang)
        if neue_akkorde:
            self.akkorde = neue_akkorde
        else:
            print(f"{lang['error_reloading_chords']}")

def lade_sprache(lang_code):
    path = os.path.join("lang", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Sprachdatei nicht gefunden: {path}.")
        # lade failsafe sprache
        return lade_sprache("de")

def lade_akkorde(dateipfad, lang):
    if not os.path.exists(dateipfad):
        print(f"{lang['error_missing_chords_file']}")
        return []
    with open(dateipfad, "r", encoding="utf-8") as f:
        return json.load(f)
    
def zeige_info(lang):
    info_text = (
        f"{lang['info_title']}\n"
        f"{lang['info_version'].format(version=__VERSION__)}\n\n"
        f"{lang['info_author']}\n\n"
        f"{lang['info_description_heading']}:\n"
        f"{lang['info_description']}"
    )
    messagebox.showinfo(lang["submenu_info"], info_text)

def zeige_kurzanleitung(lang):
    text = "\n".join(lang["short_manual_text"])
    messagebox.showinfo(lang["short_manual_title"], text)

def oeffne_github():
    webbrowser.open("https://github.com/Ma-Ko-dev/UkuleleAkkordtrainer")

def systemsprache_holen():
    locale.setlocale(locale.LC_ALL, '') 
    lang, _ = locale.getlocale()
    if not lang:
        lang = "en_US" #fallback
    return lang

def main():
    # sprache laden
    lang = lade_sprache(systemsprache_holen())

    akkorde = lade_akkorde(AKKORD_DATEI, lang)

    root = tk.Tk()
    root.title("Ukulele Akkordtrainer")

    app = AkkordTrainerGUI(root, akkorde, lang)

    # Menüleiste etc.
    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_file"], menu=filemenu)
    filemenu.add_command(label=lang["submenu_reload_chords"], command=lambda: app.akkorde_neu_laden(lang))
    filemenu.add_command(label=lang["submenu_exit"], command=root.quit)

    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=lang["menu_help"], menu=helpmenu)
    helpmenu.add_command(label=lang["submenu_info"], command=lambda: zeige_info(lang))
    helpmenu.add_command(label=lang["submenu_short_manual"], command=lambda: zeige_kurzanleitung(lang))
    helpmenu.add_command(label=lang["submenu_github"], command=oeffne_github)

    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    main()
