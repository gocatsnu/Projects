from pathlib import Path
import pandas as pd
from shared.data_fetch import fetch_csv
from shared.gsheet_export import export_dataframe
from shared.utils import load_config

CONFIG_PATH = Path(__file__).with_name("config.yml")


def main() -> None:
    cfg = load_config(CONFIG_PATH)
    csv_path = fetch_csv(cfg["data_url"])
    df = pd.read_csv(csv_path)
    # Placeholder modelling step
    df["prediction"] = 0.0
    Path("outputs").mkdir(exist_ok=True)
    out_path = Path("outputs/nba_latest.csv")
    df.to_csv(out_path, index=False)
    if cfg.get("sheet_key"):
        export_dataframe(df, cfg["sheet_key"])


if __name__ == "__main__":
    main()
