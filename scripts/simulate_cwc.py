import csv
import random
import re
from collections import defaultdict
from pathlib import Path

from add_club_world_cup_elo import (
    normalize,
    load_world_elo,
    load_europe_elo,
    lookup,
)

NU = 0.667
DELTA = 0.40


def parse_structure(path: str) -> dict:
    groups = {}
    current = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("## Knockout Stage"):
                break
            m = re.match(r"### Group ([A-H])", line)
            if m:
                current = m.group(1)
                groups[current] = []
                continue
            if current and line.lstrip().startswith("-"):
                team = re.sub(r"^-\s*", "", line.strip())
                team = re.sub(r"\([^)]*\)", "", team).strip()
                if team:
                    groups[current].append(team)
    return groups


def load_adjusted_elos(path: str) -> dict:
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                elo = int(row["Adjusted_ELO"])
            except ValueError:
                continue
            mapping[normalize(row["Team"])] = elo
    return mapping


def fetch_missing_elo(team: str, world_map: dict, euro_map: dict) -> int:
    w = lookup(team, world_map)
    e = lookup(team, euro_map)
    if w and e:
        return round(0.8 * e["elo"] + 0.2 * w["elo"])
    if w:
        return w["elo"]
    if e:
        return e["elo"]
    raise KeyError(f"No Elo for {team}")


def get_elo(team: str, mapping: dict, world_map: dict, euro_map: dict) -> int:
    key = normalize(team)
    if key not in mapping:
        mapping[key] = fetch_missing_elo(team, world_map, euro_map)
    return mapping[key]


def elo_win_draw_loss(ra: int, rb: int) -> tuple:
    alpha_a = 10 ** (ra / 400)
    alpha_b = 10 ** (rb / 400)
    denom = alpha_a + alpha_b + NU * (alpha_a * alpha_b) ** 0.5
    p_win = alpha_a / denom
    p_draw = NU * (alpha_a * alpha_b) ** 0.5 / denom
    return p_win, p_draw, 1 - p_win - p_draw


def adv_prob(ra: int, rb: int) -> float:
    p_w, p_d, _ = elo_win_draw_loss(ra, rb)
    d = ra - rb
    alpha_et = 10 ** ((d / 3) / 400)
    p_et_win_star = alpha_et / (1 + alpha_et)
    p_et_win = (1 - DELTA) * p_et_win_star
    p_et_draw = DELTA
    p_pen = 0.50 + 0.03 * (d / 400)
    p_pen = min(0.60, max(0.40, p_pen))
    return p_w + p_d * (p_et_win + p_et_draw * p_pen)


def simulate_group(teams: list, elo_map: dict, world_map: dict, euro_map: dict) -> tuple:
    pts = {t: 0 for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            a = teams[i]
            b = teams[j]
            ra = get_elo(a, elo_map, world_map, euro_map)
            rb = get_elo(b, elo_map, world_map, euro_map)
            p_win_a, p_draw, _ = elo_win_draw_loss(ra, rb)
            r = random.random()
            if r < p_win_a:
                pts[a] += 3
            elif r < p_win_a + p_draw:
                pts[a] += 1
                pts[b] += 1
            else:
                pts[b] += 3
    ranked = sorted(teams, key=lambda t: (pts[t], get_elo(t, elo_map, world_map, euro_map)), reverse=True)
    return ranked, pts


def play(a: str, b: str, elo_map: dict, world_map: dict, euro_map: dict) -> str:
    ra = get_elo(a, elo_map, world_map, euro_map)
    rb = get_elo(b, elo_map, world_map, euro_map)
    return a if random.random() < adv_prob(ra, rb) else b


def simulate(iterations: int = 1000):
    groups = parse_structure("data/raw/club_world_cup_2025_structure.md")
    elo_map = load_adjusted_elos("data/raw/2025_Club_World_Cup_Teams_with_ELO.csv")
    world_map = load_world_elo("data/raw/Football ELO World.csv")
    euro_map = load_europe_elo("data/raw/Europe Soccer ELO.csv")

    teams = [t for g in groups.values() for t in g]
    stats = {t: defaultdict(int) for t in teams}

    r16_pairs = [
        ("A1", "B2"),
        ("C1", "D2"),
        ("B1", "A2"),
        ("D1", "C2"),
        ("E1", "F2"),
        ("G1", "H2"),
        ("H1", "G2"),
        ("F1", "E2"),
    ]
    qf_pairs = [
        ("53", "54"),
        ("49", "50"),
        ("51", "52"),
        ("55", "56"),
    ]
    sf_pairs = [("57", "58"), ("59", "60")]

    for _ in range(iterations):
        group_order = {}
        for letter, gteams in groups.items():
            ranked, _ = simulate_group(gteams, elo_map, world_map, euro_map)
            group_order[f"{letter}1"] = ranked[0]
            group_order[f"{letter}2"] = ranked[1]
            stats[ranked[0]]["group_win"] += 1
            stats[ranked[0]]["knockout"] += 1
            stats[ranked[1]]["knockout"] += 1

        winners = {}
        for idx, (a_key, b_key) in enumerate(r16_pairs, start=49):
            winner = play(group_order[a_key], group_order[b_key], elo_map, world_map, euro_map)
            winners[str(idx)] = winner
            stats[winner]["quarterfinal"] += 1

        next_round = {}
        for idx, (a_m, b_m) in enumerate(qf_pairs, start=57):
            winner = play(winners[a_m], winners[b_m], elo_map, world_map, euro_map)
            next_round[str(idx)] = winner
            stats[winner]["semifinal"] += 1

        finalists = {}
        for idx, (a_m, b_m) in enumerate(sf_pairs, start=61):
            winner = play(next_round[a_m], next_round[b_m], elo_map, world_map, euro_map)
            finalists[str(idx)] = winner
            stats[winner]["final"] += 1

        champion = play(finalists["61"], finalists["62"], elo_map, world_map, euro_map)
        stats[champion]["champion"] += 1

    for team in teams:
        rec = stats[team]
        for key in rec:
            rec[key] /= iterations
    return stats


if __name__ == "__main__":
    results = simulate(5000)
    for team, rec in sorted(results.items(), key=lambda x: -x[1]["champion"]):
        print(team)
        for stage in ["group_win", "knockout", "quarterfinal", "semifinal", "final", "champion"]:
            print(f"  {stage}: {rec.get(stage, 0):.3f}")

    out_path = Path("outputs/cwc_simulation_results.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["team", "group_win", "knockout", "quarterfinal", "semifinal", "final", "champion"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for team, rec in sorted(results.items(), key=lambda x: -x[1]["champion"]):
            row = {"team": team}
            for stage in fields[1:]:
                row[stage] = round(rec.get(stage, 0), 3)
            writer.writerow(row)
    print(f"Wrote results to {out_path}")
