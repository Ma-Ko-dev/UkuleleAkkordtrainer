import customtkinter as ctk
import config
from utils import load_chords



class ChordEditor(ctk.CTkToplevel):
    def __init__(self, lang):
        super().__init__()
        self.title("Akkord Editor")
        self.geometry("1000x550")

        self.lang = lang
        self.data = load_chords(self.lang, filter_by_difficulty=False)
        self.tables = {}      

        self.tabview = ctk.CTkTabview(self, width=950, height=450)
        self.tabview.pack(padx=10, pady=10, expand=True, fill="both")

        for level in ["easy", "medium", "hard"]:
            self.create_table(level)

    def create_table(self, level):
        tab = self.tabview.add(level.capitalize())

        scroll_frame = ctk.CTkScrollableFrame(tab, width=930, height=420)
        scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        content_frame = ctk.CTkFrame(scroll_frame)
        content_frame.pack(pady=10)

        headers = ["Name", "Fret", "Fingering", "Notes of String", "Chord Notes", "Intervals", "Aktion"]

        # Header-Zeile
        for col, text in enumerate(headers):
            header = ctk.CTkLabel(
                content_frame,
                text=text,
                font=(config.BASE_FONT, 16, "bold"),
                text_color="white",
                fg_color="#444444",
                anchor="center",
                corner_radius=0,
                padx=6,
                pady=3
            )
            header.grid(row=0, column=col, sticky="nsew")
            content_frame.grid_columnconfigure(col, weight=1, uniform="spalten")

        for row_idx, chord in enumerate(self.data.get(level, []), start=1):
            bg_color = "#333333" if row_idx % 2 == 0 else "#2a2a2a"

            fields = [
                chord.get("name", ""),
                ",".join(chord.get("fingering", [])),
                ",".join(chord.get("fingers", [])),
                ",".join(chord.get("notes_on_strings", [])),
                ",".join(chord.get("chord_notes", [])),
                ",".join(chord.get("intervals", [])),
                "..."  # Placeholder
            ]

            for col_idx, value in enumerate(fields):
                label = ctk.CTkLabel(
                    content_frame,
                    text=value,
                    text_color="white",
                    fg_color=bg_color,
                    anchor="center",
                    font=(config.BASE_FONT, 16),
                    corner_radius=0,
                    padx=6,
                    pady=3
                )
                label.grid(row=row_idx, column=col_idx, sticky="nsew")

            
