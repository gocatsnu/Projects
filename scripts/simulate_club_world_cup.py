import argparse
import csv
import random
from itertools import combinations
from pathlib import Path

NU = 0.667
DELTA = 0.40


def prob_to_american(prob: float) -> str:
    """Return American odds string from a probability."""
    if prob <= 0 or prob >= 1:
        return ""
    if prob > 0.5:
        return str(int(round(-prob / (1 - prob) * 100)))
    return str(int(round((1 - prob) / prob * 100)))


def load_groups(path: str) -> dict:
    groups = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            groups.setdefault(row["Group"], []).append(row["Team"])
    return groups


def load_elos(path: str) -> dict:
    elos = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            elos[row["Team"]] = float(row.get("Updated_ELO") or row.get("Adjusted_ELO"))
    return elos


def wdl_probs(r_a: float, r_b: float, nu: float = NU) -> tuple:
    d = r_a - r_b
    alpha = 10 ** (d / 400)
    denom = alpha + 1 + nu * (alpha ** 0.5)
    p_win = alpha / denom
    p_draw = nu * (alpha ** 0.5) / denom
    return p_win, p_draw, 1 - p_win - p_draw


def adv_prob(r_a: float, r_b: float, nu: float = NU, delta: float = DELTA) -> float:
    p_w, p_d, _ = wdl_probs(r_a, r_b, nu)
    alpha_et = 10 ** ((r_a - r_b) / 1200)
    p_et_win_star = alpha_et / (1 + alpha_et)
    p_et_win = (1 - delta) * p_et_win_star
    p_et_draw = delta
    p_pen_win = max(0.40, min(0.60, 0.50 + 0.03 * ((r_a - r_b) / 400)))
    return p_w + p_d * (p_et_win + p_et_draw * p_pen_win)


def simulate_match(team_a: str, team_b: str, elos: dict) -> int:
    p_win, p_draw, p_loss = wdl_probs(elos[team_a], elos[team_b])
    r = random.random()
    if r < p_win:
        return 3, 0
    if r < p_win + p_draw:
        return 1, 1
    return 0, 3


def play_group(teams: list, elos: dict, played: dict) -> list:
    points = {t: 0 for t in teams}
    for (a, b), (pa, pb) in played.items():
        points[a] += pa
        points[b] += pb
    for a, b in combinations(teams, 2):
        if (a, b) in played or (b, a) in played:
            continue
        pa, pb = simulate_match(a, b, elos)
        points[a] += pa
        points[b] += pb
    return sorted(teams, key=lambda t: (points[t], elos[t]), reverse=True)


def run_sim(groups: dict, elos: dict, results: dict, n: int) -> dict:
    stages = {
        "group_winner": {t: 0 for t in elos},
        "knockout": {t: 0 for t in elos},
        "qf": {t: 0 for t in elos},
        "sf": {t: 0 for t in elos},
        "f": {t: 0 for t in elos},
        "champion": {t: 0 for t in elos},
    }
    for _ in range(n):
        group_order = {}
        for g, teams in groups.items():
            played = results.get(g, {})
            order = play_group(teams, elos, played)
            group_order[g] = order
            stages["group_winner"][order[0]] += 1
            stages["knockout"][order[0]] += 1
            stages["knockout"][order[1]] += 1
        # round of 16
        r16 = {
            49: (group_order['A'][0], group_order['B'][1]),
            50: (group_order['C'][0], group_order['D'][1]),
            51: (group_order['B'][0], group_order['A'][1]),
            52: (group_order['D'][0], group_order['C'][1]),
            53: (group_order['E'][0], group_order['F'][1]),
            54: (group_order['G'][0], group_order['H'][1]),
            55: (group_order['H'][0], group_order['G'][1]),
            56: (group_order['F'][0], group_order['E'][1]),
        }
        winners_r16 = {}
        for m, (a, b) in r16.items():
            pa = adv_prob(elos[a], elos[b])
            if random.random() < pa:
                w = a
            else:
                w = b
            winners_r16[m] = w
            stages['qf'][w] += 1
        # quarter finals
        qf = {
            57: (winners_r16[53], winners_r16[54]),
            58: (winners_r16[49], winners_r16[50]),
            59: (winners_r16[51], winners_r16[52]),
            60: (winners_r16[55], winners_r16[56]),
        }
        winners_qf = {}
        for m, (a, b) in qf.items():
            pa = adv_prob(elos[a], elos[b])
            w = a if random.random() < pa else b
            winners_qf[m] = w
            stages['sf'][w] += 1
        # semi finals
        sf = {
            61: (winners_qf[57], winners_qf[58]),
            62: (winners_qf[59], winners_qf[60]),
        }
        winners_sf = {}
        for m, (a, b) in sf.items():
            pa = adv_prob(elos[a], elos[b])
            w = a if random.random() < pa else b
            winners_sf[m] = w
            stages['f'][w] += 1
        # final
        a, b = winners_sf[61], winners_sf[62]
        pa = adv_prob(elos[a], elos[b])
        champ = a if random.random() < pa else b
        stages['champion'][champ] += 1
    for stage in stages:
        for team in stages[stage]:
            stages[stage][team] = stages[stage][team] * 100 / n
    return stages


def main() -> None:
    parser = argparse.ArgumentParser(description='Simulate Club World Cup')
    parser.add_argument('--teams_csv', default='data/raw/2025_Club_World_Cup_Teams.csv')
    parser.add_argument('--elos_csv', default='outputs/Updated_Club_World_Cup_ELO.csv')
    parser.add_argument('--sims', type=int, default=10000)
    parser.add_argument('--output', default='outputs/cwc_simulation.csv')
    parser.add_argument(
        '--fair_output',
        default='outputs/cwc_stage_fair_odds.csv',
        help='CSV with American odds for each stage',
    )
    args = parser.parse_args()

    groups = load_groups(args.teams_csv)
    elos = load_elos(args.elos_csv)

    played = {
        'A': {
            ('Al Ahly', 'Inter Miami'): (1, 1),
            ('Palmeiras', 'Porto'): (1, 1),
        },
        'B': {
            ('Botafogo', 'Seattle Sounders'): (3, 0),
            ('Paris Saint-Germain', 'Atletico Madrid'): (3, 0),
        },
        'C': {
            ('Bayern Munich', 'Auckland City'): (3, 0),
            ('Boca Juniors', 'Benfica'): (1, 1),
        },
        'D': {
            ('Flamengo', 'Esperance Sportive de Tunis'): (3, 0),
            ('Chelsea', 'Los Angeles FC'): (3, 0),
        },
    }

    stages = run_sim(groups, elos, played, args.sims)

    # order teams by group so output is grouped logically
    teams = [team for g in sorted(groups) for team in groups[g]]
    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Team',
            'GroupWinner%',
            'Knockout%',
            'Quarterfinal%',
            'Semifinal%',
            'Final%',
            'Champion%',
            'ChampionOdds',
        ])
        for t in teams:
            writer.writerow([
                t,
                round(stages['group_winner'][t], 2),
                round(stages['knockout'][t], 2),
                round(stages['qf'][t], 2),
                round(stages['sf'][t], 2),
                round(stages['f'][t], 2),
                round(stages['champion'][t], 2),
                prob_to_american(stages['champion'][t] / 100),
            ])

    with open(args.fair_output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Team',
            'GroupWinnerOdds',
            'KnockoutOdds',
            'QuarterfinalOdds',
            'SemifinalOdds',
            'FinalOdds',
            'ChampionOdds',
        ])
        for t in teams:
            writer.writerow([
                t,
                prob_to_american(stages['group_winner'][t] / 100),
                prob_to_american(stages['knockout'][t] / 100),
                prob_to_american(stages['qf'][t] / 100),
                prob_to_american(stages['sf'][t] / 100),
                prob_to_american(stages['f'][t] / 100),
                prob_to_american(stages['champion'][t] / 100),
            ])
    print(f'Simulation results saved to {args.output}')
    print(f'Fair odds saved to {args.fair_output}')


if __name__ == '__main__':
    main()
