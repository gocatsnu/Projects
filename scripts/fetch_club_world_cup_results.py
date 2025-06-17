import argparse
import json
from pathlib import Path
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.the-odds-api.com/v4"


def find_club_world_cup_key(api_key: str = API_KEY) -> str:
    """Return the sport key for the Club World Cup."""
    url = f"{BASE_URL}/sports"
    resp = requests.get(url, params={"apiKey": api_key}, timeout=10)
    resp.raise_for_status()
    for sport in resp.json():
        title = sport.get("title", "").lower()
        if "club world cup" in title:
            return sport["key"]
    raise RuntimeError("Club World Cup sport not found")


def fetch_results(api_key: str, sport_key: str, days_from: int = 30) -> list:
    """Return a list of completed Club World Cup matches."""
    url = f"{BASE_URL}/sports/{sport_key}/scores"
    params = {
        "apiKey": api_key,
        "daysFrom": days_from,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Club World Cup results from The Odds API",
    )
    parser.add_argument(
        "--api_key",
        default=API_KEY,
        help="The Odds API key (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="data/raw/club_world_cup_results.json",
        help="Output JSON file",
    )
    parser.add_argument(
        "--sport_key",
        help="Optional sport key for the Club World Cup",
    )
    parser.add_argument(
        "--days_from",
        type=int,
        default=30,
        help="How many days back to fetch results (default: %(default)s)",
    )
    args = parser.parse_args()

    key = args.sport_key or find_club_world_cup_key(args.api_key)
    results = fetch_results(args.api_key, key, args.days_from)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} results to {out_path}")


if __name__ == "__main__":
    main()
