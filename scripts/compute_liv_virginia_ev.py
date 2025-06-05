import csv
from pathlib import Path

BOOKS = [
    'bet365','fanduel','draftkings','betcris','caesars','betway','bovada','betonline','unibet','betmgm','betfair','pinnacle'
]

MARKET_FILES = {
    'win': 'liv_virginia_win_american_ch.csv',
    'top_5': 'liv_virginia_top5_american_ch.csv',
    'top_10': 'liv_virginia_top10_american_ch.csv',
    'top_20': 'liv_virginia_top20_american_ch.csv'
}

PRED_FILE = 'LIV Virginia Model Fairs 20250605.csv'

def american_to_decimal(odds:str):
    try:
        o=int(odds)
    except Exception:
        return None
    if o>0:
        return 1+o/100
    return 1+100/(-o)


def load_predictions(path):
    preds={}
    with open(path) as f:
        reader=csv.DictReader(f)
        for row in reader:
            # prediction file uses "first last" names
            name=row['player_name'].strip().lower()
            name=" ".join(p.title() for p in name.split())
            preds[name]= {
                'win': float(row['win']),
                'top_5': float(row['top_5']),
                'top_10': float(row['top_10']),
                'top_20': float(row['top_20'])
            }
    return preds


def best_ev_bets(preds, data_root, threshold=0.06):
    bets=[]
    for market,file in MARKET_FILES.items():
        path=Path(data_root)/file
        with open(path) as f:
            reader=csv.DictReader(f)
            for row in reader:
                name=row['player_name'].strip()
                # odds files use "Last, First" format
                if ',' in name:
                    last, first = [x.strip() for x in name.split(',',1)]
                    norm = f"{first.title()} {last.title()}"
                else:
                    norm = " ".join(p.title() for p in name.split())
                pred_key = norm
                if pred_key not in preds:
                    continue
                prob=preds[pred_key][market]
                best=None
                for book in BOOKS:
                    odds=row.get(f"{book}_odds")
                    if not odds or odds in ('','null'):
                        continue
                    dec=american_to_decimal(odds)
                    if dec is None:
                        continue
                    ev=prob*dec-1
                    if ev>=threshold and (best is None or ev>best['ev']):
                        best={'market':market,'player':name,'book':book,'odds':odds,'ev':ev}
                if best:
                    bets.append(best)
    bets.sort(key=lambda x: x['ev'], reverse=True)
    return bets


def main():
    preds=load_predictions(Path('data/raw')/PRED_FILE)
    bets=best_ev_bets(preds,'data/raw')
    out=Path('outputs/liv_virginia_positive_ev.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out,'w',newline='') as f:
        writer=csv.DictWriter(f, fieldnames=['market','player','book','odds','ev'])
        writer.writeheader()
        for b in bets:
            b2=b.copy(); b2['ev']=round(b2['ev'],4)
            writer.writerow(b2)
    for b in bets:
        print(f"{b['market']}, {b['player']}, {b['book']}, {b['odds']}, {b['ev']:.4f}")

if __name__=='__main__':
    main()
