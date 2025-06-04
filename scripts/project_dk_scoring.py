import csv
import argparse

# DraftKings scoring constants
DK_HOLE_POINTS = {
    'eagle_or_better': 8,  # treat double eagle the same as eagle for expectation
    'birdie': 3,
    'par': 0.5,
    'bogey': -0.5,
    'double_or_worse': -1,
}

# Average finish points for groups (approximate)
FINISH_PTS = {
    'win': 30,
    '2_5': 17,   # average of positions 2-5
    '6_10': 9.2, # average of positions 6-10
    '11_20': 5.5, # average of positions 11-20
}


def normalize_name(name: str) -> str:
    name = name.strip().replace('"', '')
    if ',' in name:
        last, first = [n.strip() for n in name.split(',', 1)]
        return f"{first} {last}".title()
    return name.title()

def load_hole_points(path):
    totals = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player = normalize_name(row['player'])
            e = float(row['p_eagle_or_better'])
            b = float(row['p_birdie'])
            p = float(row['p_par'])
            bo = float(row['p_bogey'])
            d = float(row['p_double_or_worse'])
            pts = (
                e * DK_HOLE_POINTS['eagle_or_better'] +
                b * DK_HOLE_POINTS['birdie'] +
                p * DK_HOLE_POINTS['par'] +
                bo * DK_HOLE_POINTS['bogey'] +
                d * DK_HOLE_POINTS['double_or_worse']
            )
            totals[player] = totals.get(player, 0.0) + pts
    return totals

def load_sim(path):
    data = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = normalize_name(row['player_name'])
            data[name] = {
                'make_cut': float(row['make_cut']),
                'top_20': float(row['top_20']),
                'top_10': float(row['top_10']),
                'top_5': float(row['top_5']),
                'win': float(row['win']),
            }
    return data


def expected_finish_pts(info):
    win = info['win']
    top5 = info['top_5']
    top10 = info['top_10']
    top20 = info['top_20']

    pts = 0.0
    pts += FINISH_PTS['win'] * win
    pts += FINISH_PTS['2_5'] * max(0.0, top5 - win)
    pts += FINISH_PTS['6_10'] * max(0.0, top10 - top5)
    pts += FINISH_PTS['11_20'] * max(0.0, top20 - top10)
    return pts


def project_dk(hole_points, sim_data):
    results = []
    for player, r1_pts in hole_points.items():
        sim = sim_data.get(player)
        if not sim:
            continue
        rounds = 2 + 2 * sim['make_cut']
        finish = expected_finish_pts(sim)
        total = r1_pts * rounds + finish
        results.append({
            'player': player,
            'expected_points': round(total, 2),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description='Project DraftKings scoring.')
    parser.add_argument('--hole_probs', required=True, help='CSV with per-hole probabilities')
    parser.add_argument('--simulation', required=True, help='CSV with simulation probabilities')
    parser.add_argument('--output', required=True, help='Output CSV')
    args = parser.parse_args()

    hole_points = load_hole_points(args.hole_probs)
    sim_data = load_sim(args.simulation)
    results = project_dk(hole_points, sim_data)

    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['player', 'expected_points'])
        writer.writeheader()
        for row in sorted(results, key=lambda x: -x['expected_points']):
            writer.writerow(row)

if __name__ == '__main__':
    main()
