import csv
from pathlib import Path

BOOKS = [
    'bet365','fanduel','draftkings','betcris','caesars','betway','bovada','betonline','unibet','betmgm','betfair','pinnacle'
]

MARKET_FILES = {
    'win': 'liv_dallas_win_american_ch.csv',
    'top_5': 'liv_dallas_top5_american_ch.csv',
    'top_10': 'liv_dallas_top10_american_ch.csv',
    'top_20': 'liv_dallas_top20_american_ch.csv'
}

PRED_FILE = 'My_Model LIV Dallas 20250625.csv'

def american_to_decimal(odds: str):
    try:
        o = int(float(odds))
    except Exception:
        return None
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)

def american_to_prob(odds: str):
    try:
        o = float(odds)
    except Exception:
        return None
    if o == float('inf'):
        return 0.0
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
            preds[name] = {}
            for market in ['win','top_5','top_10','top_20']:
                val = row.get(market)
                if val in (None, '', 'null'):
                    prob = None
                else:
                    prob = american_to_prob(val)
                preds[name][market] = prob
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
                    last, first = [x.strip() for x in name.split(',',1)]
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
                        best = {'market': market, 'player': name, 'book': book, 'odds': odds, 'ev': ev}
                if best:
                    bets.append(best)
    bets.sort(key=lambda x: x['ev'], reverse=True)
    return bets

def main():
    preds = load_predictions(Path('data/raw')/PRED_FILE)
    bets = best_ev_bets(preds, 'data/raw')
    out = Path('outputs/liv_dallas_positive_ev.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['market','player','book','odds','ev'])
        writer.writeheader()
        for b in bets:
            b2 = b.copy(); b2['ev'] = round(b2['ev'],4)
            writer.writerow(b2)
    for b in bets:
        print(f"{b['market']}, {b['player']}, {b['book']}, {b['odds']}, {b['ev']:.4f}")

if __name__ == '__main__':
    main()
