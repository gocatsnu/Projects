import argparse
import json
from pathlib import Path
import requests


BASE_URL = "https://www.thesportsdb.com/api/v1/json/1"


def fetch_results(league_id: str, season: str) -> list:
    """Return completed Club World Cup matches from TheSportsDB."""
    url = f"{BASE_URL}/eventsseason.php"
    resp = requests.get(url, params={"id": league_id, "s": season}, timeout=10)
    resp.raise_for_status()
    events = resp.json().get("events") or []
    return [
        e
        for e in events
        if e.get("intHomeScore") is not None and e.get("intAwayScore") is not None
    ]



def main() -> None:
    parser = argparse.ArgumentParser(

        description="Download Club World Cup results from TheSportsDB",

    )
    parser.add_argument(
        "--output",
        default="data/raw/club_world_cup_results.json",
        help="Output JSON file",
    )
    parser.add_argument(

        "--league_id",
        default="1234",
        help="TheSportsDB league id for the Club World Cup",
    )
    parser.add_argument(
        "--season",
        default="2025",
        help="Season or year (default: %(default)s)",
    )
    args = parser.parse_args()

    results = fetch_results(args.league_id, args.season)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} results to {out_path}")


if __name__ == "__main__":
    main()
