import re
import json
import config



class ChordEditorLogic:
    """
    Logic handler for validating, preparing, and saving chord data in the chord editor.

    This class provides:
    - Input validation for chord entries (format, duplicates, placeholders, etc.)
    - Data preparation for JSON output
    - JSON serialization with custom formatting
    - Integration with Treeview display logic

    Attributes:
        lang (dict): Dictionary of localized strings for error messages and placeholders.
        placeholder_name (str): Placeholder text for the 'name' field.
        placeholder_fingering (str): Placeholder text for the 'fingering' field.
        placeholders (set): Set of strings considered invalid input placeholders.
        list_columns (set): Columns that expect comma-separated lists.
        note_pattern (Pattern): Regex for validating musical note input (e.g., C#, F♭).
        interval_pattern (Pattern): Regex for validating interval input (e.g., b3, #5, 7).
    """
    
    def __init__(self, lang):
        self.lang = lang

        # common placeholders
        self.placeholder_name = self.lang["editor_placeholder1"]
        self.placeholder_fingering = self.lang["editor_placeholder2"]
        self.placeholders = {
            "???",
            self.placeholder_name,
            self.placeholder_fingering
        }

        self.list_columns = {"fingering", "fingers", "notes_on_strings", "chord_notes", "intervals"}
        self.note_pattern = re.compile(r"^[A-Ga-g](?:#|b|♯|♭)?$")
        self.interval_pattern = re.compile(r"^(?:b|#)?\d+$")


    def validate_treeviews(self, tables: dict) -> int:
        """
        Validate all cells in all Treeviews for syntax, completeness, and uniqueness.

        Args:
            tables (dict): Dictionary mapping difficulty levels to Treeview widgets.

        Returns:
            int: Number of invalid cells detected.
        """

        invalid_cells = 0
        seen_names = {}
        seen_fingering = {}

        for level, tree in tables.items():
            for row_id in tree.get_children():
                entry = {}
                parts_cache = {}
                row_index = tree.index(row_id) + 1

                for col in tree["columns"]:
                    value = tree.set(row_id, col).strip()
                    entry[col] = value

                    if value == "" or value in self.placeholders:
                        print(self.lang["error_editor_empty_or_placeholder_value"].format(
                            level=level, row_index=row_index, col=col))
                        invalid_cells += 1
                        continue

                    if col in self.list_columns:
                        if "." in value:
                            print(self.lang["error_editor_dot_instead_of_comma"].format(
                                level=level, row_index=row_index, col=col, value=value))
                            invalid_cells += 1
                            continue

                        parts = [p.strip() for p in value.split(",")]
                        parts_cache[col] = parts

                        if any(p == "" for p in parts):
                            print(self.lang["error_editor_empty_list_element"].format(
                                level=level, row_index=row_index, col=col, value=value))
                            invalid_cells += 1
                            continue

                        if col in {"fingering", "fingers"}:
                            if len(parts) != 4:
                                print(self.lang["error_editor_invalid_length"].format(
                                    level=level, row_index=row_index, col=col, parts=parts))
                                invalid_cells += 1
                                continue
                            for p in parts:
                                if not p.isdigit() or not (0 <= int(p) <= 12):
                                    print(self.lang["error_editor_invalid_number"].format(
                                        level=level, row_index=row_index, col=col, p=p))
                                    invalid_cells += 1
                                    break

                        if col in {"notes_on_strings", "chord_notes"}:
                            if len(parts) < 3:
                                print(self.lang["error_editor_minimum_length"].format(
                                    level=level, row_index=row_index, col=col, min_length=3))
                                invalid_cells += 1
                                continue
                            for p in parts:
                                if not self.note_pattern.match(p):
                                    print(self.lang["error_editor_invalid_note_format"].format(
                                        level=level, row_index=row_index, col=col, value=p))
                                    invalid_cells += 1
                                    break

                        elif col == "intervals":
                            if len(parts) < 3:
                                print(self.lang["error_editor_minimum_length"].format(
                                    level=level, row_index=row_index, col=col, min_length=3))
                                invalid_cells += 1
                                continue
                            for p in parts:
                                if not self.interval_pattern.match(p):
                                    print(self.lang["error_editor_invalid_interval_format"].format(
                                        level=level, row_index=row_index, col=col, value=p))
                                    invalid_cells += 1
                                    break

                name = entry.get("name", "").strip()
                fingering = entry.get("fingering", "")
                norm_name = name.lower()
                norm_fingering = fingering.replace(" ", "")

                if name:
                    if norm_name in seen_names:
                        print(self.lang["error_editor_duplicate_chord_name"].format(
                            level=level, row_index=row_index, name=name, previous_row=seen_names[norm_name]))
                        invalid_cells += 1
                    else:
                        seen_names[norm_name] = row_index

                if fingering:
                    if norm_fingering in seen_fingering:
                        print(self.lang["error_editor_duplicate_fingering"].format(
                            level=level, row_index=row_index, fingering=fingering, previous_row=seen_fingering[norm_fingering]))
                        invalid_cells += 1
                    else:
                        seen_fingering[norm_fingering] = row_index

        return invalid_cells


    def prepare_save_data(self, tables: dict) -> dict:
        """
        Extract chord data from all Treeviews and convert it into a structured dict.

        Args:
            tables (dict): Dictionary mapping difficulty levels to Treeview widgets.

        Returns:
            dict: Structured chord data ready for serialization.
        """
                
        data = {}
        for level, tree in tables.items():
            data[level] = []
            for row_id in tree.get_children():
                item = tree.item(row_id)["values"]
                chord = {
                    "name": item[0],
                    "fingering": [s.strip() for s in item[1].split(",")],
                    "fingers": [s.strip() for s in item[2].split(",")],
                    "notes_on_strings": [s.strip() for s in item[3].split(",")],
                    "chord_notes": [s.strip() for s in item[4].split(",")],
                    "intervals": [s.strip() for s in item[5].split(",")],
                }
                data[level].append(chord)
        return data


    def json_dumps_compact_lists(self, data):
        """
        Serialize the chord data to a JSON string with compact list formatting.

        Args:
            data (dict): Chord data to be serialized.

        Returns:
            str: Formatted JSON string with compact lists.
        """

        text = json.dumps(data, ensure_ascii=False, indent=4)
        pattern = re.compile(r'\[\s*(\".*?\"(?:,\s*\".*?\")*)\s*\]', re.DOTALL)

        def replacer(match):
            content = match.group(1)
            compact = content.replace('\n', '').replace(' ', '')
            return f'[{compact}]'

        return pattern.sub(replacer, text)


    def save_data(self, data):
        """
        Write chord data to file with compact list formatting.

        Args:
            data (dict): Chord data to save.

        Returns:
            tuple: (True, None) on success, or (False, Exception) on error.
        """

        try:
            json_text = self.json_dumps_compact_lists(data)
            with open(config.CHORD_PATH, "w", encoding="utf-8") as f:
                f.write(json_text)
            return True, None
        except Exception as e:
            return False, e


    def format_chord_for_display(self, chord: dict) -> tuple:
        """
        Convert a chord dictionary into a tuple of displayable strings for Treeview.

        Args:
            chord (dict): Chord entry with structured data.

        Returns:
            tuple: Display-friendly string values for each column.
        """
            
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
    

    def get_default_row(self) -> list:
        """
        Return a default row with placeholders for a new chord.

        Returns:
            list: List of default placeholder values for each column.
        """

        return [
            self.placeholder_name,             # placeholder chord name
            self.placeholder_fingering,        # editable fingering field
            "???",                             # unknown finger suggestion
            "???",                             # unknown notes on strings
            "???",                             # unknown chord tones
            "???"                              # unknown intervals
        ]


    def insert_chords_into_tree(self, tree, chords: list):
        """
        Populate a Treeview with a list of chords and apply alternating row tags.

        Args:
            tree (Treeview): The target Treeview widget.
            chords (list): List of chord dictionaries to insert.
        """
        
        for i, chord in enumerate(chords):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            values = self.format_chord_for_display(chord)
            tree.insert("", "end", values=values, tags=(tag,))


