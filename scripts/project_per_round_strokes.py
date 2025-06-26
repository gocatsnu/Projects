import argparse
import csv


def load_tournament_info(path: str) -> dict:
    """Load course par, field strength, and scoring prediction from CSV."""
    info = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            key = row[1].strip().lower()
            val = row[2].strip()
            info[key] = val
    return info


def main():
    parser = argparse.ArgumentParser(description="Project per round strokes")
    parser.add_argument("--strokes", required=True, help="DataGolf strokes gained predictions CSV")
    parser.add_argument("--tournament", required=True, help="Tournament information CSV")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    info = load_tournament_info(args.tournament)
    par = float(info.get("course par", 72))
    field = float(info.get("field strength", 0))
    scoring = float(info.get("scoring prediction", 0))

    rows = []
    with open(args.strokes, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("player_name")
            if not name:
                continue
            try:
                sg = float(row["final_prediction"])
            except (TypeError, ValueError):
                continue
            projected = round(par + field - sg + scoring, 3)
            rows.append([name.strip("\""), projected])

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PLAYER NAME", "PROJECTED STROKES"])
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
