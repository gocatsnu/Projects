import argparse
import csv
import json
from statistics import NormalDist
import re
import unicodedata
from difflib import get_close_matches
from pathlib import Path

HFA = 2.5
SIGMA = 14.0  # spread-result error standard deviation

# Manual mapping from odds team names to SP+ team names.
# Keys are normalised forms with the mascot removed ("Army Black Knights" → "army black").
TEAM_SYNONYMS = {
    "appalachian state": "App. St.",
    "army black": "Army",
    "marshall thundering": "Marshall",
    "mississippi state": "Miss. St.",
    "old dominion": "ODU",
    "penn state nittany": "Penn St.",
    "san jose state": "SJSU",
    "southern mississippi golden": "So. Miss",
    "tcu horned": "TCU",
    "central michigan": "CMU",
    "eastern michigan": "EMU",
    "western michigan": "WMU",
    "florida atlantic": "FAU",
    "georgia tech yellow": "Ga. Tech",
    "hawaii rainbow": "Hawaii",
    "jacksonville state": "J'ville St.",
    "notre dame fighting": "Notre Dame",
    "rutgers scarlet": "Rutgers",
    "alabama crimson": "Alabama",
    "duke blue": "Duke",
    "illinois fighting": "Illinois",
    "tulane green": "Tulane",
    "western kentucky": "WKU",
}


def normalize(name: str) -> str:
    """Return ASCII lowercase alphanumeric representation."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.lower().replace("&", "and")
    name = re.sub(r"[^a-z0-9 ]+", "", name)
    return re.sub(r"\s+", " ", name).strip()


def load_sp_plus(path: str) -> dict:
    """Return mapping of team name to SP+ rating."""
    ratings = {}
    with open(path) as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    for line in lines[2:]:
        parts = line.split(",")
        m = re.match(r"\d+\.\s*(.+)", parts[0])
        if not m:
            continue
        team = m.group(1)
        try:
            rating = float(parts[1])
        except ValueError:
            continue
        ratings[team] = rating
    return ratings


def build_lookup(ratings: dict) -> dict:
    """Return mapping of normalised name to SP+ team name."""
    lookup = {}
    for team in ratings:
        key = normalize(team.replace("St.", "State"))
        lookup[key] = team
    return lookup


def map_team(name: str, lookup: dict) -> str | None:
    base = " ".join(name.split()[:-1])
    key = normalize(base)
    if key in TEAM_SYNONYMS:
        return TEAM_SYNONYMS[key]
    if key in lookup:
        return lookup[key]
    match = get_close_matches(key, lookup.keys(), n=1, cutoff=0.6)
    if match:
        return lookup[match[0]]
    return None


def american_to_prob(odds: int) -> float:
    """Convert American odds to implied probability."""
    if odds > 0:
        return 100 / (odds + 100)
    return -odds / (-odds + 100)


def consensus_home_prob(event: dict) -> float | None:
    probs = []
    home = event["home_team"]
    away = event["away_team"]
    for bm in event.get("bookmakers", []):
        for market in bm.get("markets", []):
            if market.get("key") != "h2h":
                continue
            prices = {o["name"]: o.get("price") for o in market.get("outcomes", [])}
            if home in prices and away in prices:
                h = american_to_prob(int(prices[home]))
                a = american_to_prob(int(prices[away]))
                total = h + a
                probs.append(h / total)
            break
    if not probs:
        return None
    return sum(probs) / len(probs)


def prob_to_margin(prob: float) -> float:
    """Convert win probability to point margin using normal assumption."""
    prob = min(max(prob, 1e-6), 1 - 1e-6)
    z = NormalDist().inv_cdf(prob)
    return SIGMA * z


def _aggregate_event_probs(events: list, lookup: dict) -> list[tuple[str, str, float]]:
    """Return list of unique (home, away, home_prob) tuples averaged over duplicates."""
    pairs: dict[tuple[str, str], list[float]] = {}
    for ev in events:
        home = map_team(ev["home_team"], lookup)
        away = map_team(ev["away_team"], lookup)
        if not home or not away:
            continue
        prob = consensus_home_prob(ev)
        if prob is None:
            continue
        key = (home, away)
        pairs.setdefault(key, []).append(prob)
    out = []
    for (home, away), probs in pairs.items():
        out.append((home, away, sum(probs) / len(probs)))
    return out


def update_ratings(sp: dict, events: list, lookup: dict) -> dict:
    new = sp.copy()
    for home, away, home_prob in _aggregate_event_probs(events, lookup):
        market_margin = prob_to_margin(home_prob)
        rating_market = market_margin - HFA
        h_old = new[home]
        a_old = new[away]
        diff_old = h_old - a_old
        diff_new = 0.5 * diff_old + 0.5 * rating_market
        avg = (h_old + a_old) / 2
        new[home] = round(avg + diff_new / 2, 1)
        new[away] = round(avg - diff_new / 2, 1)
    return new


def write_ratings(new: dict, old: dict, path: str) -> None:
    rows = []
    for team in sorted(new):
        updated = new[team]
        previous = old.get(team, float("nan"))
        change = round(updated - previous, 1) if isinstance(previous, float) else ""
        rows.append({"Team": team, "Previous_SP": previous, "Updated_SP": updated, "Change": change})
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Team", "Previous_SP", "Updated_SP", "Change"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update SP+ ratings using market odds")
    parser.add_argument("--sp_csv", default="data/raw/SP+20250615.csv", help="CSV file with SP+ ratings")
    parser.add_argument("--odds_json", default="data/raw/college_football_games_2025-06-16.json", help="JSON file with game odds")
    parser.add_argument("--output", default="outputs/Updated_SP_Plus.csv", help="Output CSV path")
    args = parser.parse_args()

    sp = load_sp_plus(args.sp_csv)
    lookup = build_lookup(sp)
    with open(args.odds_json) as f:
        events = json.load(f)
    updated = update_ratings(sp, events, lookup)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_ratings(updated, sp, args.output)
    print(f"Wrote updated ratings for {len(updated)} teams to {args.output}")


if __name__ == "__main__":
    main()
