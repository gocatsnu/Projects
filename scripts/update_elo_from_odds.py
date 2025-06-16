import argparse
import json
import csv
import math
from pathlib import Path

# Map inconsistent team names from the odds feed to the names used in the
# ELO CSV so ratings can be matched correctly.
NAME_MAP = {
    "Al Ahly FC": "Al Ahly",
    "Al Ain FC": "Al Ain",
    "Al-Hilal Saudi FC": "Al Hilal",
    "Atlético Madrid": "Atletico Madrid",
    "Auckland City FC": "Auckland City",
    "Espérance Sportive de Tunis": "Esperance Sportive de Tunis",
    "FC Porto": "Porto",
    "Inter Miami CF": "Inter Miami",
    "Mamelodi Sundowns F.C.": "Mamelodi Sundowns",
    "Paris Saint Germain": "Paris Saint-Germain",
    "Pachuca": "CF Pachuca",
    "RB Salzburg": "FC Salzburg",
    "Seattle Sounders FC": "Seattle Sounders",
}


def fix_name(name: str) -> str:
    """Return canonical team name used in the ELO table."""
    return NAME_MAP.get(name, name)


def read_elos(path: str) -> dict:
    """Return mapping of team name to ELO rating as float."""
    elos = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                elos[row["Team"]] = float(row["Adjusted_ELO"])
            except (KeyError, ValueError):
                continue
    return elos


def parse_events(path: str) -> list:
    """Return list of events with averaged implied probabilities."""
    with open(path) as f:
        data = json.load(f)

    events = []
    for event in data:
        # Normalise team names so they match those in the ELO ratings table
        home = fix_name(event.get("home_team"))
        away = fix_name(event.get("away_team"))
        start = event.get("commence_time")
        probs = []  # (home, draw, away)
        for bm in event.get("bookmakers", []):
            for market in bm.get("markets", []):
                if market.get("key") != "h2h":
                    continue
                prices = {fix_name(o["name"]): o.get("price") for o in market.get("outcomes", [])}
                if home in prices and away in prices and "Draw" in prices:
                    h = 1 / prices[home]
                    a = 1 / prices[away]
                    d = 1 / prices["Draw"]
                    total = h + a + d
                    probs.append((h / total, d / total, a / total))
                break
        if not probs:
            continue
        home_p = sum(p[0] for p in probs) / len(probs)
        draw_p = sum(p[1] for p in probs) / len(probs)
        away_p = sum(p[2] for p in probs) / len(probs)
        events.append(
            {
                "home": home,
                "away": away,
                "start": start,
                "home_prob": home_p,
                "draw_prob": draw_p,
                "away_prob": away_p,
            }
        )
    events.sort(key=lambda e: e["start"])
    return events


def update_elos(elos: dict, events: list) -> dict:
    """Return a new dict of updated ELOs after applying events."""
    new_elos = elos.copy()
    for ev in events:
        home, away = ev["home"], ev["away"]
        if home not in new_elos or away not in new_elos:
            continue
        h_elo, a_elo = new_elos[home], new_elos[away]
        avg = (h_elo + a_elo) / 2
        diff_old = h_elo - a_elo
        score_home = ev["home_prob"] + 0.5 * ev["draw_prob"]
        diff_market = 400 * math.log10(score_home / (1 - score_home))
        diff_new = 0.5 * diff_old + 0.5 * diff_market
        new_elos[home] = round(avg + diff_new / 2, 2)
        new_elos[away] = round(avg - diff_new / 2, 2)
    return new_elos


def write_elos(new_elos: dict, old_elos: dict, path: str) -> None:
    """Write updated ELOs alongside the previous values and change."""
    rows = []
    for team in sorted(new_elos):
        updated = new_elos[team]
        previous = old_elos.get(team, float("nan"))
        change = round(updated - previous, 2) if isinstance(previous, float) else ""
        rows.append(
            {
                "Team": team,
                "Previous_ELO": previous,
                "Updated_ELO": updated,
                "Change": change,
            }
        )

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Team", "Previous_ELO", "Updated_ELO", "Change"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update Club World Cup ELO ratings using market odds"
    )
    parser.add_argument(
        "--elo_csv",
        default="data/raw/2025_Club_World_Cup_Teams_with_ELO.csv",
        help="CSV file with team ELO ratings",
    )
    parser.add_argument(
        "--odds_json",
        default="data/raw/club_world_cup_odds2020616.json",
        help="JSON file with Club World Cup odds",
    )
    parser.add_argument(
        "--output",
        default="outputs/Updated_Club_World_Cup_ELO.csv",
        help="Output CSV with updated ELO ratings",
    )
    args = parser.parse_args()

    base_elos = read_elos(args.elo_csv)
    events = parse_events(args.odds_json)
    updated = update_elos(base_elos, events)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_elos(updated, base_elos, args.output)
    print(f"Wrote updated ELO ratings for {len(updated)} teams to {args.output}")


if __name__ == "__main__":
    main()
