from collections import OrderedDict
import os
import json

LANG_DIR = "lang"
REFERENCE_FILE = "en_US.json"
PREFIX = "[MISSING] "

def load_json_ordered(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def merge_with_reference(reference, target, prefix=PREFIX):
    merged = OrderedDict()
    for key, value in reference.items():
        if key in target:
            merged[key] = target[key]
        else:
            merged[key] = prefix + value
    return merged

def main():
    ref_path = os.path.join(LANG_DIR, REFERENCE_FILE)
    if not os.path.exists(ref_path):
        print(f"Reference file '{REFERENCE_FILE}' not found.")
        return

    reference_data = load_json_ordered(ref_path)

    for filename in os.listdir(LANG_DIR):
        if not filename.endswith(".json") or filename == REFERENCE_FILE:
            continue

        path = os.path.join(LANG_DIR, filename)
        target_data = load_json_ordered(path)

        merged_data = merge_with_reference(reference_data, target_data)

        if merged_data != target_data:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} was updated.")
        else:
            print(f"{filename} is up to date.")

if __name__ == "__main__":
    main()
