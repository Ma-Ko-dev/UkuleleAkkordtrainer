import tkinter as tk
import config
import speech_recognition as sr
from tkinter import Tk
from gui.fretboardDefault import DefaultFretboard
from gui.baseChordTrainerGUI import BaseChordTrainerGUI


class DefaultChordTrainerGUI(BaseChordTrainerGUI):
    def build_widgets(self, master, lang):

        self.master.grid_columnconfigure(0, weight=1, minsize=150)
        self.master.grid_columnconfigure(1, weight=1, minsize=160)
        self.master.grid_columnconfigure(2, weight=1, minsize=150)

        self.master.grid_rowconfigure(0, weight=0)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=0)
        self.master.grid_rowconfigure(3, weight=0)

        self.chord_label = tk.Label(master, text="", font=(config.BASE_FONT, 24))
        self.chord_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.learned_label_left = tk.Label(master, text="", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 14))
        self.learned_label_left.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")

        self.fretboard_middle = DefaultFretboard(master)
        self.fretboard_middle.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.dummy_label_right = tk.Label(master, text=" ", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 12))
        self.dummy_label_right.grid(row=1, column=2, padx=5, pady=2, sticky="nsew")

        self.timer_display = tk.Label(master, text="", font=(config.BASE_FONT, 14))
        self.timer_display.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttom_frame = tk.Frame(master)
        self.buttom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttons_inner = tk.Frame(self.buttom_frame)       
        self.buttons_inner.pack(anchor="center")

        self.next_chord_button = tk.Button(self.buttons_inner, text=f"{lang['next_chord_button']}", command=lambda: self.next_chord(lang))
        self.next_chord_button.pack(side="left", padx=5)
        self.timer_button = tk.Button(self.buttons_inner, text=f"{lang['timer_button_start']}", command=lambda: self.toggle_timer(lang))
        self.timer_button.pack(side="left", padx=5)
