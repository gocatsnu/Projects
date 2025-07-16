import csv

NATIONALITY_CSV = 'data/raw/golfer_nationalities.csv'
BASE_MODEL = 'outputs/The Open DG Model.csv'
OUTPUT_CSV = 'outputs/Top Asia.csv'

ASIA_COUNTRIES = {
    'Armenia',
    'Bahrain',
    'Bangladesh',
    'China',
    'Chinese Taipei',
    'Hong Kong',
    'India',
    'Israel',
    'Japan',
    'Korea - Republic of',
    'Malaysia',
    'Oman',
    'Pakistan',
    'Philippines',
    'Qatar',
    'Russian Federation',
    'Saudi Arabia',
    'Singapore',
    'Sri Lanka',
    'Thailand',
    'Turkey',
    'United Arab Emirates',
}

def load_country_mapping():
    mapping = {}
    with open(NATIONALITY_CSV, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('player_id'):
                mapping[row['player_id']] = row['nationality']
    return mapping


def main():
    mapping = load_country_mapping()
    with open(BASE_MODEL, encoding='utf-8-sig') as inp, open(OUTPUT_CSV, 'w', newline='') as out:
        reader = csv.DictReader(inp)
        writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            nationality = mapping.get(row['dg_id'], '')
            if nationality not in ASIA_COUNTRIES:
                row['my_pred'] = '-10'
            writer.writerow(row)


if __name__ == '__main__':
    main()
