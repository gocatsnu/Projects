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

def load_strokes(path):
    data = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'ADJUSTED STROKES' in row:
                val = row['ADJUSTED STROKES']
            else:
                val = row.get('STROKES PREDICTION')
            if val is None or val == '':
                continue
            data[row['PLAYER NAME'].strip()] = float(val)
    return data

def parse_matchups(path, strokes):
    pairs = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            p1 = row['name_p1'].strip()
            p2 = row['name_p2'].strip()
            probs = []
            for col in ('betonline_p1','betcris_p1','pinnacle_p1'):
                val = row[col]
                if val and val != 'null':
                    try:
                        p1_prob = american_to_prob(val)
                    except Exception:
                        continue
                    # if paired p2 price exists, normalize for margin
                    val2 = row[col.replace('_p1','_p2')]
                    if val2 and val2 != 'null':
                        try:
                            p2_prob = american_to_prob(val2)
                            s = p1_prob + p2_prob
                            if s > 0:
                                p1_prob = p1_prob/s
                        except Exception:
                            pass
                    probs.append(p1_prob)
            if not probs:
                continue
            if p1 not in strokes or p2 not in strokes:
                continue
            prob_p1 = sum(probs)/len(probs)
            sigma_diff = 6.0
            implied_diff = -sigma_diff * phi_inv(prob_p1)
            dg_diff = strokes[p1] - strokes[p2]
            pairs.append((p1,p2,dg_diff,implied_diff))
    return pairs

def adjust_strokes(strokes, pairs):
    adj = defaultdict(float)
    cnt = defaultdict(int)
    for a,b,dg,imp in pairs:
        delta = imp - dg
        adj[a] += delta/2
        adj[b] -= delta/2
        cnt[a]+=1
        cnt[b]+=1
    result = {}
    for name,val in strokes.items():
        if cnt[name]:
            result[name] = val + adj[name]/cnt[name]
        else:
            result[name] = val
    return result

if __name__ == '__main__':
    strokes = load_strokes('DG Strokes Charles Schwab 20250520.csv')
    pairs = parse_matchups('Charles Schwab 2025 72 Hole 20250520.csv', strokes)
    final = adjust_strokes(strokes, pairs)
    with open('Adjusted Strokes Charles Schwab 20250520.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['PLAYER NAME','BASELINE STROKES','ADJUSTED STROKES'])
        for name in sorted(final):
            writer.writerow([name, strokes[name], round(final[name],3)])
    print('Adjusted projections written for', len(final), 'players')
