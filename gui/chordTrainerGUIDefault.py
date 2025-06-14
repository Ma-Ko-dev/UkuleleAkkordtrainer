import customtkinter as ctk
import config
from gui.fretboardDefault import DefaultFretboard
from gui.guiLogicManager import GuiLogicManager


class DefaultChordTrainerGUI(ctk.CTkFrame):

    def __init__(self, master, chords, lang):
        super().__init__(master)
        self.chords = chords
        self.lang = lang
        self.modes = [
            f"{self.lang['trainer_mode_random']}", 
            f"{self.lang['trainer_mode_song']}", 
            f"{self.lang['trainer_mode_twitch']}"
            ]
        self.mode_var = ctk.StringVar(value=f"{self.lang['trainer_mode_random']}")

        self.build_widgets()
        self.logic = GuiLogicManager(self, chords, lang)

        self.pack(fill="both", expand=True)

        # debug
        # def zeige_breite():
        #     print(self.left_frame.winfo_width())
        #     print(self.fretboard_frame.winfo_width())
        #     print(self.right_frame.winfo_width())
        # self.after(100, zeige_breite)
    
    def get_first_chord(self):
        self.logic.next_chord(self.lang)

    def update_chord_label(self, text):
        self.current_chord.configure(text=text)

    def update_fretboard(self, fingering):
        self.fretboard_middle.draw_chord(fingering)

    def update_learned_label(self, text):
        self.learned_label.configure(text=text)

    def update_timer_label(self, text):
        self.timer_display.configure(text=text)

    def set_timer_button_text(self, text):
        self.timer_button.configure(text=text)

    def set_next_chord_button_state(self, state):
        self.next_chord_button.configure(state=state)

    def update_theme(self):
        self.fretboard_middle.update_theme()

    def update_previous_chords(self):
        self.chord_history.configure(text=f"{self.lang['chord_history']}\n" + " ".join(config.PAST_CHORDS))

    def update_interval(self, chord):
        chord_obj = next((c for c in self.chords if c["name"].lower() == chord.lower()), None)
        if chord_obj:
            intervals = chord_obj.get("intervals", [])
            self.chord_interval.configure(text=f"{self.lang['chord_interval']} {'-'.join(intervals)}")
        else:
            self.chord_interval.configure(text=f"{self.lang['error_intervals']}")

    def update_chord_tones(self, chord):
        chord_obj = next((c for c in self.chords if c["name"].lower() == chord.lower()), None)
        if chord_obj:
            tones = chord_obj.get("chord_notes", [])
            self.chord_tones.configure(text=f"{self.lang['chord_notes']} {'-'.join(tones)}")
        else:
            self.chord_tones.configure(text=f"{self.lang['error_notes']}")


    def build_widgets(self):
        # outer frame
        self.outer_frame = ctk.CTkFrame(self, border_width=3, corner_radius=16)
        self.outer_frame.pack(expand=True, fill="both", pady=10, padx=10)


        # second inner frame, inside of outer frame
        self.middle_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10)
        self.middle_frame.pack(fill="both", expand=True, padx=10, pady=(10, 2))
        self.middle_frame.grid_columnconfigure(0, weight=1, minsize=200)
        self.middle_frame.grid_columnconfigure(1, weight=0, minsize=200)
        self.middle_frame.grid_columnconfigure(2, weight=1, minsize=200)


        # left frame of second inner frame
        self.left_frame = ctk.CTkFrame(self.middle_frame, border_width=1, corner_radius=5)
        self.left_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.left_frame.grid_propagate(True)

        # chord info and theory frame
        self.chord_info_frame = ctk.CTkFrame(self.left_frame, border_width=1, corner_radius=5)
        self.chord_info_frame.pack(fill="x", padx=5, pady=5)

        self.current_chord_label = ctk.CTkLabel(self.chord_info_frame, text=f"{self.lang['current_chord']}", font=(config.BASE_FONT, 18, "underline"))
        self.current_chord_label.pack(expand=True, pady=5)

        self.current_chord = ctk.CTkLabel(self.chord_info_frame, text="", font=(config.BASE_FONT, 16, "bold"))
        self.current_chord.pack(expand=True)

        self.chord_interval = ctk.CTkLabel(self.chord_info_frame, text="", font=(config.BASE_FONT, 16))
        self.chord_interval.pack(expand=True)

        self.chord_tones = ctk.CTkLabel(self.chord_info_frame, text="", font=(config.BASE_FONT, 16))
        self.chord_tones.pack(expand=True, pady=(0, 5))

        # chord stats frame
        self.chord_stats_frame = ctk.CTkFrame(self.left_frame, border_width=1, corner_radius=5)
        self.chord_stats_frame.pack(fill="x", padx=5, pady=5)

        self.chord_stats_label = ctk.CTkLabel(self.chord_stats_frame, text=f"{self.lang['chord_statistics']}", font=(config.BASE_FONT, 18, "underline"))
        self.chord_stats_label.pack(expand=True, pady=5)

        self.learned_label = ctk.CTkLabel(self.chord_stats_frame, text="", wraplength=170, font=(config.BASE_FONT, 16))
        self.learned_label.pack(expand=True, pady=5)

        self.chord_history = ctk.CTkLabel(self.chord_stats_frame, text="", wraplength=180, font=(config.BASE_FONT, 16))
        self.chord_history.pack(expand=True, pady=(5, 10))

        # maybe add chord info like "did you know?" somewhere

        # middle frame of second inner frame (fretboard)
        self.fretboard_frame = ctk.CTkFrame(self.middle_frame, fg_color="transparent", width=200)
        self.fretboard_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        self.fretboard_middle = DefaultFretboard(self.fretboard_frame)
        self.fretboard_middle.pack(anchor="center", expand=False)

        # right frame of second inner frame
        self.right_frame = ctk.CTkFrame(self.middle_frame, border_width=1, corner_radius=5)
        self.right_frame.grid(row=0, column=2, sticky="new", padx=10, pady=10)
        self.right_frame.grid_propagate(True)    

        # quick settings frame
        self.display_settings_frame = ctk.CTkFrame(self.right_frame, border_width=1, corner_radius=5)
        self.display_settings_frame.pack(fill="x", padx=5, pady=5)

        self.display_settings_label = ctk.CTkLabel(self.display_settings_frame, text=f"{self.lang['chord_display_headline']}", font=(config.BASE_FONT, 18, "underline"))
        self.display_settings_label.pack(expand=True, pady=5)

        self.fingering_setting_label = ctk.CTkLabel(self.display_settings_frame, text=f"{self.lang['chord_display_setting']}", font=(config.BASE_FONT, 16, "underline"))
        self.fingering_setting_label.pack(expand=True, pady=(5, 0))

        self.fingering_setting = ctk.CTkSegmentedButton(self.display_settings_frame, values=[f"{self.lang['chord_setting_frets']}", f"{self.lang['chord_setting_fingering']}"], font=(config.BASE_FONT, 16), state="disabled")
        self.fingering_setting.set(f"{self.lang['chord_setting_frets']}")
        self.fingering_setting.pack(expand=True, pady=(0, 5))

        self.left_hand_display = ctk.CTkLabel(self.display_settings_frame, text=f"{self.lang['chord_hand_preference']}", font=(config.BASE_FONT, 16, "underline"))
        self.left_hand_display.pack(expand=True, pady=5)

        self.left_hand_setting = ctk.CTkSegmentedButton(self.display_settings_frame, values=[f"{self.lang['chord_hand_left']}", f"{self.lang['chord_hand_right']}"], font=(config.BASE_FONT, 16), state="disabled")
        self.left_hand_setting.set(f"{self.lang['chord_hand_right']}")
        self.left_hand_setting.pack(expand=True, padx=10, pady=(0, 10))

        # learnmode frame
        self.mode_frame = ctk.CTkFrame(self.right_frame, border_width=1, corner_radius=5)
        self.mode_frame.pack(fill="x", padx=5, pady=5)

        self.mode_label = ctk.CTkLabel(self.mode_frame, text=f"{self.lang['trainer_learnmode']}", font=(config.BASE_FONT, 18, "underline"))
        self.mode_label.pack(expand=True, pady=5)

        for index, mode in enumerate(self.modes):
            pady = (2, 10) if index == len(self.modes) - 1 else (2, 2)
            rb = ctk.CTkRadioButton(self.mode_frame, text=mode, variable=self.mode_var, value=mode, radiobutton_width=18, radiobutton_height=18, state="disabled")
            rb.pack(anchor="w", padx=10, pady=pady)

        # controls frame
        self.control_frame = ctk.CTkFrame(self.right_frame, border_width=1, corner_radius=5)
        self.control_frame.pack(fill="x", padx=5, pady=5)

        self.controls_label = ctk.CTkLabel(self.control_frame, text=f"{self.lang['trainer_controls']}", font=(config.BASE_FONT, 18, "underline"))
        self.controls_label.pack(expand=True, pady=5)

        self.next_chord_button = ctk.CTkButton(
            self.control_frame, text=f"{self.lang['next_chord_button']}", 
            font=(config.BASE_FONT, 14), 
            command=lambda: self.logic.next_chord(self.lang))
        self.next_chord_button.pack(pady=(5, 2))

        self.prev_chord = ctk.CTkButton(self.control_frame, text=f"{self.lang['previous_chord_button']}", font=(config.BASE_FONT, 14), state="disabled")
        self.prev_chord.pack(pady=2)

        self.timer_button = ctk.CTkButton(
            self.control_frame, text=f"{self.lang['timer_button_start']}", 
            font=(config.BASE_FONT, 14), 
            command=lambda: self.logic.toggle_timer(self.lang))
        self.timer_button.pack(pady=(2, 10))


        # third inner frame, inside of outer frame
        self.buttom_frame = ctk.CTkFrame(self.outer_frame, border_width=2, corner_radius=10, height=50)
        self.buttom_frame.pack(fill="x", padx=10, pady=(5, 10))
        self.buttom_frame.pack_propagate(False)
        self.timer_display = ctk.CTkLabel(self.buttom_frame, text="", font=(config.BASE_FONT, 16))
        self.timer_display.pack(expand=True)
