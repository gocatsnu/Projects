from pathlib import Path
import pandas as pd
from shared.utils import load_config
from shared.gsheet_export import export_dataframe
from . import model

CONFIG_PATH = Path(__file__).with_name("config.yml")


def main() -> None:
    cfg = load_config(CONFIG_PATH)
    strokes = model.load_strokes(cfg["strokes_csv"])
    pairs = model.parse_matchups(cfg["matchups_csv"], strokes)
    adjusted = model.adjust_strokes(strokes, pairs)
    model.write_adjusted(adjusted, strokes, cfg["output_csv"])
    df = pd.read_csv(cfg["output_csv"])
    out_path = Path("outputs/pga_latest.csv")
    df.to_csv(out_path, index=False)
    if cfg.get("sheet_key"):
        export_dataframe(df, cfg["sheet_key"])


if __name__ == "__main__":
    main()
