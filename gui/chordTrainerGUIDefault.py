import tkinter as tk
import config
from gui.fretboardDefault import DefaultFretboard
from gui.guiLogicManager import GuiLogicManager


class DefaultChordTrainerGUI(tk.Frame):
    def __init__(self, master, chords, lang):
        super().__init__(master)
        self.chords = chords
        self.lang = lang
        self.logic = GuiLogicManager(self, chords, lang)
        self.build_widgets(lang)
        self.pack(fill="both", expand=True)


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
        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=1, minsize=160)
        self.grid_columnconfigure(2, weight=1, minsize=150)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.chord_label = tk.Label(self, text="", font=(config.BASE_FONT, 24))
        self.chord_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.learned_label_left = tk.Label(self, text="", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 14))
        self.learned_label_left.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")

        self.fretboard_middle = DefaultFretboard(self)
        self.fretboard_middle.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.dummy_label_right = tk.Label(self, text=" ", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 12))
        self.dummy_label_right.grid(row=1, column=2, padx=5, pady=2, sticky="nsew")

        self.timer_display = tk.Label(self, text="", font=(config.BASE_FONT, 14))
        self.timer_display.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttom_frame = tk.Frame(self)
        self.buttom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttons_inner = tk.Frame(self.buttom_frame)       
        self.buttons_inner.pack(anchor="center")

        self.next_chord_button = tk.Button(self.buttons_inner, text=f"{lang['next_chord_button']}", command=lambda: self.logic.next_chord(lang))
        self.next_chord_button.pack(side="left", padx=5)
        self.timer_button = tk.Button(self.buttons_inner, text=f"{lang['timer_button_start']}", command=lambda: self.logic.toggle_timer(lang))
        self.timer_button.pack(side="left", padx=5)
