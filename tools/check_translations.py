from collections import OrderedDict  # Damit die reihenfolge im JSON bleibt
import os
import json

LANG_DIR = "lang"  
REFERENCE_FILE = "en_US.json" 
PREFIX = "[MISSING] "

def load_json_ordered(path):
    with open(path, encoding="utf-8") as f:
        # JSON reinladen und reihenfolge behalten
        return json.load(f, object_pairs_hook=OrderedDict)

def merge_with_reference(reference, target, prefix=PREFIX):
    merged = OrderedDict()
    # alle schluessel aus der referenz durchgehen
    for key, value in reference.items():
        if key in target:
            # uebersetzung gefunden
            merged[key] = target[key]
        else:
            # fehlende Übersetzung mit prefix markieren
            merged[key] = prefix + value
    return merged

def main():
    ref_path = os.path.join(LANG_DIR, REFERENCE_FILE)
    if not os.path.exists(ref_path):
        print(f"Reference file '{REFERENCE_FILE}' nicht gefunden")
        return

    reference_data = load_json_ordered(ref_path)

    # alle sprachdateien im ordner checken
    for filename in os.listdir(LANG_DIR):
        if not filename.endswith(".json") or filename == REFERENCE_FILE:
            continue

        path = os.path.join(LANG_DIR, filename)
        target_data = load_json_ordered(path)

        merged_data = merge_with_reference(reference_data, target_data)

        # wenn was fehlt datei neuschreiben
        if merged_data != target_data:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} wurde aktualisiert")
        else:
            print(f"{filename} ist schon aktuell")

if __name__ == "__main__":
    main()
