# Building a Quarter‑Kelly Betting Calculator

## 1. What Is the Kelly Criterion?

The Kelly criterion determines the optimal fraction *f\**\* of a bankroll to wager on a positive‑EV bet so that long‑run log‑wealth is maximized:

$$
f^*=\frac{bp-q}{b}
$$

where

- **p** = your estimated probability the wager wins
- **q** = 1 – p = probability it loses
- **b** = net decimal odds (i.e. how many units you win per unit staked)

Betting a fraction α·*f\**\* with 0 < α ≤ 1 trades growth for reduced variance. **Quarter‑Kelly** uses α = 0.25.

## 2. Required Inputs

| Variable                | Meaning                                  | Example |
| ----------------------- | ---------------------------------------- | ------- |
| **Bankroll**            | Total capital allocated to betting       | \$5,000 |
| **Odds**                | Decimal or American format of the market | –120    |
| **Estimated win % (p)** | Your model’s probability                 | 57 %    |

## 3. Core Calculations

1. **Convert odds**\
   *American → decimal*

   $$
   \text{decimal}=
   \begin{cases}
   1+\frac{100}{|\text{odds}|} & \text{if odds} < 0\\[4pt]
   1+\frac{\text{odds}}{100} & \text{if odds} > 0
   \end{cases}
   $$

2. **Compute net odds**\
   \(b = \text{decimal} - 1\)

3. **Full‑Kelly fraction**\
   \(f^* = \dfrac{bp - (1-p)}{b}\)\
   (If the result ≤ 0, the bet has no edge—stake \$0.)

4. **Quarter‑Kelly stake**

   $$
   \text{stake} = 0.25 \times f^* \times \text{Bankroll}
   $$

## 4. Implementing the Calculator

### 4.1 Google Sheets / Excel

| Cell   | Purpose             | Formula (assuming odds in **B2**, prob in **C2**, bankroll in **B1**) |
| ------ | ------------------- | --------------------------------------------------------------------- |
| **D2** | Decimal odds        | `=IF(B2<0,1+100/ABS(B2),1+B2/100)`                                    |
| **E2** | Net odds (b)        | `=D2-1`                                                               |
| **F2** | Full‑Kelly fraction | `=(E2*C2 - (1-C2)) / E2`                                              |
| **G2** | Quarter‑Kelly stake | `=MAX(0,0.25*F2*$B$1)`                                                |

Add data‑validation so probability is 0–1 and stake is floored at 0.

### 4.2 Python Snippet

```python
def quarter_kelly(bankroll, odds_american, p):
    if odds_american < 0:
        decimal = 1 + 100/abs(odds_american)
    else:
        decimal = 1 + odds_american/100
    b = decimal - 1
    f_full = (b*p - (1-p)) / b
    f_quarter = max(0, 0.25 * f_full)
    return bankroll * f_quarter
```

## 5. Worked Example

| Item                    | Value                                 |
| ----------------------- | ------------------------------------- |
| Bankroll                | \$5,000                               |
| Odds                    | –120                                  |
| Decimal                 | 1 + 100/120 = 1.8333                  |
| Net odds (b)            | 0.8333                                |
| p                       | 0.57                                  |
| **Full‑Kelly f\***      | (0.8333×0.57 – 0.43) / 0.8333 ≈ 0.088 |
| **Quarter‑Kelly stake** | 0.25×0.088×5,000 ≈ **\$110**          |

## 6. Testing & Validation Checklist

- ✅ Edge cases: No‑edge bets produce \$0 stake
- ✅ Compare calculator output to reputable Kelly tables
- ✅ Monte‑Carlo simulate bankroll evolution to confirm quarter‑Kelly variance profile

## 7. Risk Management Notes

Quarter‑Kelly cuts growth rate to \~⅓ of full‑Kelly while halving drawdown risk. Still, large estimation errors can cause ruin—consider:

- Capping stake to a % of daily turnover
- Using Bayesian probability intervals to shrink edge estimates
- Tracking realized growth vs expected to recalibrate models

## 8. Extending the Tool

- Support parlay legs by computing joint probability and net odds
- Allow user‑selectable Kelly fractions (⅛, ½, full)
- Integrate real‑time odds feeds & model outputs via API
- Add bankroll‑at‑risk charts and anguish‑adjusted staking

---

*Prepared July 9 2025*

