import argparse
import csv
import json
import re
import unicodedata
from difflib import get_close_matches
from pathlib import Path

HFA = 2.5

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
    "delaware fightin blue": "Delaware",
    "east carolina": "ECU",
    "james madison": "JMU",
    "louisiana tech": "La. Tech",
    "northern illinois": "NIU",
    "san diego state": "SDSU",
    "tulsa golden": "Tulsa",
    "south florida": "USF",
    "virginia tech": "Va. Tech",
    "washington state": "Wash. St.",
}


def normalize(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.lower().replace("&", "and")
    name = re.sub(r"[^a-z0-9 ]+", "", name)
    return re.sub(r"\s+", " ", name).strip()


def load_sp_plus(path: str) -> dict:
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


def consensus_home_spread(event: dict) -> float | None:
    home = event["home_team"]
    away = event["away_team"]
    for bm in event.get("bookmakers", []):
        for market in bm.get("markets", []):
            if market.get("key") != "spreads":
                continue
            home_point = None
            away_point = None
            for o in market.get("outcomes", []):
                if o.get("name") == home and "point" in o:
                    home_point = float(o["point"])
                elif o.get("name") == away and "point" in o:
                    away_point = float(o["point"])
            if home_point is not None:
                return home_point
            if away_point is not None:
                return -away_point
            break
    return None


def _aggregate_event_spreads(events: list, lookup: dict) -> list[tuple[str, str, float]]:
    pairs: dict[tuple[str, str], list[float]] = {}
    for ev in events:
        home = map_team(ev["home_team"], lookup)
        away = map_team(ev["away_team"], lookup)
        if not home or not away:
            continue
        spread = consensus_home_spread(ev)
        if spread is None:
            continue
        key = (home, away)
        pairs.setdefault(key, []).append(spread)
    out = []
    for (home, away), spreads in pairs.items():
        out.append((home, away, sum(spreads) / len(spreads)))
    return out


def update_ratings(sp: dict, events: list, lookup: dict, precision: int) -> tuple[dict, set[str]]:
    new = sp.copy()
    seen: set[str] = set()
    for home, away, home_spread in _aggregate_event_spreads(events, lookup):
        market_margin = -home_spread
        rating_market = market_margin - HFA
        h_old = new[home]
        a_old = new[away]
        diff_old = h_old - a_old
        diff_new = 0.5 * diff_old + 0.5 * rating_market
        avg = (h_old + a_old) / 2
        new[home] = round(avg + diff_new / 2, precision)
        new[away] = round(avg - diff_new / 2, precision)
        seen.update([home, away])
    return new, seen


def write_ratings(new: dict, old: dict, path: str, precision: int) -> None:
    rows = []
    for team in sorted(new):
        updated = new[team]
        previous = old.get(team, float("nan"))
        change = (
            round(updated - previous, precision)
            if isinstance(previous, float)
            else ""
        )
        rows.append({"Team": team, "Previous_SP": previous, "Updated_SP": updated, "Change": change})
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Team", "Previous_SP", "Updated_SP", "Change"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update SP+ ratings using FanDuel spreads")
    parser.add_argument("--sp_csv", default="data/raw/SP+20250615.csv", help="CSV file with SP+ ratings")
    parser.add_argument("--spreads_json", default="data/raw/fanduel_college_football_spreads_2025-07-17.json", help="JSON file with FanDuel spreads")
    parser.add_argument("--output", default="outputs/Updated_SP_Plus_FD.csv", help="Output CSV path")
    parser.add_argument("--precision", type=int, default=2, help="Decimal places for rounding")
    parser.add_argument(
        "--no_adjustment_list",
        default=None,
        help="Optional path to write teams without an adjustment",
    )
    args = parser.parse_args()

    sp = load_sp_plus(args.sp_csv)
    lookup = build_lookup(sp)
    with open(args.spreads_json) as f:
        events = json.load(f)
    updated, seen = update_ratings(sp, events, lookup, args.precision)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_ratings(updated, sp, args.output, args.precision)
    print(f"Wrote updated ratings for {len(updated)} teams to {args.output}")

    zero_change = []
    for team in sorted(updated):
        prev = sp.get(team, float("nan"))
        upd = updated[team]
        if round(upd - prev, args.precision) == 0:
            reason = "no spreads" if team not in seen else "neutral adjustment"
            zero_change.append((team, reason))

    if zero_change:
        print("\nTeams with no adjustment:")
        for team, reason in zero_change:
            print(f"{team}: {reason}")
        if args.no_adjustment_list:
            with open(args.no_adjustment_list, "w") as f:
                for team, reason in zero_change:
                    f.write(f"{team},{reason}\n")
            print(f"Wrote {len(zero_change)} entries to {args.no_adjustment_list}")


if __name__ == "__main__":
    main()
