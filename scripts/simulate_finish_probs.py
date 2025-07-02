import csv
import argparse
import random
from math import sqrt


def load_players(path):
    players = []
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row['player_name'].strip()
                pred = float(row['final_prediction'])
                sd = float(row['std_dev'])
            except (KeyError, ValueError):
                continue
            players.append({'name': name, 'pred': pred, 'sd': sd})
    return players


def simulate(players, iters=10000):
    counts = {p['name']: {'make_cut': 0, 'top_20': 0, 'top_10': 0, 'top_5': 0, 'win': 0} for p in players}
    n = len(players)
    half_sd_factor = 1 / sqrt(2)
    for _ in range(iters):
        totals = []
        cuts = []
        for p in players:
            total = random.gauss(p['pred'] * 4, p['sd'])
            cut = random.gauss(p['pred'] * 2, p['sd'] * half_sd_factor)
            totals.append((total, p['name']))
            cuts.append((cut, p['name']))
        cuts.sort(reverse=True)
        cut_thresh = cuts[min(65, n - 1)][0]
        made_cut = {name: score >= cut_thresh for score, name in cuts}
        totals.sort(reverse=True)
        for rank, (score, name) in enumerate(totals, 1):
            if rank == 1:
                counts[name]['win'] += 1
            if rank <= 5:
                counts[name]['top_5'] += 1
            if rank <= 10:
                counts[name]['top_10'] += 1
            if rank <= 20:
                counts[name]['top_20'] += 1
        for score, name in cuts:
            if made_cut[name]:
                counts[name]['make_cut'] += 1
    for name in counts:
        for k in counts[name]:
            counts[name][k] /= iters
    return counts


def write_output(counts, path):
    with open(path, 'w', newline='') as f:
        fieldnames = ['player_name', 'make_cut', 'top_20', 'top_10', 'top_5', 'win']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for name, vals in counts.items():
            row = {'player_name': name}
            row.update({k: round(v, 3) for k, v in vals.items()})
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description='Approximate finish probabilities using Monte Carlo.')
    parser.add_argument('--strokes', required=True, help='Strokes gained predictions CSV')
    parser.add_argument('--iters', type=int, default=10000, help='Simulation iterations')
    parser.add_argument('--output', required=True, help='Output CSV path')
    args = parser.parse_args()

    players = load_players(args.strokes)
    counts = simulate(players, args.iters)
    write_output(counts, args.output)


if __name__ == '__main__':
    main()
