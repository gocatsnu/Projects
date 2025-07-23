import argparse
import csv
import math
from typing import Dict, List, Tuple

from adjust_projections import american_to_prob, phi_inv, adjust_strokes


def load_per_round_strokes(path: str) -> Dict[str, float]:
    """Load per-round stroke projections."""
    data = {}
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("PLAYER NAME")
            val = row.get("PROJECTED STROKES")
            if not name or not val:
                continue
            try:
                data[name.strip("\" ")] = float(val)
            except ValueError:
                continue
    return data


def parse_matchups_per_round(path: str, strokes: Dict[str, float], holes: int) -> List[Tuple[str, str, float, float]]:
    """Parse matchup CSV and return per-round implied stroke differences."""
    pairs = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.strip().lower(): v for k, v in row.items()}
            p1 = row.get("name_p1", "").strip()
            p2 = row.get("name_p2", "").strip()
            if p1 not in strokes or p2 not in strokes:
                continue

            probs = []
            for col in ("betcris_p1", "betonline_p1", "pinnacle_p1"):
                val = row.get(col)
                if not val or val == "null":
                    continue
                try:
                    p1_prob = american_to_prob(val)
                except Exception:
                    continue
                val2 = row.get(col.replace("_p1", "_p2"))
                if val2 and val2 != "null":
                    try:
                        p2_prob = american_to_prob(val2)
                        s = p1_prob + p2_prob
                        if s > 0:
                            p1_prob = p1_prob / s
                    except Exception:
                        pass
                probs.append(p1_prob)
            if not probs:
                continue

            prob_p1 = sum(probs) / len(probs)
            sigma_round = 2.5
            if holes == 18:
                sigma_diff = math.sqrt(2) * sigma_round
                implied = -sigma_diff * phi_inv(prob_p1)
            else:
                n_rounds = holes // 18
                sigma_diff = math.sqrt(n_rounds * 2) * sigma_round
                implied = -sigma_diff * phi_inv(prob_p1) / n_rounds

            dg_diff = strokes[p1] - strokes[p2]
            pairs.append((p1, p2, dg_diff, implied))
    return pairs


def main():
    parser = argparse.ArgumentParser(description="Adjust per-round strokes using market matchups")
    parser.add_argument("--strokes", required=True, help="CSV with per-round stroke projections")
    parser.add_argument("--r1", required=True, help="Round 1 matchup odds CSV")
    parser.add_argument(
        "--t72",
        required=True,
        help="Multi-round matchup odds CSV (e.g. 72-hole for PGA, 54-hole for LIV)",
    )
    parser.add_argument(
        "--holes",
        type=int,
        default=72,
        help="Number of holes for the tournament matchups (default 72)",
    )
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    strokes = load_per_round_strokes(args.strokes)
    pairs = []
    pairs.extend(parse_matchups_per_round(args.r1, strokes, holes=18))
    pairs.extend(parse_matchups_per_round(args.t72, strokes, holes=args.holes))

    adjusted = adjust_strokes(strokes, pairs)

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "PLAYER NAME",
            "PROJECTED STROKES",
            "ADJUSTED STROKES",
            "DELTA",
        ])
        for name in sorted(adjusted):
            orig = strokes.get(name, "")
            adj = adjusted[name]
            delta = adj - orig if orig != "" else ""
            writer.writerow([name, orig, round(adj, 3), round(delta, 3)])

    print(f"Wrote adjusted strokes for {len(adjusted)} players to {args.output}")


if __name__ == "__main__":
    main()
