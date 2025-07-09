import csv
import argparse


def normalize_name(name: str) -> str:
    name = name.strip().replace('"', '')
    if ',' in name:
        last, first = [n.strip() for n in name.split(',', 1)]
        return f"{first} {last}".lower()
    return name.lower()


def load_projections(path: str) -> dict:
    data = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = normalize_name(row.get('dk_name') or row.get('player'))
            val = row.get('total_points') or row.get('expected_points')
            if val is None or val == '':
                continue
            pts = float(val)
            data[key] = pts
            # handle common nickname differences
            if key == 'cameron davis':
                data['cam davis'] = pts
    return data


def main():
    parser = argparse.ArgumentParser(description='Match DK projections to upload template')
    parser.add_argument('--projections', required=True, help='CSV with DK projections')
    parser.add_argument('--template', required=True, help='DK upload template CSV')
    parser.add_argument('--output', required=True, help='Output CSV path')
    args = parser.parse_args()

    my_proj = load_projections(args.projections)

    with open(args.template, encoding='utf-8-sig') as inp, open(args.output, 'w', newline='') as out:
        reader = csv.DictReader(inp)
        fieldnames = [f for f in reader.fieldnames if f != 'import_advice']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            name = row['player_name']
            if name in my_proj:
                row['my_proj'] = round(my_proj[name], 1)
            writer.writerow({k: row.get(k, '') for k in fieldnames})


if __name__ == '__main__':
    main()
