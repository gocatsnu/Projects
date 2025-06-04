import csv
import math
from collections import OrderedDict

# Helper copied from adjust_projections.py

def american_to_prob(odds: str) -> float:
    """Convert American odds to implied probability."""
    o = int(odds)
    if o > 0:
        return 100 / (o + 100)
    return -o / (-o + 100)


def prob_to_american(prob: float) -> int:
    """Convert probability to American odds (rounded)."""
    if prob <= 0 or prob >= 1:
        raise ValueError("prob must be between 0 and 1")
    if prob > 0.5:
        return int(round(-prob / (1 - prob) * 100))
    return int(round((1 - prob) / prob * 100))


def prob_to_decimal(prob: float) -> float:
    """Return decimal odds from win probability."""
    return 1 / prob


def american_to_decimal(odds: str) -> float:
    o = int(odds)
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)


SIGMA_DIFF = 6.0


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def load_strokes(path: str) -> dict:
    strokes = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "ADJUSTED STROKES" in row:
                val = row["ADJUSTED STROKES"]
            else:
                val = row.get("STROKES PREDICTION")
            if val is None or val == "":
                continue
            strokes[row["PLAYER NAME"].strip()] = float(val)
    return strokes


def fair_probability(diff: float) -> float:
    """Probability player1 beats player2 given stroke difference."""
    return norm_cdf(-diff / SIGMA_DIFF)


BOOKS_PRIMARY = ["betonline", "betcris", "pinnacle"]
BOOKS_EXTRA = [
    "draftkings",
    "bet365",
    "fanduel",
    "betmgm",
    "pointsbet",
    "bovada",
    "caesars",
    "unibet",
]
ALL_BOOKS = BOOKS_PRIMARY + BOOKS_EXTRA


def process(matchups_path: str, strokes_path: str, out_path: str) -> None:
    strokes = load_strokes(strokes_path)
    output_rows = []

    with open(matchups_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            p1 = row["name_p1"].strip()
            p2 = row["name_p2"].strip()
            if p1 not in strokes or p2 not in strokes:
                continue
            diff = strokes[p1] - strokes[p2]
            fair_prob_p1 = fair_probability(diff)
            res = OrderedDict(
                [
                    ("name_p1", p1),
                    ("name_p2", p2),
                    ("fair_prob_p1", round(fair_prob_p1, 4)),
                    ("fair_prob_p2", round(1 - fair_prob_p1, 4)),
                    ("fair_odds_p1", prob_to_american(fair_prob_p1)),
                    ("fair_odds_p2", prob_to_american(1 - fair_prob_p1)),
                ]
            )

            has_primary = any(
                row.get(f"{b}_p1") not in ("", None, "null") for b in BOOKS_PRIMARY
            )

            for book in ALL_BOOKS:
                val = row.get(f"{book}_p1")
                if (book in BOOKS_EXTRA and not has_primary) or (book in BOOKS_PRIMARY):
                    if val and val != "null":
                        res[f"{book}_p1"] = val
                        payout = american_to_decimal(val)
                        ev = fair_prob_p1 * payout - 1
                        res[f"{book}_ev_p1"] = round(ev, 4)
                    else:
                        res[f"{book}_p1"] = ""
                        res[f"{book}_ev_p1"] = ""
            output_rows.append(res)

    fieldnames = list(output_rows[0].keys()) if output_rows else []
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    process(
        "Charles Schwab 2025 72 Hole 20250520.csv",
        "DG Strokes Charles Schwab 20250520.csv",
        "Projected Fair Odds Charles Schwab 20250520.csv",
    )
