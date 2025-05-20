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

## Fair Odds Projection

`scripts/fair_odds.py` calculates fair head-to-head odds for any matchup in the
`72 Hole` CSV that lacks a BetOnline, BetCris, or Pinnacle price. It relies on
the adjusted stroke predictions and assumes a player scoring standard deviation
of 4.5 strokes per tournament. The output also lists available lines from other
books (DraftKings, Bet365, FanDuel, BetMGM, PointsBet, Bovada, Caesars, and
Unibet) along with the expected value of each wager relative to the projected
fair probability.

Run with:

```bash
python3 scripts/fair_odds.py
```

The script writes `Projected Fair Odds Charles Schwab 20250520.csv` which lists
the projected probabilities, no-vig American odds, and for each sportsbook the
offered price and expected value of betting either golfer.
