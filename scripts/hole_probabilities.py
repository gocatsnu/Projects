import csv
import argparse
from statistics import mean
from collections import defaultdict
import math


def read_hole_stats(path, rounds=None):
    holes = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if rounds and row["round_num"] not in rounds:
                continue
            h = int(row["hole_num"])
            par = int(row["hole_par"])
            counts = {
                "eagle": int(row["eagles_or_better"]),
                "birdie": int(row["birdies"]),
                "par": int(row["pars"]),
                "bogey": int(row["bogeys"]),
                "double": int(row["doubles_or_worse"]),
            }
            total = sum(counts.values())
            probs = {k: v / total for k, v in counts.items()}
            values = {
                "eagle": par - 2,
                "birdie": par - 1,
                "par": par,
                "bogey": par + 1,
                "double": par + 2,
            }
            mean_val = sum(probs[k] * values[k] for k in probs)
            var_val = sum(probs[k] * (values[k] - mean_val) ** 2 for k in probs)
            holes[h] = {
                "par": par,
                "probs": probs,
                "mean": mean_val,
                "var": var_val,
            }
    return holes


def read_player_projections(path):
    players = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            players.append({
                "name": row["PLAYER NAME"],
                "baseline": float(row["BASELINE STROKES"]),
                "adjusted": float(row["ADJUSTED STROKES"]),
            })
    return players


def normal_cdf(x, mu, sigma):
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def compute_probabilities(players, holes, avg_field):
    results = []
    for p in players:
        delta = p["adjusted"] - avg_field
        shift = delta / 18.0
        for hole_num, info in holes.items():
            mu_new = info["mean"] + shift
            sigma = math.sqrt(info["var"])
            par = info["par"]
            # normal approximation boundaries
            b_eagle = normal_cdf(par - 1.5, mu_new, sigma)
            b_birdie = normal_cdf(par - 0.5, mu_new, sigma)
            b_par = normal_cdf(par + 0.5, mu_new, sigma)
            b_bogey = normal_cdf(par + 1.5, mu_new, sigma)
            p_eagle = b_eagle
            p_birdie = max(0.0, b_birdie - b_eagle)
            p_par = max(0.0, b_par - b_birdie)
            p_bogey = max(0.0, b_bogey - b_par)
            p_double = max(0.0, 1.0 - b_bogey)
            results.append({
                "player": p["name"],
                "hole": hole_num,
                "par": par,
                "p_eagle_or_better": p_eagle,
                "p_birdie": p_birdie,
                "p_par": p_par,
                "p_bogey": p_bogey,
                "p_double_or_worse": p_double,
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="Compute hole-by-hole score probabilities")
    parser.add_argument("--holes", required=True, help="CSV with hole stats")
    parser.add_argument("--projections", required=True, help="CSV with player round projections")
    parser.add_argument("--output", required=True, help="Output CSV")
    parser.add_argument("--rounds", default="1", help="Comma separated round numbers to include from hole stats")
    args = parser.parse_args()

    rounds = {r.strip() for r in args.rounds.split(',') if r.strip()}
    holes = read_hole_stats(args.holes, rounds if rounds else None)
    players = read_player_projections(args.projections)
    avg_field = mean(p["adjusted"] for p in players)

    results = compute_probabilities(players, holes, avg_field)

    with open(args.output, "w", newline="") as f:
        fieldnames = ["player", "hole", "par", "p_eagle_or_better", "p_birdie", "p_par", "p_bogey", "p_double_or_worse"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

if __name__ == "__main__":
    main()
