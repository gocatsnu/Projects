import csv
import json
import requests


def fetch_espn_leaderboard(event_id: str) -> dict:
    """Return leaderboard JSON from ESPN for a given event."""
    url = (
        "https://site.web.api.espn.com/apis/v2/sports/golf/pga-tour/leaderboard"
        f"?event={event_id}&enable=linescores"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def parse_hole_scores(data: dict) -> list:
    """Parse hole-by-hole scores for every competitor."""
    events = data.get("events") or data.get("items")
    if not events:
        return []
    event = events[0]
    competitions = event.get("competitions") or []
    if not competitions:
        return []
    comp = competitions[0]
    players = []
    for c in comp.get("competitors", []):
        athlete = c.get("athlete", {})
        name = athlete.get("displayName") or athlete.get("shortName")
        scores = [s.get("displayValue") for s in c.get("linescores", [])]
        players.append({"name": name, "scores": scores})
    return players


def write_scores_csv(players: list, out_path: str) -> None:
    """Write list of hole scores to CSV."""
    # ensure 18 columns for holes
    header = ["Player"] + [f"H{i}" for i in range(1, 19)]
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for p in players:
            row = [p["name"]] + p["scores"][:18]
            row += ["" for _ in range(19 - len(row))]
            writer.writerow(row)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download live hole-by-hole scores from ESPN"
    )
    parser.add_argument("--event_id", required=True, help="ESPN event id")
    parser.add_argument(
        "--output",
        default="live_scores.csv",
        help="Output CSV file (default: live_scores.csv)",
    )
    args = parser.parse_args()

    data = fetch_espn_leaderboard(args.event_id)
    players = parse_hole_scores(data)
    write_scores_csv(players, args.output)
    print(f"Wrote {len(players)} players to {args.output}")
