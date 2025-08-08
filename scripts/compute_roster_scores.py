import argparse
import csv
import json
from pathlib import Path


POSITION_GROUPS = {
    "QB": ["QB"],
    "LT": ["LT"],
    "CB1": ["CB"],
    "EDGE": ["RE", "LE"],
    "LB1": ["MLB", "ROLB", "LOLB"],
    "WR1": ["WR"],
    "RT": ["RT"],
    "DT1": ["DT"],
    "CB2": ["CB"],
    "LG": ["LG"],
    "DE": ["RE", "LE"],
    "S1": ["FS", "SS"],
    "WR2": ["WR"],
    "C": ["C"],
    "LB2": ["MLB", "ROLB", "LOLB"],
    "DT2": ["DT"],
    "RB": ["HB"],
    "RG": ["RG"],
    "WR3": ["WR"],
    "TE": ["TE"],
    "CB3": ["CB"],
    "S2": ["FS", "SS"],
}



def load_pos_values(path: Path) -> dict:
    values = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            pos = row[0].strip()
            if pos.lower() == "total" or not pos:
                continue
            val = row[1].strip().strip("%")
            try:
                values[pos] = float(val) / 100.0
            except ValueError:
                continue
    return values


def take_rating(pos_lists: dict, options: list) -> int:
    for p in options:
        lst = pos_lists.get(p)
        if lst:
            return lst.pop(0)
    return 0


def compute_team_score(team: dict, values: dict) -> float:
    pos_lists = {}
    for player in team.get("players", []):
        pos = player.get("position")
        rating = player.get("overall_rating")
        if pos is None or rating is None:
            continue
        pos_lists.setdefault(pos, []).append(rating)
    for lst in pos_lists.values():
        lst.sort(reverse=True)

    ratings = {}
    # iterate in positional order defined above
    temp_lists = {k: v[:] for k, v in pos_lists.items()}
    for pos in [
        "QB",
        "LT",
        "CB1",
        "EDGE",
        "LB1",
        "WR1",
        "RT",
        "DT1",
        "CB2",
        "LG",
        "DE",
        "S1",
        "WR2",
        "C",
        "LB2",
        "DT2",
        "RB",
        "RG",
        "WR3",
        "TE",
        "CB3",
        "S2",
    ]:
        opts = POSITION_GROUPS.get(pos, [])
        ratings[pos] = take_rating(temp_lists, opts)

    score = 0.0
    for pos, weight in values.items():
        rating = ratings.get(pos, 0)
        score += rating * weight
    return score


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute roster scores from TeamCrafters JSON using positional value weights"
    )
    parser.add_argument("json_path", type=Path, help="TeamCrafters JSON file")
    parser.add_argument(
        "--values_csv",
        default="College Football Positional Value.csv",
        help="CSV with positional values",
    )
    parser.add_argument(
        "--output",
        default="outputs/team_roster_scores.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    values = load_pos_values(Path(args.values_csv))
    with open(args.json_path) as f:
        data = json.load(f)

    results = []
    for team in data.get("teams", []):
        score = compute_team_score(team, values)
        results.append([team.get("name"), round(score, 3)])

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["team_name", "roster_score"])
        writer.writerows(results)

    print(f"Wrote {len(results)} teams to {out_path}")


if __name__ == "__main__":
    main()
