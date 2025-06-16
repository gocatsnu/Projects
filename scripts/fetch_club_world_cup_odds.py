import argparse
import json
from pathlib import Path
import requests

API_KEY = "1362ad97eb3190133c1d980b759acd94"
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


def fetch_cwc_matches(api_key: str, sport_key: str) -> list:
    """Return a list of upcoming Club World Cup matches."""
    url = f"{BASE_URL}/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Club World Cup matches from The Odds API"
    )
    parser.add_argument(
        "--api_key",
        default=API_KEY,
        help="The Odds API key (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="data/raw/club_world_cup_odds.json",
        help="Output JSON file",
    )
    parser.add_argument(
        "--sport_key",
        help="Optional sport key for the Club World Cup",
    )
    args = parser.parse_args()

    key = args.sport_key or find_club_world_cup_key(args.api_key)
    matches = fetch_cwc_matches(args.api_key, key)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(matches, f, indent=2)

    print(f"Saved {len(matches)} matches to {out_path}")


if __name__ == "__main__":
    main()
