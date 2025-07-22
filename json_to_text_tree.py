import json
import re
from pathlib import Path
import argparse

def sanitize_name(name):
    """Convert name to snake_case and remove invalid Windows characters."""
    name = name.strip().lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name

def is_flat_string_dict(d):
    """Check if all values (excluding optional 'self') are strings."""
    if not isinstance(d, dict):
        return False
    return all(isinstance(v, str) for k, v in d.items() if k != 'self')

def write_tags_from_json(data, base_path, parent_key=None):
    for key, value in data.items():
        # Special case: skip creating "self" subdir
        if key == "self":
            if isinstance(value, dict):
                write_tags_from_json(value, base_path, parent_key)
            elif isinstance(value, str):
                base_path.mkdir(parents=True, exist_ok=True)
                filename = base_path / f"{sanitize_name(parent_key)}.txt"
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(value.replace("\\", "") + "\n")
            continue

        filename_base = sanitize_name(key)
        current_path = base_path

        if isinstance(value, dict):
            if is_flat_string_dict(value):
                current_path.mkdir(parents=True, exist_ok=True)
                out_file = current_path / f"{filename_base}.txt"
                with open(out_file, "a", encoding="utf-8") as f:
                    for v in value.values():
                        if isinstance(v, str):
                            escaped = v.replace("\\", "") \
                                .replace("(", r"\(") \
                                .replace(")", r"\)")
                            f.write(escaped + "\n")
            else:
                write_tags_from_json(value, current_path / filename_base, key)

        elif isinstance(value, str):
            current_path.mkdir(parents=True, exist_ok=True)
            out_file = current_path / f"{sanitize_name(parent_key)}.txt"
            with open(out_file, "a", encoding="utf-8") as f:
                f.write(value.replace("\\", "") + "\n")

def main():
    parser = argparse.ArgumentParser(description="Convert nested JSON into text files in snake_case directories.")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Output base directory")
    args = parser.parse_args()

    input_json = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    write_tags_from_json(data, output_dir)

if __name__ == "__main__":
    main()
