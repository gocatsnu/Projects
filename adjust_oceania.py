import csv

# Set of nationalities considered to be part of Oceania
OCEANIA_NATIONS = {"Australia", "New Zealand", "Fiji"}

# Read the nationality mapping
nationality_file = 'data/raw/golfer_nationalities.csv'
# We'll map dg_id (player_id) to nationality
id_to_nation = {}
with open(nationality_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        player_id = row['player_id']
        if player_id:
            id_to_nation[int(player_id)] = row['nationality']

# Read the original DG Model
input_file = 'outputs/The Open DG Model.csv'
output_file = 'outputs/Top Oceania.csv'
rows = []
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        dg_id = int(row['dg_id'])
        nationality = id_to_nation.get(dg_id)
        if nationality not in OCEANIA_NATIONS:
            row['my_pred'] = '-10'
        rows.append(row)

# Write adjusted CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['player_name', 'dg_id', 'my_pred'])
    writer.writeheader()
    writer.writerows(rows)
