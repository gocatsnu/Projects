import csv
import math
from adjust_projections import american_to_prob

# Standard normal CDF using error function

def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# Convert American odds to decimal payout (including stake)
def american_to_decimal(o):
    o = int(o)
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / abs(o)

# Convert probability to American odds

def prob_to_american(p):
    """Return American odds for probabilities p and 1-p."""
    if p <= 0 or p >= 1:
        raise ValueError('p must be between 0 and 1')

    def single(prob):
        if prob == 0.5:
            val = -110
        elif prob > 0.5:
            val = -100 * prob / (1 - prob)
        else:
            val = 100 * (1 - prob) / prob
        val = int(round(val))
        return f"{val:+d}"

    return single(p), single(1 - p)


def load_adjusted(path):
    data = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row['PLAYER NAME'].strip()] = float(row['ADJUSTED STROKES'])
    return data


def fair_odds(matchup_csv, strokes, out_csv):
    sigma_player = 4.5  # typical tournament std dev per player
    sigma_diff = math.sqrt(2) * sigma_player
    other_books = [
        'draftkings', 'bet365', 'fanduel',
        'betmgm', 'pointsbet', 'bovada',
        'caesars', 'unibet'
    ]
    out_rows = []
    seen = set()
    with open(matchup_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            has_market = any(
                row[col] not in ('', 'null')
                for col in ('betonline_p1', 'betcris_p1', 'pinnacle_p1')
            )
            if has_market:
                continue
            p1 = row['name_p1'].strip()
            p2 = row['name_p2'].strip()
            key = (p1, p2)
            if key in seen:
                continue
            seen.add(key)
            if p1 not in strokes or p2 not in strokes:
                continue
            diff = strokes[p1] - strokes[p2]
            win_prob = phi(-diff / sigma_diff)
            odds_p1, odds_p2 = prob_to_american(win_prob)
            row_out = {
                'p1': p1,
                'p2': p2,
                'fair_prob_p1': f'{win_prob:.4f}',
                'fair_odds_p1': odds_p1,
                'fair_odds_p2': odds_p2,
            }
            prob_p2 = 1 - win_prob
            for book in other_books:
                o1 = row.get(f'{book}_p1', '')
                o2 = row.get(f'{book}_p2', '')
                if o1 and o1 != 'null':
                    dec = american_to_decimal(o1)
                    ev = win_prob * dec - 1
                    row_out[f'{book}_p1'] = o1
                    row_out[f'{book}_p1_ev'] = f'{ev:.4f}'
                else:
                    row_out[f'{book}_p1'] = ''
                    row_out[f'{book}_p1_ev'] = ''
                if o2 and o2 != 'null':
                    dec = american_to_decimal(o2)
                    ev = prob_p2 * dec - 1
                    row_out[f'{book}_p2'] = o2
                    row_out[f'{book}_p2_ev'] = f'{ev:.4f}'
                else:
                    row_out[f'{book}_p2'] = ''
                    row_out[f'{book}_p2_ev'] = ''
            out_rows.append(row_out)
    with open(out_csv, 'w', newline='') as f:
        fieldnames = ['p1', 'p2', 'fair_prob_p1', 'fair_odds_p1', 'fair_odds_p2']
        for book in other_books:
            fieldnames.extend([
                f'{book}_p1', f'{book}_p1_ev',
                f'{book}_p2', f'{book}_p2_ev'
            ])
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print('Wrote', len(out_rows), 'projected odds to', out_csv)


if __name__ == '__main__':
    strokes = load_adjusted('Adjusted Strokes Charles Schwab 20250520.csv')
    fair_odds('Charles Schwab 2025 72 Hole 20250520.csv', strokes,
              'Projected Fair Odds Charles Schwab 20250520.csv')
