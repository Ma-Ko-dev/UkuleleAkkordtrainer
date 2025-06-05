import customtkinter as ctk
import config
from gui.fretboardDefault import DefaultFretboard
from gui.guiLogicManager import GuiLogicManager


class DefaultChordTrainerGUI(ctk.CTkFrame):
    def __init__(self, master, chords, lang):
        super().__init__(master)
        self.chords = chords
        self.lang = lang

        self.build_widgets()
        self.logic = GuiLogicManager(self, chords, lang)

        self.pack(fill="both", expand=True)
    
    def get_first_chord(self):
        self.logic.next_chord(self.lang)

    def update_chord_label(self, text):
        self.chord_label.configure(text=text)

    def update_fretboard(self, fingering):
        self.fretboard_middle.draw_chord(fingering)

    def update_learned_label(self, text):
        self.learned_label_left.configure(text=text)

    def update_timer_label(self, text):
        self.timer_display.configure(text=text)

    def set_timer_button_text(self, text):
        self.timer_button.configure(text=text)

    def set_next_chord_button_state(self, state):
        self.next_chord_button.configure(state=state)

    def build_widgets(self):
        self.grid_columnconfigure(0, weight=1, minsize=50)
        self.grid_columnconfigure(1, weight=0, minsize=75)
        self.grid_columnconfigure(2, weight=1, minsize=50)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.chord_label = ctk.CTkLabel(self, text="", font=(config.BASE_FONT, 24))
        self.chord_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.learned_label_left = ctk.CTkLabel(self, text="", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 14))
        self.learned_label_left.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")

        self.fretboard_middle = DefaultFretboard(self)
        self.fretboard_middle.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.dummy_label_right = ctk.CTkLabel(self, text=" ", anchor="nw", wraplength=120, justify="left", font=(config.BASE_FONT, 12))
        self.dummy_label_right.grid(row=1, column=2, padx=5, pady=2, sticky="nsew")

        self.timer_display = ctk.CTkLabel(self, text="", font=(config.BASE_FONT, 14))
        self.timer_display.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttom_frame = ctk.CTkFrame(self)
        self.buttom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.buttons_inner = ctk.CTkFrame(self.buttom_frame)
        self.buttons_inner.pack(anchor="center")

        self.next_chord_button = ctk.CTkButton(self.buttons_inner, text=f"{self.lang['next_chord_button']}", command=lambda: self.logic.next_chord(self.lang))
        self.next_chord_button.pack(side="left", padx=5)

        self.timer_button = ctk.CTkButton(self.buttons_inner, text=f"{self.lang['timer_button_start']}", command=lambda: self.logic.toggle_timer(self.lang))
        self.timer_button.pack(side="left", padx=5)
