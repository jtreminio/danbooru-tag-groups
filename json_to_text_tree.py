import json
import re
import argparse
from pathlib import Path

def sanitize_filename(name):
    name = name.strip().lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name

def load_ref_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def resolve_refs(data, base_path="."):
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = resolve_refs(v, base_path)
        return data
    elif isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, str) and item.strip().startswith("$ref:"):
                ref_path = item.strip()[5:].strip()
                ref_file = Path(base_path) / ref_path
                if ref_file.exists():
                    result.extend(load_ref_file(ref_file))
                else:
                    print(f"Warning: {ref_file} not found")
            else:
                result.append(item)
        return list(dict.fromkeys(result))  # dedup
    else:
        return data

def write_list_to_file(base_path: Path, filename: str, data: list[str]):
    base_path.mkdir(parents=True, exist_ok=True)
    file_path = base_path / f"{sanitize_filename(filename)}.txt"
    with file_path.open("w", encoding="utf-8") as f:
        for item in data:
            item = item.replace("\\", "")
            item = re.sub(r"([()])", r"\\\1", item)
            f.write(item + "\n")

def recurse(obj, path):
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_clean = sanitize_filename(key)

            if isinstance(value, list):
                write_list_to_file(path, key_clean, value)

            elif isinstance(value, dict):
                if "_data" in value and isinstance(value["_data"], list):
                    write_list_to_file(path / key_clean, key_clean, value["_data"])

                    for sub_key, sub_value in value.items():
                        if sub_key != "_data":
                            recurse({sub_key: sub_value}, path / key_clean)
                else:
                    recurse(value, path / key_clean)

def main():
    parser = argparse.ArgumentParser(description="Flatten structured JSON into directory tree of .txt files.")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    resolved = resolve_refs(data)
    recurse(resolved, Path(args.output))

if __name__ == "__main__":
    main()
