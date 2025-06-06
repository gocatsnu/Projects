# Golf Betting Projections

This repository contains data files and a simple script for producing market-adjusted stroke projections for the 2025 Charles Schwab Challenge.

## Data Files

- `DG Strokes Charles Schwab 20250520.csv` – baseline strokes projections from DataGolf.
- `Charles Schwab 2025 72 Hole 20250520.csv` – head-to-head matchup odds from various sportsbooks.

## Script

`scripts/adjust_projections.py` reads one or more matchup CSV files and produces an adjusted strokes file. It converts available odds from BetOnline, BetCris, and Pinnacle to implied probabilities, infers expected stroke differences, and nudges the DataGolf projections toward the market view.

Run the script with:

```bash
python3 scripts/adjust_projections.py \
  --strokes "Canadian Open DG Thursday Strokes 20250602.csv" \
  --matchups "Canadian Open 72 Hole Matchups 20250604.csv" \
  --matchups "Canadian Open r1 match ups 20250604.csv" \
  --output "Adjusted Strokes Canadian Open 20250604.csv"
```

For a LIV event (54 holes), include `--holes 54` and supply the LIV matchup files:

```bash
python3 scripts/adjust_projections.py \
  --strokes "LIV Golf DG Thursday Strokes 20250605.csv" \
  --matchups "LIV Virginia 54 Hole Matchup Odds 20250605.csv" \
  --matchups "LIV VIrginia r1 matchup Odds 20250605.csv" \
  --holes 54 \
  --output "Adjusted Strokes LIV Virginia 20250605.csv"
```

The resulting CSV lists each player with the original and adjusted stroke projection.


`scripts/fair_odds.py` calculates fair head-to-head odds for any matchup in the `72 Hole` CSV that lacks a BetOnline, BetCris, or Pinnacle line. The script uses the adjusted stroke predictions and assumes a player scoring standard deviation of 4.5 strokes per tournament. It also pulls available prices from DraftKings, Bet365, FanDuel, BetMGM, PointsBet, Bovada, Caesars, and Unibet and computes the expected value of each.

For each listed matchup, the script uses DataGolf stroke projections to estimate a fair win probability. For markets where BetOnline, BetCris, or Pinnacle prices are missing, it pulls available odds from other sportsbooks. Each price is converted to an implied probability and its expected value (EV), calculated as:

```
EV = fair_prob_p1 * payout - 1
```
where `payout` is the decimal return for a winning bet.

Run with:

```bash
python3 scripts/fair_odds.py
```

It outputs `Projected Fair Odds Charles Schwab 20250520.csv` containing the fair probabilities and their equivalent American odds (`fair_odds_p1` and `fair_odds_p2`). The CSV also lists each sportsbook's offered price with the expected value of a wager at that line so you can easily compare the market to the model.

Production outputs from the scripts are saved in the `outputs/` directory. Those generated CSVs are typically the only outputs that get committed to version control.

## Comparing Projections Across Rounds

`scripts/compute_stroke_diff.py` reports the change in projected strokes between two adjusted files. Provide the pre‑tournament and pre‑round files and an output path:

```bash
python3 scripts/compute_stroke_diff.py \
  "outputs/Adjusted Canadian Open DG Thursday Strokes 20250604.csv" \
  "outputs/Adjusted Round Score Pre R2 Canadian Open 20250606.csv" \
  "outputs/PreR1_vs_PreR2_Strokes_Diff Canadian Open 20250606.csv"
```

The resulting CSV lists each player with their pre‑round‑one strokes, pre‑round‑two strokes, and the difference between them.


## Scraping Live Scores

`scripts/scrape_live_scores.py` downloads the current hole-by-hole scores from ESPN's leaderboard API. Provide the ESPN `event_id` for an active tournament and an output file name:

```bash
python3 scripts/scrape_live_scores.py --event_id 401234567 --output memorial_scores.csv
```

The resulting CSV lists each player and their score on holes 1–18. Empty fields indicate holes not yet played.

## Evaluating Sportsbook Prices

`scripts/model_ev.py` compares your model's probabilities for each golfer against the American-odds lines from multiple sportsbooks. It converts the odds to decimal form and computes expected value using

```
EV = prob * payout - 1
```

Any wager with EV above 6% is written to `outputs/model_positive_ev_klm_open.csv` sorted from highest to lowest. Run the helper with:

```bash
python3 scripts/model_ev.py
```
