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

`scripts/fair_odds.py` uses the DataGolf stroke projections to estimate a fair
win probability for every listed matchup. For markets where BetOnline, BetCris
or Pinnacle prices are missing, the script also pulls available odds from other
books (DraftKings, Bet365, FanDuel, BetMGM, PointsBet, Bovada, Caesars and
Unibet). Each price is converted to an implied probability and its expected
value is calculated as:

```
EV = fair_prob_p1 * payout - (1 - fair_prob_p1)
```

where `payout` is the decimal return for a winning bet. These sportsbook lines
and their EVs are written to `Projected Fair Odds Charles Schwab 20250520.csv`
so you can easily compare the market to the model.
