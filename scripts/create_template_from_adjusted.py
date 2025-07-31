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


def load_info(path: str) -> dict:
    """Load tournament info (course par, field strength, scoring prediction)."""
    info = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            key = row[1].strip().lower()
            info[key] = row[2].strip()
    return info


def main():
    parser = argparse.ArgumentParser(
        description="Match adjusted strokes to a DataGolf model template"
    )
    parser.add_argument("--adjusted", required=True, help="CSV with adjusted strokes")
    parser.add_argument("--template", required=True, help="DataGolf template CSV")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument(
        "--tournament",
        help="Tournament info CSV used to derive the average projected score",
    )
    parser.add_argument(
        "--avg-score",
        type=float,
        default=None,
        dest="avg_score",
        help="Average projected score when --tournament is not given",
    )
    args = parser.parse_args()

    scores = load_adjusted(args.adjusted)

    avg = args.avg_score
    if args.tournament:
        info = load_info(args.tournament)
        try:
            par = float(info.get("course par", 72))
            field = float(info.get("field strength", 0))
            scoring = float(info.get("scoring prediction", 0))
            avg = par + field + scoring
        except Exception:
            pass
    if avg is None:
        avg = 72.0

    with open(args.template, encoding="utf-8-sig") as inp, open(args.output, "w", newline="") as out:
        reader = csv.DictReader(inp)
        fieldnames = [f for f in reader.fieldnames if f != "import_advice"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            key = row.get("player_name", "").strip()
            if key in scores:
                sg = avg - scores[key]
                row["my_pred"] = round(sg, 3)
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
