import csv
from pathlib import Path

BOOKS = [
    'bet365', 'fanduel', 'draftkings', 'betcris', 'caesars',
    'betway', 'bovada', 'betonline', 'unibet', 'betmgm',
    'betfair', 'pinnacle'
]

MARKET_FILES = {
    'win': 'italian_open_win_american_ch.csv',
    'top_5': 'italian_open_top5_american_ch.csv',
    'top_10': 'italian_open_top10_american_ch.csv',
    'top_20': 'italian_open_top20_american_ch.csv',
    'make_cut': 'italian_open_cut_american_ch.csv',
    'miss_cut': 'italian_open_mc_american_ch.csv',
}

PRED_FILE = 'my_model Italian Open 20250625.csv'

def american_to_decimal(odds: str):
    try:
        o = int(odds)
    except Exception:
        return None
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)

def american_to_prob(odds: str):
    try:
        o = int(odds)
    except Exception:
        return None
    if o > 0:
        return 100 / (o + 100)
    return -o / (-o + 100)

def load_predictions(path: Path):
    preds = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['player_name'].strip().lower()
            name = ' '.join(p.title() for p in name.split())
            mc = american_to_prob(row['make_cut'])
            t20 = american_to_prob(row['top_20'])
            t10 = american_to_prob(row['top_10'])
            t5 = american_to_prob(row['top_5'])
            win = american_to_prob(row['win'])
            preds[name] = {
                'make_cut': mc,
                'miss_cut': 1 - mc if mc is not None else None,
                'top_20': t20,
                'top_10': t10,
                'top_5': t5,
                'win': win,
            }
    return preds

def best_ev_bets(preds: dict, data_root: str, threshold: float = 0.06):
    bets = []
    for market, file in MARKET_FILES.items():
        path = Path(data_root) / file
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['player_name'].strip()
                if ',' in name:
                    last, first = [x.strip() for x in name.split(',', 1)]
                    norm = f"{first.title()} {last.title()}"
                else:
                    norm = ' '.join(p.title() for p in name.split())
                if norm not in preds:
                    continue
                prob = preds[norm].get(market)
                if prob is None:
                    continue
                best = None
                for book in BOOKS:
                    odds = row.get(f"{book}_odds")
                    if not odds or odds in ('', 'null'):
                        continue
                    dec = american_to_decimal(odds)
                    if dec is None:
                        continue
                    ev = prob * dec - 1
                    if ev >= threshold and (best is None or ev > best['ev']):
                        best = {
                            'market': market,
                            'player': name,
                            'book': book,
                            'odds': odds,
                            'ev': ev,
                        }
                if best:
                    bets.append(best)
    bets.sort(key=lambda x: x['ev'], reverse=True)
    return bets

def main():
    preds = load_predictions(Path('data/raw') / PRED_FILE)
    bets = best_ev_bets(preds, 'data/raw')
    out = Path('outputs/italian_open_positive_ev.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['market', 'player', 'book', 'odds', 'ev'])
        writer.writeheader()
        for b in bets:
            b2 = b.copy(); b2['ev'] = round(b2['ev'], 4)
            writer.writerow(b2)
    for b in bets:
        print(f"{b['market']}, {b['player']}, {b['book']}, {b['odds']}, {b['ev']:.4f}")

if __name__ == '__main__':
    main()
