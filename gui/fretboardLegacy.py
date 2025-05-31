from tkinter import Canvas
import config


class LegacyFretboard(Canvas):
    def __init__(self, master, width=800, height=200, **kwargs):
        self.string_label_width = 40
        super().__init__(master, width=width + self.string_label_width, height=height, bg='#F3E9D2', **kwargs)  # light wood
        self.fret_count = 12
        self.string_count = 4
        self.fret_spacing = width / self.fret_count
        self.string_spacing = height / (self.string_count + 1)
        self.markers = []
        self.string_names = ["G", "C", "E", "A"]
        self.draw_base_lines()

    def draw_base_lines(self):
        self.delete("all")
        # Stringnames left
        for i, name in enumerate(self.string_names):
            y = (i + 1) * self.string_spacing
            self.create_text(12, y, text=name, font=(config.BASE_FONT, 16, "bold"), anchor="w", fill="#3B3B3B")

        # Frets (vertical) - brown, realistic like metal rods
        for i in range(self.fret_count + 1):
            x = self.string_label_width + i * self.fret_spacing
            line_color = "#6B4C3B"  # dunkles braun
            line_style = (2, 4) if i != 0 else None
            line_width = 3 if i == 0 else 1
            self.create_line(x, 0, x, self.winfo_reqheight(), fill=line_color, dash=line_style, width=line_width)

        # Strings (horizontal) - dark gray, slightly thicker for a realistic feel
        for i in range(1, self.string_count + 1):
            y = i * self.string_spacing
            start_x = self.string_label_width
            end_x = self.string_label_width + self.fret_spacing * self.fret_count
            self.create_line(start_x, y, end_x, y, fill="#4A4A4A", width=3)

    def draw_chord(self, fretboard):
        for m in self.markers:
            self.delete(m)
        self.markers.clear()

        for string_idx, fret in enumerate(fretboard):
            try:
                fret_num = int(fret)
                if 1 <= fret_num <= self.fret_count:
                    x = self.string_label_width + self.fret_spacing * (fret_num - 0.5)
                    y = (string_idx + 1) * self.string_spacing
                    circle = self.create_oval(x - 12, y - 12, x + 12, y + 12, fill="#8B0000") 
                    number = self.create_text(x, y, text=str(fret), fill="white", font=(config.BASE_FONT, 12, "bold"))
                    self.markers.extend([circle, number])
            except ValueError:
                continue
