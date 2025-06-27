from tkinter import ttk, messagebox
from gui.editorLogicManager import ChordEditorLogic
from version import __VERSION__
import customtkinter as ctk
import config
import utils



class ChordEditor(ctk.CTkToplevel):
    """
    A modal editor window for managing ukulele chord data grouped by difficulty levels.

    This GUI allows users to:
    - View, add, edit, or delete chord entries across difficulty tabs (easy, medium, hard)
    - Inline-edit table cells with tab and shift-tab navigation
    - Save changes to disk with validation
    - Reset changes to the initially loaded state
    - Be prompted to save changes on close if unsaved modifications exist

    Attributes:
        lang (dict): Dictionary with localized strings.
        logic (ChordEditorLogic): Logic handler for data operations.
        on_close (callable): Optional callback executed when the window is closed.
        is_dirty (bool): Tracks if there are unsaved changes in the current session.
        saved (bool): Indicates whether the last save attempt was successful.
        data (dict): Raw chord data grouped by difficulty level.
        tables (dict): Maps difficulty levels to their corresponding Treeview widgets.
        tab_name_to_level (dict): Maps tab titles to internal level keys (e.g., 'easy').
        config_data (dict): The loaded configuration, e.g., theme settings.
        mode (str): Current theme mode ('light' or 'dark').
        edit_box (ttk.Entry | None): Currently active inline editing widget, if any.
        tabview (CTkTabview): Main container holding difficulty-specific tables.
        info_label (CTkLabel): Info label displayed below the tab view.
        add_button, delete_button, save_button, reset_button (CTkButton): Editor control buttons.
        button_frame (CTkFrame): Frame holding the action buttons.
        bg_even, bg_odd (str): Background colors for even/odd rows depending on the theme.
        fg, header_bg, header_fg (str): Theme-related foreground/background colors.
        style (ttk.Style): Custom style applied to Treeview widgets.
        style_initialized (bool): Class-level flag to initialize Treeview style only once.
    """

    style_initialized = False
    def __init__(self, lang, master=None, on_close=None):
        super().__init__(master)
        self.lang = lang
        self.logic = ChordEditorLogic(self.lang)
        self.edit_box = None
        self.on_close = on_close
        self.title(f"{lang['title']} - {lang['info_version'].format(version=__VERSION__)} - {self.lang['editor_title']}")
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
        """Handle window close event with optional save confirmation if unsaved changes exist."""
        if self.is_dirty:
            confirm = messagebox.askyesnocancel(
                self.lang["editor_confirm_close_title"],
                self.lang["editor_confirm_close_message"],
                parent=self
            )
            # Yes = save and close, No = close without saving, Cancel = abort closing
            if confirm is None:
                return   # Cancel: keep the window open
            elif confirm:  # Yes: save
                self.save_changes()
                if self.is_dirty:  # if saving fails, abort closing
                    return
            # else: No (do not save) - just close

        if self.on_close:
            self.on_close()
        self.destroy()

        
    def create_table(self, parent, level):
        """
        Create and populate a Treeview table for a given difficulty level.

        Args:
            parent (CTkFrame): The parent widget to place the table in.
            level (str): The difficulty level key (e.g., 'easy', 'medium', 'hard').
        """

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
        self.logic.insert_chords_into_tree(tree, self.data.get(level, []))
        self.tables[level] = tree

        # Bind double-click to start editing
        tree.bind("<Double-1>", self.on_double_click)


    def add_entry(self):
        """Insert a new chord row with default values into the currently selected tab."""

        current_tab_name = self.tabview.get()
        current_tab = self.tab_name_to_level.get(current_tab_name)
        tree = self.tables.get(current_tab)
        if tree:
            default_values = self.logic.get_default_row()
            index = len(tree.get_children())
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.insert("", "end", values=default_values, tags=(tag,))
            self.is_dirty = True  
            self.update_buttons_state()


    def delete_selected_row(self):
        """Delete the selected row(s) from the currently active Treeview tab."""

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


    def reset_tables(self):
        """Reset all chord tables to the original loaded state."""

        # Reset all tables to initial loaded data state
        for level, tree in self.tables.items():
            tree.delete(*tree.get_children())  # Clear all rows
            self.logic.insert_chords_into_tree(tree, self.data.get(level, []))
        self.is_dirty = False
        self.update_buttons_state()


    def save_changes(self):
        """Validate and save all chord data to file if changes were made."""

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
            messagebox.showerror(
                self.lang["error_editor_saving_title"],
                self.lang["error_editor_saving_message"],
                parent=self
            )


    def update_buttons_state(self):
        """Enable or disable save/reset buttons based on the dirty state."""
        
        if self.is_dirty:
            self.reset_button.configure(state="normal")
            self.save_button.configure(state="normal")
        else:
            self.reset_button.configure(state="disabled")
            self.save_button.configure(state="disabled")


    def on_double_click(self, event):
        """Handle double-clicks on a Treeview cell to start inline editing."""

        tree = event.widget
        if tree.identify("region", event.x, event.y) != "cell":
            return
        row_id = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if row_id and col:
            self.start_editing_cell(tree, row_id, col)


    def start_editing_cell(self, tree, row_id, col):
        """
        Open an entry widget to allow inline editing of a Treeview cell.

        Args:
            tree (Treeview): The Treeview widget.
            row_id (str): The ID of the row to edit.
            col (str): The column identifier (e.g., '#1').
        """

        # Prevent duplicate edit boxes
        if self.edit_box:
            return

        x, y, width, height = tree.bbox(row_id, col)
        if not width:
            return

        abs_x = tree.winfo_rootx() - self.winfo_rootx() + x
        abs_y = tree.winfo_rooty() - self.winfo_rooty() + y
        current_value = tree.set(row_id, col)

        self.edit_box = ttk.Entry(self)
        self.edit_box.place(x=abs_x, y=abs_y, width=width, height=height)
        self.edit_box.insert(0, current_value)
        self.edit_box.after_idle(self.edit_box.focus)
        self.edit_box.select_range(0, "end")

        def save_edit(event=None, next_col=None, prev_col=None):
            new_value = self.edit_box.get()
            old_value = tree.set(row_id, col)
            if new_value != old_value:
                tree.set(row_id, col, new_value)
                self.is_dirty = True
                self.update_buttons_state()
            self.edit_box.destroy()
            self.edit_box = None

            # Move to next cell (just focus, don't set any value)
            if next_col:
                self.start_editing_cell(tree, row_id, next_col)
            elif prev_col:
                self.start_editing_cell(tree, row_id, prev_col)

        self.edit_box.bind("<FocusOut>", save_edit)
        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<Tab>", lambda e: save_edit(next_col=self._get_next_col(tree, col)), "break")
        self.edit_box.bind("<Shift-Tab>", lambda e: save_edit(prev_col=self._get_prev_col(tree, col)), "break")


    def _get_next_col(self, tree, col):
        """
        Get the identifier of the next column in the Treeview.

        Args:
            tree (Treeview): The Treeview widget.
            col (str): The current column identifier (e.g., '#2').

        Returns:
            str or None: The next column identifier, or None if at the end.
        """

        col_index = int(col[1:]) - 1
        next_index = col_index + 1
        columns = tree["columns"]
        if next_index < len(columns):
            return f"#{next_index + 1}"
        return None
    

    def _get_prev_col(self, tree, col):
        """
        Get the identifier of the previous column in the Treeview.

        Args:
            tree (Treeview): The Treeview widget.
            col (str): The current column identifier (e.g., '#2').

        Returns:
            str or None: The previous column identifier, or None if at the start.
        """

        col_index = int(col[1:]) - 1
        prev_index = col_index - 1
        columns = tree["columns"]
        if prev_index >= 0:
            return f"#{prev_index + 1}"
        return None

