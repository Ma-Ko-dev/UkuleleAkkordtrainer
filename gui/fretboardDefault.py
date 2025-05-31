from tkinter import Canvas
import config


class DefaultFretboard(Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='#F3E9D2', **kwargs)
        self.fret_count = 12
        self.string_count = 4
        self.top_padding = 40
        self.circle_radius = 9

        self.left_padding = 0
        self.string_spacing = 0
        self.fret_spacing = 0

        self.bind("<Configure>", self.on_resize)

        self.markers = []
        self.string_names = ["G", "C", "E", "A"]
        # self.draw_base_lines()

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height

        # Fixe String-Spacings, Fretboard-Breite nicht größer als Canvas-Frame
        self.string_spacing = 40
        fretboard_width = self.string_spacing * (self.string_count - 1)
        self.left_padding = (self.width - fretboard_width) / 2
        self.fret_spacing = (self.height - self.top_padding - 20) / (self.fret_count + 1) + 2

        # Falls Canvas größer als fretboard_width: begrenzen
        canvas_width = min(self.width, fretboard_width + 20)  # 20px Puffer
        canvas_height = self.height

        self.config(width=canvas_width, height=canvas_height)
        self.draw_base_lines()


    def draw_base_lines(self):
        self.delete("all")
        # strings (vertical lines) with labels on top
        for i, name in enumerate(self.string_names):
            x = self.left_padding + i * self.string_spacing
            self.create_text(x, self.top_padding - 10, text=name, font=(config.BASE_FONT, 16, "bold"), anchor="s", fill="#3B3B3B")
            self.create_line(x, self.top_padding, x, self.height - 20, fill="#4A4A4A", width=3)

        # frets (horizontal lines)
        for i in range(self.fret_count + 1):
            y = self.top_padding + i * self.fret_spacing
            line_color = "#6B4C3B"
            line_width = 3 if i == 0 else 1  #first fret thicker (nut)
            self.create_line(self.left_padding, y, self.left_padding + self.string_spacing * (self.string_count -1), y, fill=line_color, width=line_width)

    def draw_chord(self, fretboard):
        radius = self.circle_radius
        for m in self.markers:
            self.delete(m)
        self.markers.clear()

        for string_idx, fret in enumerate(fretboard):
            try:
                fret_num = int(fret)
                if 1 <= fret_num <= self.fret_count:
                    x = self.left_padding + string_idx * self.string_spacing
                    y = self.top_padding + fret_num * self.fret_spacing - self.fret_spacing / 2
                    circle = self.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#8B0000")
                    number = self.create_text(x, y, text=str(fret), fill="white", font=(config.BASE_FONT, 10, "bold"))
                    self.markers.extend([circle, number])
            except ValueError:
                continue
