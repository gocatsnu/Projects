import csv
from pathlib import Path
from typing import Dict, List

BANKROLL = 100000.0

BOOKS = [
    "bet365",
    "fanduel",
    "draftkings",
    "betcris",
    "caesars",
    "betway",
    "bovada",
    "betonline",
    "unibet",
    "betmgm",
    "betfair",
    "pinnacle",
]

MARKET_FILES = {
    "win": "liv_andalucia_win_american_ch.csv",
    "top_5": "liv_andalucia_top5_american_ch.csv",
    "top_10": "liv_andalucia_top10_american_ch.csv",
    "top_20": "liv_andalucia_top20_american_ch.csv",
}

PRED_FILE = "my_model_liv Andalucia.csv"


def american_to_decimal(odds: str) -> float:
    o = float(odds)
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)


def american_to_prob(odds: str) -> float:
    o = float(odds)
    if o > 0:
        return 100 / (o + 100)
    return -o / (-o + 100)


def normalize_model_name(name: str) -> str:
    return name.strip().lower()


def normalize_book_name(name: str) -> str:
    if "," in name:
        last, first = [x.strip().lower() for x in name.split(",", 1)]
        return f"{first} {last}"
    return name.strip().lower()


def load_model_predictions(path: Path) -> Dict[str, Dict[str, float]]:
    preds: Dict[str, Dict[str, float]] = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = normalize_model_name(row["player_name"])
            preds[name] = {
                "top_20": american_to_prob(row["top_20"]),
                "top_10": american_to_prob(row["top_10"]),
                "top_5": american_to_prob(row["top_5"]),
                "win": american_to_prob(row["win"]),
            }
    return preds


def compute_bets(preds: Dict[str, Dict[str, float]], data_root: Path) -> List[dict]:
    bets: List[dict] = []
    for market, fname in MARKET_FILES.items():
        path = data_root / fname
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = normalize_book_name(row["player_name"])
                if key not in preds:
                    continue
                prob = preds[key][market]
                for book in BOOKS:
                    odds = row.get(f"{book}_odds")
                    if not odds or odds in ("", "null"):
                        continue
                    dec = american_to_decimal(odds)
                    ev = prob * dec - 1
                    b = dec - 1
                    if b <= 0:
                        continue
                    kelly_f = (b * prob - (1 - prob)) / b
                    if ev <= 0 or kelly_f <= 0:
                        continue
                    kelly_bet = kelly_f * BANKROLL
                    if ev >= 0.05 or kelly_bet >= 1000:
                        bets.append(
                            {
                                "market": market,
                                "player": row["player_name"],
                                "book": book,
                                "odds": odds,
                                "ev": ev,
                                "kelly_fraction": kelly_f,
                                "kelly_bet": kelly_bet,
                            }
                        )
    return bets


def main() -> None:
    preds = load_model_predictions(Path("data/raw") / PRED_FILE)
    bets = compute_bets(preds, Path("data/raw"))
    if not bets:
        print("No bets meet criteria.")
        return
    bets.sort(key=lambda x: (-x["ev"], -x["kelly_bet"]))
    out_path = Path("outputs/liv_andalucia_ev_kelly_filtered.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["market", "player", "book", "odds", "ev", "kelly_fraction", "kelly_bet"],
        )
        writer.writeheader()
        for b in bets:
            row = b.copy()
            row["ev"] = round(row["ev"], 4)
            row["kelly_fraction"] = round(row["kelly_fraction"], 4)
            row["kelly_bet"] = round(row["kelly_bet"], 2)
            writer.writerow(row)
    print(f"Wrote {len(bets)} bets to {out_path}")


if __name__ == "__main__":
    main()
