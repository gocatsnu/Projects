import csv
import sys

pre_r1_path = sys.argv[1]
pre_r2_path = sys.argv[2]
output_path = sys.argv[3]

pre_r1 = {}
with open(pre_r1_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('PLAYER NAME')
        if not name:
            continue
        val = row.get('ADJUSTED STROKES') or row.get('STROKES')
        if val:
            pre_r1[name.strip()] = float(val)

rows = []
with open(pre_r2_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('PLAYER NAME')
        if not name:
            continue
        val = row.get('ADJUSTED STROKES') or row.get('STROKES')
        if not val:
            continue
        r2 = float(val)
        r1 = pre_r1.get(name.strip())
        if r1 is None:
            continue
        rows.append([name.strip(), r1, r2, round(r2 - r1, 3)])

with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['PLAYER NAME', 'PRE R1 STROKES', 'PRE R2 STROKES', 'DIFFERENCE'])
    for row in rows:
        writer.writerow(row)

print('Wrote', len(rows), 'rows to', output_path)
