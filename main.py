import tkinter as tk
from tkinter import Canvas
import random
import json
import os
import speech_recognition as sr
import threading

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

def lade_akkorde(dateipfad):
    if not os.path.exists(dateipfad):
        print("Fehlende akkorde.json Datei!")
        return []
    with open(dateipfad, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    akkorde = lade_akkorde(AKKORD_DATEI)
    root = tk.Tk()
    root.title("Ukulele Akkordtrainer")
    app = AkkordTrainerGUI(root, akkorde)
    root.mainloop()

if __name__ == "__main__":
    main()