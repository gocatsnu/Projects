# coding: utf-8
"""Download hole-by-hole scores from DataGolf's API or PGA Tour's website.

This script expects a DataGolf API key and the event slug used by the API. It
fetches hole-by-hole scoring data for the specified year range and outputs a
CSV with one row per hole.

Because website endpoints occasionally change, you may need to tweak the
``fetch_datagolf`` function or add an alternative ``fetch_pga`` implementation
for the PGA Tour site. Check the API documentation for the latest details.
"""

import argparse
import csv
from urllib import request
from typing import Dict, Iterable, List


def fetch_datagolf(event: str, year: int, api_key: str) -> Dict:
    """Return JSON hole data for the given event and year via DataGolf."""
    url = (
        "https://feeds.datagolf.com/hole-by-hole"
        f"?event={event}&year={year}&tour=pga&key={api_key}"
    )
    with request.urlopen(url, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} fetching {url}")
        import json

        return json.loads(resp.read().decode())


def parse_datagolf(data: Dict, year: int) -> Iterable[Dict]:
    """Yield hole-score rows from DataGolf JSON."""
    for rnd in data.get("rounds", []):
        round_num = rnd.get("round")
        for player in rnd.get("players", []):
            name = player.get("player_name")
            for hole in player.get("holes", []):
                yield {
                    "year": year,
                    "player": name,
                    "round": round_num,
                    "hole": hole.get("hole"),
                    "score": hole.get("score"),
                }


def main() -> None:
    p = argparse.ArgumentParser(description="Scrape hole-by-hole scores")
    p.add_argument("event", help="event slug, e.g. the-memorial-tournament")
    p.add_argument("start_year", type=int, help="first year of data")
    p.add_argument("end_year", type=int, help="last year of data")
    p.add_argument("api_key", help="DataGolf API key")
    p.add_argument(
        "--output",
        default="outputs/muirfield_hole_scores.csv",
        help="CSV file to write",
    )
    args = p.parse_args()

    rows: List[Dict] = []
    for yr in range(args.start_year, args.end_year + 1):
        data = fetch_datagolf(args.event, yr, args.api_key)
        rows.extend(parse_datagolf(data, yr))

    if rows:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["year", "player", "round", "hole", "score"]
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.output}")
    else:
        print("No data returned")


if __name__ == "__main__":
    main()
