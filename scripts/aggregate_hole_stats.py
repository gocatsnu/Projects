import csv
import argparse
from collections import defaultdict


def aggregate(paths, years_label, course, rounds):
    agg = {}
    for path in paths:
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['round_num'] not in rounds:
                    continue
                h = int(row['hole_num'])
                par = int(row['hole_par'])
                yard = row.get('hole_yardage') or ''
                e = int(row['eagles_or_better'])
                b = int(row['birdies'])
                p = int(row['pars'])
                bo = int(row['bogeys'])
                d = int(row['doubles_or_worse'])
                if h not in agg:
                    agg[h] = {
                        'par': par,
                        'yard': yard,
                        'eagle': 0,
                        'birdie': 0,
                        'par_ct': 0,
                        'bogey': 0,
                        'double': 0,
                    }
                agg[h]['eagle'] += e
                agg[h]['birdie'] += b
                agg[h]['par_ct'] += p
                agg[h]['bogey'] += bo
                agg[h]['double'] += d
                agg[h]['yard'] = yard
                agg[h]['par'] = par
    rows = []
    for h in sorted(agg):
        info = agg[h]
        total = info['eagle'] + info['birdie'] + info['par_ct'] + info['bogey'] + info['double']
        scoring_avg = (
            info['eagle'] * (info['par'] - 2) +
            info['birdie'] * (info['par'] - 1) +
            info['par_ct'] * info['par'] +
            info['bogey'] * (info['par'] + 1) +
            info['double'] * (info['par'] + 2)
        ) / total
        rel = scoring_avg - info['par']
        rows.append({
            'tournament_year': years_label,
            'course_name': course,
            'round_num': 1,
            'hole_num': h,
            'hole_par': info['par'],
            'hole_yardage': info['yard'],
            'scoring_avg': scoring_avg,
            'rel_scoring_avg': rel,
            'eagles_or_better': info['eagle'],
            'birdies': info['birdie'],
            'pars': info['par_ct'],
            'bogeys': info['bogey'],
            'doubles_or_worse': info['double'],
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description='Aggregate hole stats across years')
    parser.add_argument('files', nargs='+', help='Input CSV files')
    parser.add_argument('--label', required=True, help='Year label for output (e.g., 2021-2024)')
    parser.add_argument('--course', required=True, help='Course name for output rows')
    parser.add_argument('--rounds', default='1', help='Comma separated round numbers to include (e.g., 1,2,3)')
    parser.add_argument('--output', required=True, help='Output CSV path')
    args = parser.parse_args()

    rounds = {r.strip() for r in args.rounds.split(',') if r.strip()}

    rows = aggregate(args.files, args.label, args.course, rounds)
    with open(args.output, 'w', newline='') as f:
        fieldnames = ['tournament_year','course_name','round_num','hole_num','hole_par','hole_yardage','scoring_avg','rel_scoring_avg','eagles_or_better','birdies','pars','bogeys','doubles_or_worse']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == '__main__':
    main()
