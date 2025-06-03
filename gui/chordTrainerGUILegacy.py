import random
import threading
import time
import tkinter as tk
import config
import speech_recognition as sr
from gui.fretboardLegacy import LegacyFretboard
from utils.gui_helpers import load_chords, get_chord_file


class LegacyChordTrainerGUI:
    # TODO Refactor Legacy and Default GUI 
    def __init__(self, master, chords, lang):
        self.master = master
        self.chords = chords
        self.lang = lang
        self.speech_enabled = True
        self.chord_label = tk.Label(master, text="", font=(config.BASE_FONT, 24))
        self.chord_label.pack(pady=10)
        self.fretboard = LegacyFretboard(master)
        self.fretboard.pack()
        self.timer_active = False
        self.timer_interval = 10000 # in ms ca. 10 seconds
        self.timer_id = None
        self.timer_display = tk.Label(master, text="", font=(config.BASE_FONT, 14))
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
        past_names = [n.strip().lower() for n in config.PAST_CHORDS]

        possible = [
            a for a in self.chords
            if a["name"].strip().lower() not in past_names
        ]

        if not possible:
            config.PAST_CHORDS.clear()
            possible = self.chords[:]

        chord = random.choice(possible)
        config.PAST_CHORDS.append(chord["name"].strip())

        if len(config.PAST_CHORDS) > config.MAX_HISTORY:
            config.PAST_CHORDS.pop(0)

        try:
            with open("last_chords.txt", "w", encoding="utf-8") as f:
                f.write(" - ".join(config.PAST_CHORDS))
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
                    audio_command = recognizer.recognize_google(audio, language=config.LANG_CODE).lower()
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
        new_chords = load_chords(get_chord_file(), lang)
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

    # def stop(self):
    #     # Stop timer if active
    #     if self.timer_active:
    #         self.timer_active = False
    #         if self.timer_id:
    #             self.master.after_cancel(self.timer_id)
    #             self.timer_id = None
    #         self.next_chord_button.config(state="normal")
    #         self.speech_enabled = True
    #         self.timer_display.config(text="")
    #         self.timer_button.config(text=self.lang["timer_button_start"])

    #     self.running = False
