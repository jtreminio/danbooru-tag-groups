import json
import sys
from pathlib import Path

def lowercase_keys(obj):
    if isinstance(obj, dict):
        return {k.lower(): lowercase_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [lowercase_keys(item) for item in obj]
    else:
        return obj

def main(input_path, output_path=None):
    input_path = Path(input_path)
    output_path = Path(output_path) if output_path else input_path.with_name(f"lowercase_{input_path.name}")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    lowered_data = lowercase_keys(data)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(lowered_data, f, indent=2, ensure_ascii=False)

    print(f"Lowercased JSON saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lowercase_json_keys.py input.json [output.json]")
    else:
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
