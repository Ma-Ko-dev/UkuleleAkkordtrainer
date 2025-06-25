import customtkinter as ctk
from tkinter import ttk, messagebox
from gui.editorLogicManager import ChordEditorLogic
import config
import utils
import json
import re



class ChordEditor(ctk.CTkToplevel):
    style_initialized = False
    def __init__(self, lang, master=None, on_close=None):
        super().__init__(master)
        self.lang = lang
        self.logic = ChordEditorLogic(self.lang)
        self.on_close = on_close
        self.title(f"{self.lang['editor_title']}")
        self.geometry("1000x650")

        self.is_dirty = False # just to make sure "no changes" are saved to the file later
        self.saved = False
        self.data = utils.load_chords(self.lang, filter_by_difficulty=False)
        self.tables = {}      
        self.config_data = utils.load_config()
        self.mode = self.config_data.get("theme", "dark")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=(10, 0), expand=True, fill="both")

        # TODO think about theme handling
        # Define colors for dark/light mode
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

        # Style initialization for ttk.Treeview
        self.style = ttk.Style()
        self.style.theme_use("default")

        if not ChordEditor.style_initialized:
            ChordEditor.style_initialized = True

            # Define custom header layout for Treeview
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
                                rowheight = 25,
                                font=(config.BASE_FONT, 12,))
            
            self.style.configure("Custom.Treeview.Heading",
                                background = self.header_bg,
                                foreground = self.header_fg,
                                relief = "flat",
                                font = (config.BASE_FONT, 13, "bold"))
            
            self.style.map("Custom.Treeview.Heading",
                        background = [('active', self.header_bg)],
                        relief = [('active', 'flat'), ('pressed', 'sunken')])
        
        # levels with translations
        levels = [
            ("easy", self.lang["difficulty_easy"]),
            ("medium", self.lang["difficulty_medium"]),
            ("hard", self.lang["difficulty_hard"]),
        ]

        # Create tabs for each difficulty level
        self.tab_name_to_level = {}
        for level_key, display_name in levels:
            tab = self.tabview.add(display_name)
            self.tab_name_to_level[display_name] = level_key
            self.create_table(tab, level_key)

        # Info label at the bottom
        self.info_label = ctk.CTkLabel(self, text=f"{self.lang['editor_info_text']}", anchor="center", font=(config.BASE_FONT, 16))
        self.info_label.pack(pady=(5, 0))

        # Button row
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.add_button = ctk.CTkButton(self.button_frame, text=f"{self.lang['editor_button_add']}", command=self.add_entry)
        self.add_button.pack(side="left", padx=10)

        self.delete_button = ctk.CTkButton(self.button_frame, text=f"{self.lang['editor_button_delete']}", command=self.delete_selected_row)
        self.delete_button.pack(side="left", padx=10)

        self.save_button = ctk.CTkButton(self.button_frame, text=f"{self.lang['editor_button_save']}", command=self.save_changes, state="disabled")
        self.save_button.pack(side="left", padx=10)

        self.reset_button = ctk.CTkButton(self.button_frame, text=f"{self.lang['editor_button_reset']}", command=self.reset_tables, state="disabled")
        self.reset_button.pack(side="left", padx=10)

        self.transient(self.master)  # makes this window associated with the main window (optional but clean)
        self.grab_set()              # blocks interaction with other windows (makes this window modal)
        self.focus_force()           # actively sets focus to this window

        self.protocol("WM_DELETE_WINDOW", self._on_close)


    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()

        
    def create_table(self, parent, level):
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(
            tree_frame,
            columns=("name", "fingering", "fingers", "notes_on_strings", "chord_notes", "intervals"),
            show="headings",
            style="Custom.Treeview"
        )
        tree.pack(side="left", fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Header labels
        tree.heading("name", text=f"{self.lang['editor_chordname']}", anchor="center")
        tree.heading("fingering", text=f"{self.lang['editor_fingering']}", anchor="center")
        tree.heading("fingers", text=f"{self.lang['editor_fingers']}", anchor="center")
        tree.heading("notes_on_strings", text=f"{self.lang['editor_notes_on_strings']}", anchor="center")
        tree.heading("chord_notes", text=f"{self.lang['editor_chord_notes']}", anchor="center")
        tree.heading("intervals", text=f"{self.lang['editor_interval']}", anchor="center")

        # Define column properties
        for col in tree["columns"]:
            tree.column(col, anchor="center", width=100)
        
        # Tag rows for alternating background color
        tree.tag_configure("evenrow", background=self.bg_even, foreground=self.fg)
        tree.tag_configure("oddrow", background=self.bg_odd, foreground=self.fg)

        # Fill table with data
        for i, chord in enumerate(self.data.get(level, [])):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.insert("", "end", values=self.format_chord_for_display(chord), tags=(tag,))
        self.tables[level] = tree

        # Bind double-click to start editing
        tree.bind("<Double-1>", self.on_double_click)


    def format_chord_for_display(self, chord):
        def to_display(value):
            return ", ".join(value) if isinstance(value, list) else value or ""

        return (
            chord.get("name", ""),
            to_display(chord.get("fingering", [])),
            to_display(chord.get("fingers", [])),
            to_display(chord.get("notes_on_strings", [])),
            to_display(chord.get("chord_notes", [])),
            to_display(chord.get("intervals", []))
        )


    def on_double_click(self, event):
        # If already editing, ignore new click
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

        # Get absolute position of clicked cell
        x, y, width, height = tree.bbox(row_id, col)
        abs_x = tree.winfo_rootx() - self.winfo_rootx() + x
        abs_y = tree.winfo_rooty() - self.winfo_rooty() + y

        current_value = tree.set(row_id, col)

        # Create entry box in place
        self.edit_box = ttk.Entry(self)
        self.edit_box.place(x=abs_x, y=abs_y, width=width, height=height)
        self.edit_box.insert(0, current_value)
        self.edit_box.focus()

        # Save on return, focus out or tab
        # TODO save_edit is defined two times. here and in tab_to_next_cell - refactor that
        def save_edit(event=None):
            new_value = self.edit_box.get()
            old_value = tree.set(row_id, col)
            if new_value != old_value:
                tree.set(row_id, col, new_value)
                self.is_dirty = True
                self.update_buttons_state()
            self.edit_box.destroy()
            self.edit_box = None

        self.edit_box.bind("<FocusOut>", save_edit)
        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<Tab>", lambda e: self.tab_to_next_cell(tree, row_id, col, e))


    def add_entry(self):
        current_tab_name = self.tabview.get()
        current_tab = self.tab_name_to_level.get(current_tab_name)
        tree = self.tables.get(current_tab)
        if tree:
            default_values = [
                f"{self.lang['editor_placeholder1']}",    # placeholder chord name
                f"{self.lang['editor_placeholder2']}",  # editable fingering field
                "???",            # unknown finger suggestion
                "???",            # unknown notes on strings
                "???",            # unknown chord tones
                "???"             # unknown intervals
            ]
            index = len(tree.get_children())
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.insert("", "end", values=default_values, tags=(tag,))
            self.is_dirty = True  
            self.update_buttons_state()


    def json_dumps_compact_lists(self, data):
        text = json.dumps(data, ensure_ascii=False, indent=4)
        pattern = re.compile(r'\[\s*(\".*?\"(?:,\s*\".*?\")*)\s*\]', re.DOTALL)

        def replacer(match):
            content = match.group(1)
            compact = content.replace('\n', '').replace(' ', '')
            return f'[{compact}]'

        return pattern.sub(replacer, text)


    def save_changes(self):
        if not self.is_dirty:
            return

        errors = self.logic.validate_treeviews(self.tables)
        if errors > 0:
            messagebox.showerror(
                self.lang["error_editor_validation_title"],
                self.lang["error_editor_validation_message"].format(errors=errors), 
                parent=self
            )
            return

        data = self.logic.prepare_save_data(self.tables)
        success, error = self.logic.save_data(data)

        if success:
            self.is_dirty = False
            self.saved = True
            self.update_buttons_state()
            messagebox.showinfo(
                self.lang["editor_button_save"],
                self.lang["editor_save_success_message"],
                parent=self
            )
        else:
            self.saved = False
            print(self.lang["error_editor_saving"])
            print(error)


    def reset_tables(self):
        # Reset all tables to initial loaded data state
        for level, tree in self.tables.items():
            tree.delete(*tree.get_children())  # Clear all rows

            for i, chord in enumerate(self.data.get(level, [])):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                tree.insert("", "end", values=self.format_chord_for_display(chord), tags=(tag,))
        self.is_dirty = False
        self.update_buttons_state()


    def delete_selected_row(self):
        current_tab_name = self.tabview.get()
        current_tab = self.tab_name_to_level.get(current_tab_name)
        tree = self.tables.get(current_tab)
        if not tree:
            print(self.lang["error_editor_no_treeview_for_tab"].format(tab_name=current_tab_name))
            return

        selected = tree.selection()
        if not selected:
            messagebox.showinfo(f"{self.lang['error_editor_no_selection_title']}", 
                                f"{self.lang['error_editor_no_selection_message']}", 
                                parent=self)
            return

        confirm = messagebox.askyesno(f"{self.lang['editor_confirm_delete_title']}",
                                    f"{self.lang['editor_confirm_delete_message']}",
                                    parent=self)
        if not confirm:
            return

        for item in selected:
            tree.delete(item)

        # Re-tag remaining rows to fix alternating colors
        for i, item in enumerate(tree.get_children()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.item(item, tags=(tag,))
        
        self.is_dirty = True
        self.update_buttons_state()


    def tab_to_next_cell(self, tree, row_id, col, event=None):
        col_index = int(col[1:]) - 1  # '#1' → 0
        columns = tree["columns"]

        # Save current value
        new_value = self.edit_box.get()
        tree.set(row_id, col, new_value)
        self.edit_box.destroy()
        self.edit_box = None

        # Determine next column
        next_index = col_index + 1
        if next_index >= len(columns):
            return "break"  # no more columns

        next_col = f"#{next_index + 1}"
        x, y, width, height = tree.bbox(row_id, next_col)
        if not width:
            return "break"  # invalid cell

        # Create new entry box at next cell
        current_value = tree.set(row_id, next_col)

        self.edit_box = ttk.Entry(self)
        abs_x = tree.winfo_rootx() - self.winfo_rootx() + x
        abs_y = tree.winfo_rooty() - self.winfo_rooty() + y
        self.edit_box.place(x=abs_x, y=abs_y, width=width, height=height)
        self.edit_box.insert(0, current_value)
        self.edit_box.focus()

        # Bind again for the next cell
        def save_edit(event=None):
            new_value = self.edit_box.get()
            old_value = tree.set(row_id, col)
            if new_value != old_value:
                tree.set(row_id, next_col, new_value)
                self.is_dirty = True
                self.update_buttons_state()
            self.edit_box.destroy()
            self.edit_box = None

        self.edit_box.bind("<FocusOut>", save_edit)
        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<Tab>", lambda e: self.tab_to_next_cell(tree, row_id, next_col, e))

        return "break"

    def update_buttons_state(self):
        if self.is_dirty:
            self.reset_button.configure(state="normal")
            self.save_button.configure(state="normal")
        else:
            self.reset_button.configure(state="disabled")
            self.save_button.configure(state="disabled")
