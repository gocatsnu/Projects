import csv
import sys

sg_path = sys.argv[1]
template_path = sys.argv[2]
output_path = sys.argv[3]

# Load strokes gained data keyed by normalized player name
sg_data = {}
with open(sg_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['PLAYER NAME'].strip('"')
        if ',' in name:
            last, first = name.split(',', 1)
            key = f"{first.strip()} {last.strip()}".lower()
        else:
            key = name.lower()
        sg_data[key] = row['STROKES GAINED']

with open(template_path, encoding='utf-8-sig') as inp, open(output_path, 'w', newline='') as out:
    reader = csv.DictReader(inp)
    fieldnames = [f for f in reader.fieldnames if f != 'import_advice']
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        key = row['player_name']
        if key in sg_data:
            row['my_pred'] = sg_data[key]
        writer.writerow({k: row.get(k, '') for k in fieldnames})
print('Wrote', output_path)
