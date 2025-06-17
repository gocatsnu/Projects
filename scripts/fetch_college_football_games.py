import argparse
import json
from pathlib import Path
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.the-odds-api.com/v4"


def find_ncaaf_key(api_key: str = API_KEY) -> str:
    """Return the sport key for college football."""
    url = f"{BASE_URL}/sports"
    resp = requests.get(url, params={"apiKey": api_key}, timeout=10)
    resp.raise_for_status()
    for sport in resp.json():
        title = sport.get("title", "").lower()
        if "college football" in title or "ncaaf" in title:
            return sport["key"]
    raise RuntimeError("College football sport not found")


def fetch_ncaaf_games(api_key: str, sport_key: str) -> list:
    """Return a list of upcoming college football games."""
    url = f"{BASE_URL}/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download college football games from The Odds API",
    )
    parser.add_argument(
        "--api_key",
        default=API_KEY,
        help="The Odds API key (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="data/raw/college_football_games.json",
        help="Output JSON file",
    )
    parser.add_argument(
        "--sport_key",
        help="Optional sport key for college football",
    )
    args = parser.parse_args()

    key = args.sport_key or find_ncaaf_key(args.api_key)
    games = fetch_ncaaf_games(args.api_key, key)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(games, f, indent=2)

    print(f"Saved {len(games)} games to {out_path}")


if __name__ == "__main__":
    main()
