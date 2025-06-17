import csv
from collections import defaultdict

def american_to_prob(odds):
    """Convert American odds to implied win probability."""
    o = int(odds)
    if o > 0:
        return 100/(o + 100)
    return -o/(-o + 100)

def phi_inv(p):
    """Inverse standard normal CDF (approximation)."""
    import math
    # constants from Peter J. Acklam's approximation
    a1=-39.69683028665376
    a2=220.9460984245205
    a3=-275.9285104469687
    a4=138.3577518672690
    a5=-30.66479806614716
    a6=2.506628277459239
    b1=-54.47609879822406
    b2=161.5858368580409
    b3=-155.6989798598866
    b4=66.80131188771972
    b5=-13.28068155288572
    c1=-7.784894002430293e-03
    c2=-3.223964580411365e-01
    c3=-2.400758277161838e+00
    c4=-2.549732539343734e+00
    c5=4.374664141464968e+00
    c6=2.938163982698783e+00
    d1=7.784695709041462e-03
    d2=3.224671290700398e-01
    d3=2.445134137142996
    d4=3.754408661907416
    p_low = 0.02425
    p_high = 1 - p_low
    if p <= 0 or p >= 1:
        raise ValueError('p must be between 0 and 1')
    if p < p_low:
        q = math.sqrt(-2*math.log(p))
        return (((((c1*q+c2)*q+c3)*q+c4)*q+c5)*q+c6)/((((d1*q+d2)*q+d3)*q+d4)*q+1)
    elif p <= p_high:
        q = p - 0.5
        r = q*q
        return (((((a1*r+a2)*r+a3)*r+a4)*r+a5)*r+a6)*q/(((((b1*r+b2)*r+b3)*r+b4)*r+b5)*r+1)
    else:
        q = math.sqrt(-2*math.log(1-p))
        return -(((((c1*q+c2)*q+c3)*q+c4)*q+c5)*q+c6)/((((d1*q+d2)*q+d3)*q+d4)*q+1)

def load_strokes(path, use_adjusted=True, course=None):
    """Load strokes from a CSV. Optionally filter by course name."""
    data = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize header names for easier matching
            row = {k.strip().upper().replace("_", " "): v for k, v in row.items()}

            if course and row.get("COURSE NAME") and course not in row["COURSE NAME"]:
                continue

            if use_adjusted and "ADJUSTED STROKES" in row:
                val = row["ADJUSTED STROKES"]
            elif "BASELINE STROKES" in row:
                val = row["BASELINE STROKES"]
            elif "STROKES PREDICTION" in row:
                val = row.get("STROKES PREDICTION")
            else:
                val = row.get("STROKES")

            if val is None or val == "":
                continue

            name = row.get("PLAYER NAME")
            if not name:
                continue
            data[name.strip()] = float(val)
    return data

import math

def parse_matchups(path, strokes, holes=72):
    """Parse matchup CSV and return implied stroke differences.

    Duplicate rows for the same player pair are averaged so that each
    matchup influences the adjustment only once.
    """
    agg = defaultdict(lambda: [0.0, 0])  # (p1,p2) -> [sum_implied_diff, count]

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.strip().lower(): v for k, v in row.items()}
            p1 = row['name_p1'].strip()
            p2 = row['name_p2'].strip()

            probs = []
            for col in ('betonline_p1', 'betcris_p1', 'pinnacle_p1'):
                val = row[col]
                if not val or val == 'null':
                    continue
                try:
                    p1_prob = american_to_prob(val)
                except Exception:
                    continue
                # normalize for the book's margin when possible
                val2 = row[col.replace('_p1', '_p2')]
                if val2 and val2 != 'null':
                    try:
                        p2_prob = american_to_prob(val2)
                        s = p1_prob + p2_prob
                        if s > 0:
                            p1_prob = p1_prob / s
                    except Exception:
                        pass
                probs.append(p1_prob)

            if not probs:
                continue
            if p1 not in strokes or p2 not in strokes:
                continue

            prob_p1 = sum(probs) / len(probs)
            m = row.get('market', '').lower()
            if any(r in m for r in ('r1', 'r2', 'r3', 'r4')) or 'round' in m:
                sigma_round = 2.5  # see pga_dispersion_model.md
                sigma_diff = math.sqrt(2) * sigma_round
                scale = 1  # already single-round
            else:
                n_rounds = holes // 18
                sigma_round = 2.5
                sigma_diff = math.sqrt(n_rounds * 2) * sigma_round
                # convert tournament difference to per-round difference
                scale = 1 / n_rounds if n_rounds else 1

            implied_diff = (-sigma_diff * phi_inv(prob_p1)) * scale
            key = (p1, p2)
            agg[key][0] += implied_diff
            agg[key][1] += 1

    pairs = []
    for (p1, p2), (total_diff, count) in agg.items():
        dg_diff = strokes[p1] - strokes[p2]
        pairs.append((p1, p2, dg_diff, total_diff / count))

    return pairs

def adjust_strokes(strokes, pairs, iters=25, lr=0.5):
    """Iteratively adjust strokes so all matchups are satisfied in aggregate."""

    adj = defaultdict(float)
    players = set(strokes)

    for _ in range(iters):
        for a, b, _, imp in pairs:
            # predicted difference with current adjustments
            pred = (strokes[a] + adj[a]) - (strokes[b] + adj[b])
            err = imp - pred
            # move each player half the error in opposite directions
            adj[a] += lr * err / 2
            adj[b] -= lr * err / 2

    return {p: strokes[p] + adj[p] for p in players}

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Adjust stroke projections using market odds.')
    parser.add_argument('--strokes', default='DG Strokes Charles Schwab 20250520.csv',
                        help='CSV with baseline or previously adjusted strokes')
    parser.add_argument('--baseline', default=None,
                        help='CSV with original baseline strokes (optional)')
    parser.add_argument('--matchups', action='append', default=[],
                        help='CSV file with matchup odds. Can be used multiple times.')
    parser.add_argument('--output', default='Adjusted Strokes Charles Schwab 20250520.csv',
                        help='Output CSV path')
    parser.add_argument('--course', default=None,
                        help='If provided, filter strokes to rows containing this course name')
    parser.add_argument('--holes', type=int, default=72,
                        help='Number of holes for tournament matchups (default 72)')
    args = parser.parse_args()

    if not args.matchups:
        args.matchups = ['Charles Schwab 2025 72 Hole 20250520.csv']

    baseline = load_strokes(args.baseline or args.strokes, use_adjusted=False, course=args.course)
    strokes = load_strokes(args.strokes, use_adjusted=True, course=args.course)
    pairs = []
    for mp in args.matchups:
        pairs.extend(parse_matchups(mp, strokes, holes=args.holes))
    final = adjust_strokes(strokes, pairs)

    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['PLAYER NAME', 'BASELINE STROKES', 'ADJUSTED STROKES'])
        for name in sorted(final):
            writer.writerow([name, baseline.get(name, strokes.get(name, '')), round(final[name], 3)])

    print('Adjusted projections written for', len(final), 'players')
