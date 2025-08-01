import customtkinter as ctk
import config
from PIL import Image, ImageTk

class DefaultFretboard(ctk.CTkCanvas):
    """
    A visual representation of a ukulele fretboard using CustomTkinter Canvas.

    Draws the fretboard background, strings, frets, and chord positions.
    Allows redrawing based on theme or window resize.
    """
    def __init__(self, master, **kwargs):
        """
        Initialize the fretboard canvas, calculate size and draw initial layout.

        Args:
            master (tk.Widget): Parent widget.
            **kwargs: Additional arguments passed to CTkCanvas.
        """

        self.frets = 12
        self.strings = 4
        self.fret_width = 45
        self.string_height = 45
        self.marker_radius = 13
        self.fingering = []
        self.fingers = []
        self.string_names = ["G", "C", "E", "A"]

        width = self.fret_width * self.strings + 60
        height = self.string_height * self.frets + 60

        theme_mode = ctk.get_appearance_mode()
        color_list = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        background = color_list[1] if theme_mode == "Dark" else color_list[0]

        super().__init__(master, width=width, height=height, bg=background, highlightthickness=0, **kwargs)

        self.canvas_width = width
        self.canvas_height = height
        self.padding_x = (self.canvas_width - (self.fret_width * (self.strings - 1))) // 2
        self.padding_y = 30
        self.markers = []

        self.draw_fretboard()
        self.draw_string_names()
        # self.bind("<Configure>", self.on_resize)

    def update_theme(self):
        """
        Redraws the entire fretboard to reflect the current color theme.
        """
        theme_mode = ctk.get_appearance_mode()
        color_list = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        background = color_list[1] if theme_mode == "Dark" else color_list[0]
        self.configure(bg=background)
        self.delete("all")
        self.draw_fretboard()
        self.draw_string_names()
        self.draw_chord(self.fingering, self.fingers)

    def on_resize(self, event):
        """
        Adjusts canvas size and redraws when the widget is resized.

        Args:
            event: Tkinter event with new width and height.
        """
        min_width = self.fret_width * (self.strings - 1) + 60
        min_height = self.string_height * self.frets + 60

        new_width = max(event.width, min_width)
        new_height = max(event.height, min_height)

        self.config(width=new_width, height=new_height)

        self.canvas_width = new_width
        self.canvas_height = new_height

        self.redraw()


    def redraw(self):
        """
        Clears and redraws the entire fretboard, including strings and current chord.
        """
        self.delete("all")

        self.padding_x = (self.canvas_width - (self.fret_width * (self.strings - 1))) // 2
        self.padding_y = 30

        self.draw_fretboard()
        self.draw_string_names()
        self.draw_chord(self.fingering, self.fingers)


    def draw_fretboard(self):
        """
        Draws the fretboard background (wood texture or fallback), frets and strings.
        """
        board_width = self.fret_width * (self.strings - 1)
        board_height = self.string_height * self.frets

        try:
            image = Image.open(config.TEXTURE_PATH).resize((board_width, board_height))
            self.wood_texture = ImageTk.PhotoImage(image)
            self.create_image(
                self.padding_x,
                self.padding_y,
                image=self.wood_texture,
                anchor="nw"
            )
        except Exception as e:
            print("Fehler beim Laden der Textur:", e)
            self.create_rectangle(
                self.padding_x,
                self.padding_y,
                self.padding_x + board_width,
                self.padding_y + board_height,
                fill="#5a381e",  # fallback-farbe
                outline=""
            )

        for i in range(self.frets + 1):
            y = self.padding_y + i * self.string_height
            start_x = self.padding_x - 1 if i == 0 else self.padding_x
            end_x = self.padding_x + board_width + 2 if i == 0 else self.padding_x + board_width
            self.create_line(
                start_x,
                y,
                end_x,
                y,
                width=6 if i == 0 else 1,
                fill="silver"
            )

        for i in range(self.strings):
            x = self.padding_x + i * self.fret_width
            self.create_line(
                x,
                self.padding_y,
                x,
                self.padding_y + board_height,
                width=3,
                fill="#e6d4b6"
            )

    def draw_string_names(self):
        """
        Draws the note names of the strings above the fretboard (G, C, E, A).
        Automatically mirrors for left-handed mode.
        """
        string_names = self.string_names
        if config.PREFERED_HAND == "left":
            string_names = self.string_names[::-1]
        y = self.padding_y - 15

        for i, name in enumerate(string_names):
            x = self.padding_x + i * self.fret_width
            self.create_text(
                x,
                y,
                text=name,
                fill="white",
                font=("Arial", 12, "bold")
            )

    def draw_chord(self, fingering, fingers):
        """
        Draws markers for chord fingering on the fretboard.

        Args:
            fingering (list): Fret positions per string (as strings).
            fingers (list): Corresponding finger numbers (as strings).
        """
        self.fingering = fingering
        self.fingers = fingers
        r = self.marker_radius
        num_strings = len(fingering)

        for marker in self.markers:
            self.delete(marker)
        self.markers.clear()

        for string_index, fret_str in enumerate(fingering):
            try:
                fret = int(fret_str)
                finger = int(fingers[string_index])
            except ValueError:
                continue
            if fret == 0:
                continue
            if 1 <= fret <= self.frets:
                draw_index = (
                num_strings - 1 - string_index
                if config.PREFERED_HAND == "left"
                else string_index
                )
                x = self.padding_x + draw_index * self.fret_width
                y = self.padding_y + (fret - 1) * self.string_height + self.string_height / 2

                circle = self.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill="green", outline=""
                )

                if config.CHORD_DISPLAY_SETTING == "frets":
                    label = str(fret)
                elif config.CHORD_DISPLAY_SETTING == "fingers":
                    label = str(finger) if finger > 0 else ""
                else:
                    label = "?"

                text = self.create_text(x, y, text=label, fill="white", font=("Arial", 10, "bold"))
                self.markers.extend([circle, text])

