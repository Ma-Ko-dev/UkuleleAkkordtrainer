import customtkinter as ctk
from tkinter import ttk, messagebox
import config
import utils



class ChordEditor(ctk.CTkToplevel):
    style_initialized = False

    def __init__(self, lang):
        super().__init__()
        self.title("Akkord Editor")
        self.geometry("1000x650")


        self.lang = lang
        self.data = utils.load_chords(self.lang, filter_by_difficulty=False)
        self.tables = {}      
        self.config_data = utils.load_config()
        self.mode = self.config_data.get("theme", "dark")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=(10, 0), expand=True, fill="both")

        if self.mode == "dark":
            self.bg_even = "#2e2e2e"
            self.bg_odd = "#3a3a3a"
            self.fg = "#ffffff"
            self.header_bg = "#1e1e1e"
            self.header_fg = "#ffffff"
        else:
            self.bg_even = "#f0f0f0"
            self.bg_odd = "#e0e0e0"
            self.fg = "#000000"
            self.header_bg = "#d0d0d0"
            self.header_fg = "#000000"

        self.style = ttk.Style()
        self.style.theme_use("default")

        if not ChordEditor.style_initialized:
            ChordEditor.style_initialized = True
            self.style.element_create("Custom.Treeheading.border", "from", "default")
            self.style.layout("Custom.Treeview.Heading", [
                ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
                ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeheading.padding", {'sticky': 'nsew', 'children': [
                        ("Custom.Treeheading.image", {'side': 'right', 'sticky': ''}),
                        ("Custom.Treeheading.text", {'sticky': 'we'})
                    ]})
                ]}),
            ])

            self.style.configure("Custom.Treeview",
                                background = self.bg_even,
                                foreground = self.fg,
                                fieldbackground = self.bg_even,
                                rowheight = 25)
            
            self.style.configure("Custom.Treeview.Heading",
                                background = self.header_bg,
                                foreground = self.header_fg,
                                relief = "flat",
                                font = (config.BASE_FONT, 14))
            
            self.style.map("Custom.Treeview.Heading",
                        background = [('active', self.header_bg)],
                        relief = [('active', 'flat'), ('pressed', 'sunken')])
        
        for level in ["easy", "medium", "hard"]:
            tab = self.tabview.add(level.capitalize())
            self.create_table(tab, level)

        self.info_label = ctk.CTkLabel(self, text="Doppelklick auf eine Zelle zum Bearbeiten", anchor="center")
        self.info_label.pack(pady=(5, 0))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.add_button = ctk.CTkButton(self.button_frame, text="Hinzufügen", command=self.add_entry)
        self.add_button.pack(side="left", padx=10)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Löschen", command=self.delete_selected_row)
        self.delete_button.pack(side="left", padx=10)


    def create_table(self, parent, level):
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=("name", "fingering", "fingers", "notes_on_strings", "chord_notes", "intervals"), show="headings", style="Custom.Treeview")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("name", text="Akkordname", anchor="center")
        tree.heading("fingering", text="Griff", anchor="center")
        tree.heading("fingers", text="Fingerempfehlung", anchor="center")
        tree.heading("notes_on_strings", text="Saiten-Noten", anchor="center")
        tree.heading("chord_notes", text="Akkordtöne", anchor="center")
        tree.heading("intervals", text="Intervalle", anchor="center")

        for col in ("name", "fingering", "fingers", "notes_on_strings", "chord_notes", "intervals"):
            tree.column(col, anchor="center", width=100)
        
        tree.tag_configure("evenrow", background=self.bg_even, foreground=self.fg)
        tree.tag_configure("oddrow", background=self.bg_odd, foreground=self.fg)

        for i, chord in enumerate(self.data.get(level, [])):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=(
                chord.get("name", ""),
                chord.get("fingering", ""),
                chord.get("fingers", ""),
                chord.get("notes_on_strings", ""),
                chord.get("chord_notes", ""),
                chord.get("intervals", "")
            ), tags=(tag,))

        self.tables[level] = tree

        tree.bind("<Double-1>", self.on_double_click)


    def on_double_click(self, event):
        if hasattr(self, 'edit_box') and self.edit_box is not None:
            return

        tree = event.widget
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if not row_id or not col:
            return

        x, y, width, height = tree.bbox(row_id, col)
        abs_x = tree.winfo_rootx() - self.winfo_rootx() + x
        abs_y = tree.winfo_rooty() - self.winfo_rooty() + y

        current_value = tree.set(row_id, col)

        self.edit_box = ttk.Entry(self)
        self.edit_box.place(x=abs_x, y=abs_y, width=width, height=height)
        self.edit_box.insert(0, current_value)
        self.edit_box.focus()

        def save_edit(event=None):
            new_value = self.edit_box.get()
            tree.set(row_id, col, new_value)
            self.edit_box.destroy()
            self.edit_box = None

        self.edit_box.bind("<FocusOut>", save_edit)
        self.edit_box.bind("<Return>", save_edit)

    
    def add_entry(self):
        current_tab = self.tabview.get().lower()
        tree = self.tables.get(current_tab)
        if tree:
            default_values = [
            "Neuer Akkord",    
            "Bearbeiten...",   
            "???",               
            "???",               
            "???",                
            "???"                 
            ]
            index = len(tree.get_children())
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.insert("", "end", values=default_values, tags=(tag,))


    def delete_selected_row(self):
        current_tab = self.tabview.get().lower()
        tree = self.tables.get(current_tab)
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Keine Auswahl", "Bitte wähle eine Zeile zum Löschen aus.")
            return

        for item in selected:
            tree.delete(item)

        # print(f"{len(selected)} Zeile(n) gelöscht im Tab '{current_tab}'.")
