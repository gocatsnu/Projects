"""Quarter-Kelly staking calculator.

This script computes the recommended stake for a wager using
Quarter-Kelly staking. It accepts a bankroll amount, the market odds,
and the bettor's estimated probability of winning. Odds may be entered
in American or decimal format.

Example:
    python3 quarter_kelly.py --bankroll 5000 --odds -120 --prob 0.57
"""

import argparse
from typing import Literal


def american_to_decimal(odds: float) -> float:
    """Convert American odds to decimal."""
    if odds >= 0:
        return 1 + odds / 100
    return 1 + 100 / (-odds)


def quarter_kelly_stake(
    bankroll: float, odds: float, prob: float, fmt: Literal["american", "decimal"]
) -> float:
    """Return the Quarter-Kelly stake.

    Parameters
    ----------
    bankroll : float
        Total bankroll available for betting.
    odds : float
        Betting odds in either American or decimal form.
    prob : float
        Estimated win probability for the wager (0-1).
    fmt : {"american", "decimal"}
        Format of the supplied odds.
    """

    if not 0 <= prob <= 1:
        raise ValueError("prob must be between 0 and 1")

    decimal = american_to_decimal(odds) if fmt == "american" else odds
    b = decimal - 1
    full_fraction = (b * prob - (1 - prob)) / b
    quarter_fraction = max(0.0, 0.25 * full_fraction)
    return bankroll * quarter_fraction


def main() -> None:
    parser = argparse.ArgumentParser(description="Quarter-Kelly betting calculator")
    parser.add_argument("--bankroll", type=float, required=True, help="Total bankroll")
    parser.add_argument("--odds", type=float, required=True, help="Wager odds")
    parser.add_argument(
        "--format",
        choices=["american", "decimal"],
        default="american",
        help="Input odds format (default: american)",
    )
    parser.add_argument("--prob", type=float, required=True, help="Win probability (0-1)")

    args = parser.parse_args()

    stake = quarter_kelly_stake(args.bankroll, args.odds, args.prob, args.format)
    print(f"Recommended stake: {stake:.2f}")


if __name__ == "__main__":
    main()
