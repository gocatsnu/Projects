import csv
import math


def phi(x: float) -> float:
    """Standard normal CDF using the error function."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def prob_to_american(p: float) -> tuple[int, int]:
    """Convert win probability to American odds for both sides."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1")
    if abs(p - 0.5) < 1e-9:
        return -110, -110
    if p > 0.5:
        odds = -(p / (1 - p)) * 100
        return int(round(odds)), int(round(-10000 / odds))
    odds = ((1 - p) / p) * 100
    return int(round(10000 / odds)), int(round(-odds))


def american_to_prob(odds: str) -> float:
    """Convert American odds string to implied probability."""
    o = int(odds)
    if o > 0:
        return 100 / (o + 100)
    return -o / (-o + 100)


def payout_decimal(odds: str) -> float:
    """Return decimal payout for a $1 stake at given American odds."""
    o = int(odds)
    if o > 0:
        return 1 + o / 100
    return 1 + 100 / (-o)


def load_adjusted(path):
    data = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row['PLAYER NAME'].strip()] = float(row['ADJUSTED STROKES'])
    return data


def fair_odds(matchup_csv: str, strokes: dict[str, float], out_csv: str) -> None:
    """Compute fair odds and expected value for head-to-head matchups."""
    sigma_player = 4.5
    sigma_diff = math.sqrt(2) * sigma_player
    books = [
        "draftkings",
        "bet365",
        "fanduel",
        "betmgm",
        "pointsbet",
        "bovada",
        "caesars",
        "unibet",
    ]

    out_rows = []
    seen = set()
    with open(matchup_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            p1 = row["name_p1"].strip()
            p2 = row["name_p2"].strip()
            pair = tuple(sorted((p1, p2)))
            if pair in seen:
                continue
            seen.add(pair)

            has_market = any(
                row[col] not in ("", "null")
                for col in ("betonline_p1", "betcris_p1", "pinnacle_p1")
            )
            if has_market:
                continue
            if p1 not in strokes or p2 not in strokes:
                continue

            diff = strokes[p1] - strokes[p2]
            win_prob = phi(-diff / sigma_diff)
            odds_p1, odds_p2 = prob_to_american(win_prob)

            rec = {
                "p1": p1,
                "p2": p2,
                "fair_prob_p1": f"{win_prob:.4f}",
                "fair_odds_p1": odds_p1,
                "fair_odds_p2": odds_p2,
            }

            for book in books:
                p1_col = f"{book}_p1"
                p2_col = f"{book}_p2"
                val1 = row.get(p1_col, "")
                val2 = row.get(p2_col, "")
                if val1 not in ("", "null"):
                    try:
                        payout1 = payout_decimal(val1)
                        ev1 = win_prob * payout1 - 1
                        rec[p1_col] = int(val1)
                        rec[f"{book}_ev_p1"] = f"{ev1:.4f}"
                    except Exception:
                        pass
                if val2 not in ("", "null"):
                    try:
                        payout2 = payout_decimal(val2)
                        ev2 = (1 - win_prob) * payout2 - 1
                        rec[p2_col] = int(val2)
                        rec[f"{book}_ev_p2"] = f"{ev2:.4f}"
                    except Exception:
                        pass

            out_rows.append(rec)

    fieldnames = ["p1", "p2", "fair_prob_p1", "fair_odds_p1", "fair_odds_p2"]
    for book in books:
        fieldnames.extend(
            [f"{book}_p1", f"{book}_ev_p1", f"{book}_p2", f"{book}_ev_p2"]
        )

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print("Wrote", len(out_rows), "projected odds to", out_csv)


if __name__ == '__main__':
    strokes = load_adjusted('Adjusted Strokes Charles Schwab 20250520.csv')
    fair_odds('Charles Schwab 2025 72 Hole 20250520.csv', strokes,
              'Projected Fair Odds Charles Schwab 20250520.csv')
