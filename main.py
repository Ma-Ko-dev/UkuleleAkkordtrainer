import tkinter as tk
from tkinter import Canvas, messagebox
import random
import json
import os
import speech_recognition as sr
import threading
import webbrowser

__VERSION__ = "1.0.1"

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
    def __init__(self, master, akkorde):
        self.master = master
        self.akkorde = akkorde
        self.label = tk.Label(master, text="", font=("Arial", 24))
        self.label.pack(pady=10)
        self.griffbrett = Griffbrett(master)
        self.griffbrett.pack()
        self.button = tk.Button(master, text="Naechster Akkord", command=self.naechster_akkord)
        self.button.pack(pady=10)
        self.running = True

        self.naechster_akkord()
        threading.Thread(target=self.spracherkennung, daemon=True).start()

    def naechster_akkord(self):
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
            print("Fehler beim schreiben der Datei:", e)

        self.label.config(text=akkord["name"])
        self.griffbrett.zeichne_akkord(akkord["griff"])

    def spracherkennung(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while self.running:
                try:
                    print("Sage 'weiter' oder 'stopp'...")
                    audio = recognizer.listen(source, timeout=5)
                    befehl = recognizer.recognize_google(audio, language="de-DE").lower()
                    print(f"Erkannt: {befehl}")

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
                    print("API-Fehler")
                    break

    def akkorde_neu_laden(self):
        neue_akkorde = lade_akkorde(AKKORD_DATEI)
        if neue_akkorde:
            self.akkorde = neue_akkorde
        else:
            print("Fehler beim Akkorde neu laden")                

def lade_akkorde(dateipfad):
    if not os.path.exists(dateipfad):
        print("Fehlende akkorde.json Datei!")
        return []
    with open(dateipfad, "r", encoding="utf-8") as f:
        return json.load(f)
    
def zeige_info():
    info_text = (
        "Ukulele Akkordtrainer\n"
        f"Version: {__VERSION__}\n\n"
        "Author: Mathias K.\n\n"
        "Beschreibung:\n"
        "Dieses Programm zeigt zufällige Ukulele-Akkorde an und unterstützt Sprachsteuerung.\n"
        "Es richtet sich an Einsteiger und Fortgeschrittene.\n"
    )
    messagebox.showinfo("Info", info_text)

def zeige_kurzanleitung():
    anleitung_text = (
        "Ukulele Akkordtrainer\n\n"
        "• Klicke auf 'Nächster Akkord', um einen neuen Akkord zu sehen.\n"
        "• Oder sage 'weiter', um per Sprache zum nächsten Akkord zu wechseln.\n"
        "• Sage 'stopp', um das Programm zu beenden.\n"
        "• Akkorde werden zufällig angezeigt – Wiederholungen werden vermieden.\n"
        "• Alle gespielten Akkorde werden in 'letzte_akkorde.txt' gespeichert."
    )
    messagebox.showinfo("Kurzanleitung", anleitung_text)

def oeffne_github():
    webbrowser.open("https://github.com/Ma-Ko-dev/UkuleleAkkordtrainer")

def main():
    akkorde = lade_akkorde(AKKORD_DATEI)
    root = tk.Tk()
    root.title("Ukulele Akkordtrainer")

    app = AkkordTrainerGUI(root, akkorde)

    # Menüleiste etc.
    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Datei", menu=filemenu)
    filemenu.add_command(label="Akkorde neu laden", command=app.akkorde_neu_laden)
    filemenu.add_command(label="Beenden", command=root.quit)

    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Hilfe", menu=helpmenu)
    helpmenu.add_command(label="Info", command=zeige_info)
    helpmenu.add_command(label="Kurzanleitung", command=zeige_kurzanleitung)
    helpmenu.add_command(label="Github öffnen", command=oeffne_github)

    root.config(menu=menubar)
    root.mainloop()

if __name__ == "__main__":
    main()
