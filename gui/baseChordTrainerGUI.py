import random
import threading
import time
import config
import speech_recognition as sr
from tkinter import Tk
from utils.gui_helpers import load_chords, get_chord_file


class BaseChordTrainerGUI:
    def __init__(self, master: Tk, chords, lang):
        self.master = master
        self.chords = chords
        self.lang = lang
        self.speech_enabled = True
        self.learned_chords = 0
        self.timer_active = False
        self.timer_interval = 10000 # in ms ca. 10 seconds
        self.timer_id = None
        self.running = True

        self.build_widgets(master, lang) 

        self.master.after(100, lambda: self.next_chord(lang))
        threading.Thread(target=self.speech_recognition, args=(lang,), daemon=True).start()

    def build_widgets(self, master, lang):
        raise NotImplementedError("Subclasses must implement build_widgets")

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
        self.fretboard_middle.draw_chord(chord["fingering"])
        self.learned_chords = self.learned_chords + 1
        self.learned_label_left.config(text=self.lang["learned_chords_text"].format(count=self.learned_chords))

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
