"""Download DraftKings anytime touchdown odds for college football games."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://sportsbook.draftkings.com"
DEFAULT_SITE = "US-SB"
DEFAULT_MARKET = "Anytime Touchdown Scorer"


def fetch_json(url: str) -> dict:
    """Return the JSON payload for a DraftKings API endpoint."""

    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:  # nosec B310
        return json.load(response)


def find_event_group_id(base_url: str, site: str, *, league_terms: Iterable[str]) -> int:
    """Return the DraftKings event group id for college football."""

    url = f"{base_url}/sites/{site}/api/v5/sports"
    payload = fetch_json(url)
    search_terms = [term.lower() for term in league_terms]

    for sport in payload.get("sports", []):
        for league in sport.get("leagues", []):
            name = (league.get("name") or "").lower()
            if any(term in name for term in search_terms):
                event_group_id = league.get("eventGroupId")
                if event_group_id is None:
                    continue
                return int(event_group_id)

    raise RuntimeError("Could not find a DraftKings college football event group id")


@dataclass
class Outcome:
    """A single anytime touchdown market outcome."""

    event_id: int
    event_name: str
    start_time: Optional[str]
    away_team: Optional[str]
    home_team: Optional[str]
    label: Optional[str]
    player: Optional[str]
    odds_american: Optional[str]
    odds_decimal: Optional[float]
    outcome_id: Optional[int]
    offer_id: Optional[int]


def _event_lookup(event_group: dict) -> Dict[int, dict]:
    lookup: Dict[int, dict] = {}
    for event in event_group.get("events", []):
        event_id = event.get("eventId")
        if event_id is None:
            continue
        lookup[int(event_id)] = event
    return lookup


def _iter_anytime_td_offers(event_group: dict, *, market_name: str) -> Iterator[Outcome]:
    events = _event_lookup(event_group)
    target = market_name.lower()

    for category in event_group.get("offerCategories", []):
        for descriptor in category.get("offerSubcategoryDescriptors", []):
            descriptor_name = (descriptor.get("name") or "").lower()
            subcategory = descriptor.get("offerSubcategory", {})
            subcategory_name = (subcategory.get("name") or "").lower()
            if target not in descriptor_name and target not in subcategory_name:
                continue

            for offer_group in subcategory.get("offers", []):
                for offer in offer_group:
                    event_id = offer.get("eventId")
                    if event_id is None:
                        continue
                    event = events.get(int(event_id), {})
                    outcomes = offer.get("outcomes", [])
                    for outcome in outcomes:
                        yield Outcome(
                            event_id=int(event_id),
                            event_name=event.get("name", ""),
                            start_time=event.get("startDate"),
                            away_team=event.get("teamName1")
                            or event.get("awayTeamName")
                            or event.get("awayTeam"),
                            home_team=event.get("teamName2")
                            or event.get("homeTeamName")
                            or event.get("homeTeam"),
                            label=outcome.get("label"),
                            player=outcome.get("participant")
                            or outcome.get("description")
                            or outcome.get("label"),
                            odds_american=outcome.get("oddsAmerican"),
                            odds_decimal=outcome.get("oddsDecimal"),
                            outcome_id=outcome.get("id"),
                            offer_id=offer.get("id") or offer.get("offerId"),
                        )


def scrape_anytime_td(
    base_url: str,
    site: str,
    market_name: str,
    event_group_id: Optional[int] = None,
) -> List[Outcome]:
    """Return all anytime touchdown odds for the specified DraftKings site."""

    if event_group_id is None:
        event_group_id = find_event_group_id(
            base_url,
            site,
            league_terms=("ncaaf", "college football"),
        )

    url = f"{base_url}/sites/{site}/api/v5/eventgroups/{event_group_id}?format=json"
    payload = fetch_json(url)
    event_group = payload.get("eventGroup", {})
    outcomes = list(_iter_anytime_td_offers(event_group, market_name=market_name))
    outcomes.sort(key=lambda o: (o.start_time or "", o.player or ""))
    return outcomes


def write_csv(outcomes: Iterable[Outcome], output_path: Path) -> None:
    """Persist the scraped odds to ``output_path`` as CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "event_id",
                "event_name",
                "start_time",
                "away_team",
                "home_team",
                "player",
                "label",
                "odds_american",
                "odds_decimal",
                "outcome_id",
                "offer_id",
            ]
        )
        for outcome in outcomes:
            writer.writerow(
                [
                    outcome.event_id,
                    outcome.event_name,
                    outcome.start_time,
                    outcome.away_team,
                    outcome.home_team,
                    outcome.player,
                    outcome.label,
                    outcome.odds_american,
                    outcome.odds_decimal,
                    outcome.outcome_id,
                    outcome.offer_id,
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download DraftKings college football anytime touchdown odds",
    )
    parser.add_argument(
        "--output",
        default="outputs/draftkings_ncaaf_anytime_td.csv",
        help="CSV file for the scraped odds (default: %(default)s)",
    )
    parser.add_argument(
        "--market",
        default=DEFAULT_MARKET,
        help="DraftKings market name to search (default: %(default)s)",
    )
    parser.add_argument(
        "--base_url",
        default=DEFAULT_BASE_URL,
        help="DraftKings sportsbook base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--site",
        default=DEFAULT_SITE,
        help="DraftKings site segment (default: %(default)s)",
    )
    parser.add_argument(
        "--event_group_id",
        type=int,
        help="Optional DraftKings event group id for college football",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        outcomes = scrape_anytime_td(
            base_url=args.base_url,
            site=args.site,
            market_name=args.market,
            event_group_id=args.event_group_id,
        )
    except (HTTPError, URLError) as exc:
        raise SystemExit(f"Network error fetching DraftKings data: {exc}") from exc

    out_path = Path(args.output)
    write_csv(outcomes, out_path)
    print(f"Saved {len(outcomes)} anytime touchdown prices to {out_path}")


if __name__ == "__main__":
    main()
