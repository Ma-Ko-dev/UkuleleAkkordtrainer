import tkinter as tk
import config
from gui.fretboardLegacy import LegacyFretboard
from gui.baseChordTrainerGUI import BaseChordTrainerGUI


class LegacyChordTrainerGUI(BaseChordTrainerGUI):
    # TODO Refactor Legacy and Default GUI 
    def build_widgets(self, master, lang):
        self.chord_label = tk.Label(master, text="", font=(config.BASE_FONT, 24))
        self.chord_label.pack(pady=10)

        self.fretboard = LegacyFretboard(master)
        self.fretboard.pack()

        self.timer_display = tk.Label(master, text="", font=(config.BASE_FONT, 14))
        self.timer_display.pack()

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.next_chord_button = tk.Button(button_frame, text=f"{lang['next_chord_button']}", command=lambda: self.next_chord(lang))
        self.next_chord_button.pack(side="left", pady=10)

        self.timer_button = tk.Button(button_frame, text=f"{lang['timer_button_start']}", command=lambda: self.toggle_timer(lang))
        self.timer_button.pack(side="left", pady=5)
