import csv
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]
avg_score = 73.05

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
