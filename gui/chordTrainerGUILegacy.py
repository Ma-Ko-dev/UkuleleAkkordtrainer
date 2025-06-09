import tkinter as tk
import config
from gui.fretboardLegacy import LegacyFretboard
from gui.guiLogicManager import GuiLogicManager


class LegacyChordTrainerGUI(tk.Frame):
    def __init__(self, master, chords, lang):
        super().__init__(master)
        self.chords = chords
        self.lang = lang
        self.logic = GuiLogicManager(self, chords, lang)
        self.build_widgets(lang)
        self.pack(fill="both", expand=True)

    def get_first_chord(self):
        self.logic.next_chord(self.lang)


    def update_chord_label(self, text):
        self.chord_label.config(text=text)


    def update_fretboard(self, fingering):
        self.fretboard_middle.draw_chord(fingering)


    def update_learned_label(self, text):
        self.learned_label_left.config(text=text)

    
    def update_timer_label(self, text):
        self.timer_display.config(text=text)


    def set_timer_button_text(self, text):
        self.timer_button.config(text=text)


    def set_next_chord_button_state(self, state):
        self.next_chord_button.config(state=state)


    def build_widgets(self, lang):
        self.chord_label = tk.Label(self, text="", font=(config.BASE_FONT, 24))
        self.chord_label.pack(pady=10)

        self.fretboard_middle = LegacyFretboard(self)
        self.fretboard_middle.pack()

        self.learned_label_left = tk.Label(self, text="", font=(config.BASE_FONT, 12))
        self.learned_label_left.pack()

        self.timer_display = tk.Label(self, text="", font=(config.BASE_FONT, 14))
        self.timer_display.pack()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.next_chord_button = tk.Button(button_frame, text=f"{lang['next_chord_button']}", font=(config.BASE_FONT, 12), command=lambda: self.logic.next_chord(lang))
        self.next_chord_button.pack(side="left", pady=5)

        self.timer_button = tk.Button(button_frame, text=f"{lang['timer_button_start']}", font=(config.BASE_FONT, 12), command=lambda: self.logic.toggle_timer(lang))
        self.timer_button.pack(side="left", pady=5)
