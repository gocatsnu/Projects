import argparse
import csv

parser = argparse.ArgumentParser(
    description="Compute strokes gained from a strokes projection CSV"
)
parser.add_argument("input_path", help="CSV with baseline/adjusted strokes")
parser.add_argument("output_path", help="Where to write the strokes gained file")
parser.add_argument(
    "--info",
    dest="info_path",
    default=None,
    help="Tournament info CSV with Course Par, Field Strength, and Scoring Prediction",
)
parser.add_argument(
    "--avg-score",
    dest="avg_score",
    type=float,
    default=73.05,
    help="Fallback average score if --info is not provided",
)
args = parser.parse_args()

input_path = args.input_path
output_path = args.output_path
avg_score = args.avg_score

info_path = args.info_path
if info_path:
    info = {}
    with open(info_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            key = row[1].strip().lower()
            info[key] = row[2].strip()
    par = float(info.get("course par", 72))
    field = float(info.get("field strength", 0))
    scoring = float(info.get("scoring prediction", 0))
    avg_score = par + field + scoring

rows = []
with open(input_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('PLAYER NAME')
        if not name:
            continue
        try:
            adjusted = float(row.get('ADJUSTED STROKES') or row.get('STROKES'))
        except (TypeError, ValueError):
            continue
        baseline = row.get('BASELINE STROKES')
        baseline = float(baseline) if baseline else None
        gained = round(avg_score - adjusted, 3)
        if baseline is not None:
            rows.append([name.strip(), baseline, adjusted, gained])
        else:
            rows.append([name.strip(), adjusted, gained])

with open(output_path, 'w', newline='') as f:
    if rows and len(rows[0]) == 4:
        writer = csv.writer(f)
        writer.writerow(['PLAYER NAME', 'BASELINE STROKES', 'ADJUSTED STROKES', 'STROKES GAINED'])
        for row in rows:
            writer.writerow(row)
    else:
        writer = csv.writer(f)
        writer.writerow(['PLAYER NAME', 'ADJUSTED STROKES', 'STROKES GAINED'])
        for row in rows:
            writer.writerow(row)

print('Wrote', len(rows), 'rows to', output_path)
