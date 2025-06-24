import argparse
import csv
import json
from pathlib import Path


def _fix_shifted_rosters(teams: list) -> None:
    """The raw JSON lists several late teams without players and then shifts
    subsequent rosters by one team. Detect the empty "USC" entry and rotate the
    following rosters upward so each team has the proper players."""

    start = next((i for i, t in enumerate(teams) if t.get("name") == "USC"), None)
    if start is None:
        return

    for i in range(start, len(teams) - 1):
        teams[i]["players"] = teams[i + 1].get("players", [])
        teams[i]["player_count"] = len(teams[i]["players"])

    teams[-1]["players"] = []
    teams[-1]["player_count"] = 0


def convert(json_path: Path, output_csv: Path) -> None:
    with open(json_path, "r") as f:
        data = json.load(f)

    _fix_shifted_rosters(data.get("teams", []))

    header = ["team_id", "team_name", "player_name", "position", "overall_rating"]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for team in data.get("teams", []):
            tid = team.get("id")
            tname = team.get("name")
            for player in team.get("players", []):
                writer.writerow([
                    tid,
                    tname,
                    player.get("name"),
                    player.get("position"),
                    player.get("overall_rating"),
                ])


def main():
    parser = argparse.ArgumentParser(description="Convert TeamCrafters JSON to CSV")
    parser.add_argument("json_path", type=Path, help="Input JSON file")
    parser.add_argument("output_csv", type=Path, help="Output CSV file")
    args = parser.parse_args()
    convert(args.json_path, args.output_csv)


if __name__ == "__main__":
    main()
