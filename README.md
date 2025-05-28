# Golf Betting Projections

This repository contains data files and a simple script for producing market-adjusted stroke projections for the 2025 Charles Schwab Challenge.

## Data Files

- `DG Strokes Charles Schwab 20250520.csv` – baseline strokes projections from DataGolf.
- `Charles Schwab 2025 72 Hole 20250520.csv` – head-to-head matchup odds from various sportsbooks.

## Script

`scripts/adjust_projections.py` reads the two CSV files and produces `Adjusted Strokes Charles Schwab 20250520.csv`. The script converts available odds from BetOnline, BetCris, and Pinnacle to implied probabilities, infers expected stroke differences, and nudges the DataGolf projections toward the market view.

Run the script with:

```bash
python3 scripts/adjust_projections.py
```

The resulting CSV lists each player with the original and adjusted stroke projection.


`scripts/fair_odds.py` calculates fair head-to-head odds for any matchup in the `72 Hole` CSV that lacks a BetOnline, BetCris, or Pinnacle line. The script uses the adjusted stroke predictions and assumes a player scoring standard deviation of 4.5 strokes per tournament. It also pulls available prices from DraftKings, Bet365, FanDuel, BetMGM, PointsBet, Bovada, Caesars, and Unibet and computes the expected value of each.

For each listed matchup, the script uses DataGolf stroke projections to estimate a fair win probability. For markets where BetOnline, BetCris, or Pinnacle prices are missing, it pulls available odds from other sportsbooks. Each price is converted to an implied probability and its expected value (EV), calculated as:

```
EV = fair_prob_p1 * payout - (1 - fair_prob_p1)
```
where `payout` is the decimal return for a winning bet.

Run with:

```bash
python3 scripts/fair_odds.py
```

It outputs `Projected Fair Odds Charles Schwab 20250520.csv` containing the fair probabilities and their equivalent American odds (`fair_odds_p1` and `fair_odds_p2`). The CSV also lists each sportsbook's offered price with the expected value of a wager at that line so you can easily compare the market to the model.

Production outputs from the scripts are saved in the `outputs/` directory. Those generated CSVs are typically the only outputs that get committed to version control.

## Muirfield Hole Scores

`scripts/scrape_hole_scores.py` downloads hole-by-hole scoring data from DataGolf's API. Provide the event slug, a year range, and your API key:

```bash
python3 scripts/scrape_hole_scores.py the-memorial-tournament 2020 2024 YOUR_KEY
```

The script writes `outputs/muirfield_hole_scores.csv` with one row per hole showing the year, player name, round, hole number, and raw score.

