import csv
from pathlib import Path


def american_to_decimal(odds: str):
    """Return decimal odds or None if input cannot be parsed."""
    try:
        o = int(odds)
    except (TypeError, ValueError):
        return None
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)


def format_pred_name(name: str) -> str:
    parts = name.strip().split()
    if len(parts) < 2:
        return name.title()
    first = parts[0].title()
    last = " ".join(p.title() for p in parts[1:])
    return f"{last}, {first}"


def load_predictions(path: str) -> dict:
    preds = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = format_pred_name(row['player_name'])
            preds[key] = {
                'make_cut': float(row['make_cut']),
                'top_20': float(row['top_20']),
                'top_10': float(row['top_10']),
                'top_5': float(row['top_5']),
                'win': float(row['win']),
            }
    return preds


BOOKS = [
    'bet365',
    'fanduel',
    'draftkings',
    'betcris',
    'caesars',
    'betway',
    'bovada',
    'betonline',
    'unibet',
    'betmgm',
    'betfair',
    'pinnacle',
]

MARKET_FILES = {
    'win': 'klm_open_win_american_ch.csv',
    'top_5': 'klm_open_top5_american_ch.csv',
    'top_10': 'klm_open_top10_american_ch.csv',
    'top_20': 'klm_open_top20_american_ch.csv',
    'make_cut': 'klm_open_cut_american_ch.csv',
}


def compute_positive_ev(preds: dict, root: str, threshold: float = 0.06):
    """Return all wagers with EV above the given threshold."""
    bets = []
    for market, fname in MARKET_FILES.items():
        path = Path(root) / fname
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['player_name'].strip()
                if name not in preds:
                    continue
                prob = preds[name][market]
                for book in BOOKS:
                    odds = row.get(f"{book}_odds")
                    if not odds or odds in ("", "null"):
                        continue
                    payout = american_to_decimal(odds)
                    if payout is None:
                        continue
                    ev = prob * payout - 1
                    if ev > threshold:
                        bets.append(
                            {
                                "market": market,
                                "player": name,
                                "book": book,
                                "odds": odds,
                                "ev": ev,
                            }
                        )
    bets.sort(key=lambda x: x['ev'], reverse=True)
    return bets


def main():
    preds = load_predictions("data/raw/KLM Open Simulation.csv")
    bets = compute_positive_ev(preds, "data/raw")
    out_path = Path('outputs/model_positive_ev.csv')
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['market', 'player', 'book', 'odds', 'ev'])
        writer.writeheader()
        for b in bets:
            b2 = b.copy()
            b2['ev'] = round(b2['ev'], 4)
            writer.writerow(b2)
    for b in bets[:20]:
        print(f"{b['market']}, {b['player']}, {b['book']}, {b['odds']}, {b['ev']:.4f}")


if __name__ == '__main__':
    main()
