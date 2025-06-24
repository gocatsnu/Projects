import argparse
import csv
import json
from pathlib import Path


def list_missing(json_path: Path, output_csv: Path) -> None:
    with open(json_path, 'r') as f:
        data = json.load(f)
    header = ["team_id", "team_name"]
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for team in data.get("teams", []):
            if team.get("player_count", 0) == 0:
                writer.writerow([team.get("id"), team.get("name")])


def main():
    parser = argparse.ArgumentParser(description="List teams without players")
    parser.add_argument("json_path", type=Path, help="Input JSON file")
    parser.add_argument("output_csv", type=Path, help="Output CSV file")
    args = parser.parse_args()
    list_missing(args.json_path, args.output_csv)


if __name__ == "__main__":
    main()
