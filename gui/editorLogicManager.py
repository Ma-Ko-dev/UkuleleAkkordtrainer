import re



class ChordEditorLogic:
    def __init__(self, lang):
        self.lang = lang

        # common placeholders
        self.placeholders = {
            "???",
            self.lang["editor_placeholder1"],
            self.lang["editor_placeholder2"]
        }

        self.list_columns = {"fingering", "fingers", "notes_on_strings", "chord_notes", "intervals"}
        self.note_pattern = re.compile(r"^[A-Ga-g](?:#|b|♯|♭)?$")
        self.interval_pattern = re.compile(r"^(?:b|#)?\d+$")


    def validate_treeviews(self, tables: dict) -> int:
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
