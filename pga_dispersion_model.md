# PGA Tour Scoring-Dispersion Model — Key Factors & Parameters  
*(1993 – 2024, top-250 skill cohort)*

## 1 · Core Statistical Benchmarks  

| Metric | Notation | Mean Value | Notes / Context |
|--------|----------|-----------:|-----------------|
| Single-round std-dev | `sigma_round` | **2.5 strokes** | Top-250 players, regular event baseline |
| Tourney std-dev (no cut) | `sigma_tourney_theoretical` | `2 × sigma_round` ≈ **5.0** | Independent-round (IID) expectation |
| Observed tourney std-dev<br>— regular events (finishers) | `sigma_tourney_regular` | **4.4 – 4.6** | Cut truncates high-tail |
| Observed tourney std-dev<br>— majors (finishers) | `sigma_tourney_major` | **4.8 – 5.1** | Tougher setup offsets cut bias |
| Observed tourney std-dev<br>— no-cut elite events | `sigma_tourney_nocut` | **5.0 – 5.5** | All outcomes retained |
| Round-to-round autocorr. | `rho_round` | **0.02** | Weak positive AR(1) persistence |
| Typical skew (round) | `skew_round` | ~ 0.1 – 0.2 (right) | Occasional blow-ups |
| Typical kurtosis (round) | `kurt_round` | ~ 3.1 – 3.4 | Slightly heavy-tailed vs Gaussian |

---

## 2 · Event-Type Parameter Sets (YAML)

```yaml
event_types:
  standard:
    sigma_round: 2.4
    sigma_tourney_finishers: 4.5
    cut: true
    cut_size: 65            # players + ties
    skew_round: 0.10
    kurt_round: 3.2
  major:
    sigma_round: 2.7
    sigma_tourney_finishers: 5.0
    cut: true
    cut_size: 60
    skew_round: 0.20
    kurt_round: 3.4
  no_cut:
    sigma_round: 2.4
    sigma_tourney_finishers: 5.2
    cut: false
    field_size: 70
    skew_round: 0.15
    kurt_round: 3.3
common:
  rho_round: 0.02           # AR(1) persistence
  strokes_per_sigma: 1      # unit scale (strokes)
```

---

## 3 · Modeling Workflow (Pseudo-Python)

```python
# 1. Set player-specific mean score μ based on skill metric (e.g. SG_Total → expected_score)
mu = skill_to_score(player.skill_rating)

# 2. Draw 4 independent round shocks ε_i  ~  N(0, sigma_round^2)
epsilon = np.random.normal(0, sigma_round, size=4)

# 2a.  Add minimal AR(1) persistence
for i in range(1, 4):
    epsilon[i] += rho_round * epsilon[i-1]

# 3. Round scores = μ + ε_i
round_scores = mu + epsilon

# 4. Apply cut logic (if event has a cut)
if event.cut and sum(round_scores[:2]) > cut_line:
    player.status = "MC"          # missed cut
else:
    player.tourney_total = np.sum(round_scores)

# 5. Repeat for all players → produce leaderboard distribution
```

---

## 4 · Optional Model Extensions  

1. **Course-difficulty adjustment**  
   - Normalize scores to *strokes-gained against field* or *course fixed-effects*; then re-add expected course mean for forward simulation.  
2. **Weather variance** (`sigma_weather`)  
   - Add wave-specific shocks (AM/PM) to capture draw bias.  
3. **Risk-adjusted weekend variance**  
   - Inflate `sigma_round` on R3–R4 for﻿ finishers by +5 – 10 % (empirical).  
4. **Player-specific volatility**  
   - Let `sigma_round_i = sigma_round · (1 + v_i)` with  \(v_i\sim\mathcal{N}(0,0.05^2)\) to reflect small heterogeneity.  
5. **Skewed error distribution**  
   - Replace Gaussian ε with *skew-t* (df ≈ 7, skew ≈ 0.2) to capture fat-tail blow-ups.  

---

## 5 · Recommended Defaults for Monte-Carlo Sims  

```yaml
simulation_defaults:
  n_players: 144
  n_iterations: 25_000
  scoring_model:
    distribution: skew_t
    df: 7
    skew: 0.15
    sigma_round: 2.5
    rho_round: 0.02
  cut_rule: top65_and_ties
  weather:
    wave_bias_std: 0.3      # strokes
  output_metrics:
    - win_probabilities
    - make_cut_prob
    - top10_prob
    - expected_finish_position
```

---

## 6 · Usage Notes for LLM Agents  

- **Parse headings** to identify sections (`Core Statistical Benchmarks`, `Event-Type Parameter Sets`, etc.).  
- **Extract YAML blocks** verbatim; they define event-type presets and simulation defaults.  
- **Follow pseudo-code** as the canonical logic; translate into the target language as-is.  
- When ingesting numeric fields, treat all values as **floats (strokes)** unless otherwise noted.  
- If additional granularity (e.g. weather, player-specific σ) is required, extend the YAML under `Optional Model Extensions`.  

---

*End of document.*
