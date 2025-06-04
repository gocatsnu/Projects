# DraftKings PGA DFS — Official Rules Reference (2025)

## 1 · Contest Formats

| Mode | Scoring Window | Lineup Size | Salary Cap | Finish-Pts? | Notes |
|------|---------------|------------|------------|-------------|-------|
| **Classic (Full‑Tournament)** | All 4 scheduled rounds | 6 golfers | $50,000 | ✅ | Default “72‑hole” lobby |
| **Showdown** | Single round (R1, R2, R3 or R4) | 6 golfers | $50,000 | ⛔ R1–R3<br>✅ R4 | Rounds 1‑3 omit placement points; R4 adds them back |
| **Captain Showdown** | Same as Showdown | 1 Captain (1.5× pts & salary) + 5 Flex | $50,000 cap still applies after 1.5× salary bump | Same as Showdown | Pick a high‑ceiling scorer or ownership pivot as Captain |

A valid entry **must** use exactly the stated roster size and remain **≤ $50K** in total salary.

---

## 2 · Per‑Hole Fantasy Scoring  
*(applies to Classic **and** Showdown)*

| Result | DK Pts |
|--------|-------|
| Double‑Eagle (Albatross) or better | **+13** |
| Eagle | **+8** |
| Birdie | **+3** |
| Par | **+0.5** |
| Bogey | **−0.5** |
| Double Bogey or worse | **−1** |

---

## 3 · Round & Tournament Bonuses

| Bonus | Limit | DK Pts |
|-------|-------|-------|
| Streak of **3 birdies or better** | Max 1 per round | +3 |
| **Bogey‑free round** | Max 1 per round | +3 |
| **All 4 rounds < 70** | Once per event | +5 |
| **Hole‑in‑one** | Any time | +10 |

Bonuses stack with hole points; e.g., a bogey‑free 66 yields par/birdie pts **plus** +3.

---

## 4 · Finishing‑Position Points *(Classic + R4 Showdown)*

| Pos | Pts | Pos | Pts |
|-----|-----|-----|-----|
| 1 | **30** | 11‑15 | 6 |
| 2 | 20 | 16‑20 | 5 |
| 3 | 18 | 21‑25 | 4 |
| 4 | 16 | 26‑30 | 3 |
| 5 | 14 | 31‑40 | 2 |
| 6 | 12 | 41‑50 | 1 |
| 7 | 10 | >50 | 0 |
| 8 | 9 |  |  |
| 9 | 8 |  |  |
| 10 | 7 |  |  |

Placement points do **not** appear in R1‑R3 Showdown slates.

---

## 5 · Lineup Lock & Stat Eligibility

* **Classic:** all six golfers lock at the first tournament tee‑time—no late swap.  
* **Showdown:** the six golfers lock at that round’s first tee‑time.  
* **Playoff holes** do **not** generate per‑hole points; however, the playoff outcome *does* decide final position points.  
* A golfer who **WDs/DQs** stops earning points; accrued stats remain.

---

## 6 · Captain Mechanics (Showdown Captain Mode)

```text
TotalPts   = 1.5 × CaptainDKPts + Σ FlexDKPts
TotalSalary = 1.5 × CaptainSalary + Σ FlexSalary  ≤ $50,000
```

Selecting a volatile birdie‑maker as Captain can create slate‑winning ceilings.

---

## 7 · Minimal JSON Schema Example

```jsonc
{
  "per_hole": {
    "double_eagle": 13,
    "eagle": 8,
    "birdie": 3,
    "par": 0.5,
    "bogey": -0.5,
    "double_bogey_or_worse": -1
  },
  "bonuses": {
    "birdie_streak": 3,
    "bogey_free_round": 3,
    "all_rounds_sub70": 5,
    "hole_in_one": 10
  },
  "finish_points": {
    "1": 30, "2": 20, "3": 18, "4": 16, "5": 14, "6": 12,
    "7": 10, "8": 9, "9": 8, "10": 7,
    "11-15": 6, "16-20": 5, "21-25": 4,
    "26-30": 3, "31-40": 2, "41-50": 1
  },
  "roster": {
    "size": 6,
    "salary_cap": 50000
  }
}
```

---

### 8 · Quick Strategy Implications

* **Birdie > Bogey math** (+3 vs −0.5) means high‑variance scorers are DFS gold.  
* **Getting 6/6 golfers through the cut** boosts ceiling via two extra rounds *and* placement points.  
* **R1‑R3 Showdown:** with no finish points, chase raw birdie volume.  
* **Captain slates:** leverage the 1.5× multiplier for a stud or contrarian upside play.

---

*Updated June 4 2025.*  
*Source: DraftKings Help Center & curated DFS primers.*
