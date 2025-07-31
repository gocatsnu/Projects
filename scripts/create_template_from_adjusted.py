import csv
import argparse


def normalize(name: str) -> str:
    name = name.strip().replace('"', '')
    if ',' in name:
        last, first = [n.strip() for n in name.split(',', 1)]
        return f"{first} {last}".lower()
    return name.lower()


def load_adjusted(path: str) -> dict:
    data = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("PLAYER NAME")
            val = row.get("ADJUSTED STROKES")
            if not name or val is None or val == "":
                continue
            try:
                data[normalize(name)] = float(val)
            except ValueError:
                continue
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Match adjusted strokes to a DataGolf model template"
    )
    parser.add_argument("--adjusted", required=True, help="CSV with adjusted strokes")
    parser.add_argument("--template", required=True, help="DataGolf template CSV")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    scores = load_adjusted(args.adjusted)

    with open(args.template, encoding="utf-8-sig") as inp, open(args.output, "w", newline="") as out:
        reader = csv.DictReader(inp)
        fieldnames = [f for f in reader.fieldnames if f != "import_advice"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            key = row.get("player_name", "").strip()
            if key in scores:
                row["my_pred"] = round(scores[key], 3)
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
