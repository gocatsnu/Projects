import pandas as pd
import requests
from pathlib import Path

URL = "https://footballdatabase.com/ranking/world/1"
OUTPUT = Path("outputs/Football ELO World.csv")


def download_football_elo(url: str = URL, output: Path = OUTPUT) -> None:
    """Download the world football ELO rankings and save as CSV."""
    response = requests.get(url)
    response.raise_for_status()
    tables = pd.read_html(response.text)
    if not tables:
        raise ValueError("No tables found on the page")
    df = tables[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Saved {len(df)} rows to {output}")


if __name__ == "__main__":
    download_football_elo()
