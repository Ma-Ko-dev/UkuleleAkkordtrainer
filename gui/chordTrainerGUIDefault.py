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
        self.top_label.configure(text=text)

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
        # outer frame
        self.outer_frame = ctk.CTkFrame(self, border_width=3, corner_radius=16)
        self.outer_frame.pack(expand=True, fill="both", pady=10, padx=10)

        # first inner frame, inside of outer frame
        self.top_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10)
        self.top_frame.pack(fill="x", padx=10, pady=10)
        self.top_label = ctk.CTkLabel(self.top_frame, text="", font=(config.BASE_FONT, 24))
        self.top_label.pack(pady=5)

        # second inner frame, inside outer frame
        self.middle_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10)
        self.middle_frame.pack(fill="both", expand=True, padx=10)
        self.middle_frame.grid_columnconfigure(0, weight=1, minsize=200)
        self.middle_frame.grid_columnconfigure(1, weight=1, minsize=200)
        self.middle_frame.grid_columnconfigure(2, weight=1, minsize=200)

        # left frame of second inner frame
        self.left_frame = ctk.CTkFrame(self.middle_frame, border_width=1, corner_radius=5)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame_frame1 = ctk.CTkFrame(self.left_frame, border_width=1, corner_radius=5)
        self.left_frame_frame1.pack(fill="x", padx=5, pady=10)
        self.learned_label_left = ctk.CTkLabel(self.left_frame_frame1, text="", wraplength=180, font=(config.BASE_FONT, 16))
        self.learned_label_left.pack(pady=5)
        # middle frame of second inner frame (fretboard)
        self.fretboard_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent")
        self.fretboard_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        self.fretboard_middle = DefaultFretboard(self.fretboard_frame)
        self.fretboard_middle.pack(fill="both", expand=True, padx=5, pady=5)
        # right frame of second inner frame
        self.right_frame = ctk.CTkFrame(self.middle_frame, border_width=1, corner_radius=5)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.dummy_label_right = ctk.CTkLabel(self.right_frame, text=" ", anchor="nw", justify="left", font=(config.BASE_FONT, 14))
        self.dummy_label_right.pack(pady=5)

        # third inner frame, inside outer frame
        self.buttom_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10)
        self.buttom_frame.pack(fill="x", padx=10, pady=5)
        self.timer_display = ctk.CTkLabel(self.buttom_frame, text="", font=(config.BASE_FONT, 16))
        self.timer_display.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10)
        self.button_frame.pack(fill="both", padx=10, pady=10)
        self.buttons_inner = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.buttons_inner.pack(pady=10)
        self.next_chord_button = ctk.CTkButton(self.buttons_inner, text=f"{self.lang['next_chord_button']}", command=lambda: self.logic.next_chord(self.lang))
        self.next_chord_button.pack(side="left", padx=10, pady=5)
        self.timer_button = ctk.CTkButton(self.buttons_inner, text=f"{self.lang['timer_button_start']}", command=lambda: self.logic.toggle_timer(self.lang))
        self.timer_button.pack(side="left", padx=10, pady=5)


