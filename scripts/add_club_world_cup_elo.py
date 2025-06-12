import csv
import re
import unicodedata
from difflib import get_close_matches


def normalize(name: str) -> str:
    """Normalize club names for matching."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"\b(fc|cf|sc|afc|club)\b", "", name)
    name = name.replace("&", "and")
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return re.sub(r"\s+", " ", name).strip()


TEAM_SYNONYMS = {
    normalize("Bayern Munich"): ["bayern munchen", "bayern"],
    normalize("Paris Saint-Germain"): ["paris sg", "psg"],
    normalize("Manchester City"): ["man city"],
    normalize("Inter Milan"): ["inter"],
    normalize("AC Milan"): ["milan"],
    normalize("Borussia Dortmund"): ["dortmund"],
    normalize("Seattle Sounders"): ["seattle sounders fc"],
    normalize("Inter Miami"): ["inter miami cf"],
    normalize("Fluminense"): ["fluminense fc"],
    normalize("Mamelodi Sundowns"): ["mamelodi sundowns fc"],
    normalize("Al Ain"): ["al ain fc", "al-ain fc"],
    normalize("FC Salzburg"): ["red bull salzburg", "rb salzburg"],
    normalize("Wydad AC"): ["wydad casablanca"],
    normalize("CF Monterrey"): ["monterrey"],
    normalize("Al Hilal"): ["al hilal saudi"],
}


def load_world_elo(path: str) -> dict:
    mapping = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[normalize(row["Club"])] = {
                "club": row["Club"],
                "country": row["Country"],
                "elo": int(row["ELO"]),
            }
    return mapping


def load_europe_elo(path: str) -> dict:
    mapping = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if row and row[0].strip():
                try:
                    elo = int(row[1])
                except ValueError:
                    continue
                mapping[normalize(row[0])] = {"club": row[0], "elo": elo}
    return mapping


def lookup(name: str, mapping: dict, cutoff: float = 0.75):
    n = normalize(name)
    candidates = [n] + [normalize(s) for s in TEAM_SYNONYMS.get(n, [])]
    for cand in candidates:
        if cand in mapping:
            return mapping[cand]
    for cand in candidates:
        match = get_close_matches(cand, mapping.keys(), n=1, cutoff=cutoff)
        if match:
            return mapping[match[0]]
    return None


def main():
    world_map = load_world_elo("data/raw/Football ELO World.csv")
    euro_map = load_europe_elo("data/raw/Europe Soccer ELO.csv")

    output_rows = []
    with open("data/raw/2025_Club_World_Cup_Teams.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = lookup(row["Team"], world_map)
            e = lookup(row["Team"], euro_map)
            row["World_ELO"] = w["elo"] if w else ""
            row["Europe_ELO"] = e["elo"] if e else ""
            output_rows.append(row)

    out_path = "data/raw/2025_Club_World_Cup_Teams_with_ELO.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Team", "Group", "Country", "World_ELO", "Europe_ELO"]
        )
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
