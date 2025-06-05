# Modeling‑Relevant Format Differences: LIV Golf vs. PGA Tour  
*(team elements omitted, LIV field = 54 players)*

| Factor that drives your matchup model | LIV Golf League | PGA Tour (regular “open” events) | Why it matters for modeling |
|---|---|---|---|
| **Total holes & rounds** | **54 holes / 3 rounds** (Fri–Sun) | **72 holes / 4 rounds** (Thu–Sun) | Fewer holes → larger scoring variance. If you convert a per‑round stroke edge Δ to win probability, multiply by **3** (not 4) and use σ₃ ≈ √6 · σ_round (~5.5) instead of σ₄ ≈ √8 · σ_round (~6.6). |
| **Field size** | **54 players** (13 × 4‑man teams + 2 wild cards) | 120–156 players in full‑field events; Signature events min. 72 | Smaller field cuts down the number of potential matchup pairings and narrows the talent distribution. Upsets are slightly less frequent because baseline skill gaps are wider at the bottom of a 54‑man list than in a 156‑man field. |
| **Cut policy** | **None** – everyone plays all 54 holes | **36‑hole cut** to low 65 & ties (majors vary) | In LIV there is zero “miss‑cut” risk, so the lower tail of each player’s strokes‑gained distribution is truncated. For head‑to‑head models you can ignore MC probability and use pure stroke distributions. On the PGA Tour you must model MC risk (≈ 8–20 % per player) and treat post‑cut rounds as implicit missing strokes if a player is cut. |
| **Starting format** | **Shotgun start** – all 54 players on course simultaneously | **Wave tee times** off Nos. 1 & 10 | Shotgun minimizes weather/tee‑time wave bias. You can usually skip “AM vs PM” adjustments that matter on the PGA Tour and treat round‑level scoring errors as i.i.d. |
| **Playoff structure** | Sudden‑death stroke play at a designated hole | Sudden‑death for most events (majors sometimes 3‑ or 2‑hole aggregate) | Ties in betting matchups typically push, but if you model outright‑win probability the shorter event plus sudden‑death makes true‑tie frequency slightly higher for LIV. |
| **Ranking & data availability** | No OWGR/FedExCup points; independent ratings (DataGolf, etc.) become primary baselines | OWGR + FedExCup points feed directly into pricing | When calibrating priors, you can’t lean on OWGR for LIV players. Blend in independent strokes‑gained metrics from all‑tour data or regress to global talent priors. |
| **Schedule & course history** | Many brand‑new venues with limited historical data | Repeats long‑standing PGA stops (TPC, Classic rota) | LIV course‑fit adjustments carry higher uncertainty. Weight generic SG skill more heavily; shrink course‑history coefficients. |
| **Guaranteed money** | All finishers paid (last place ≈ $120 k) | Missed‑cut earns **$0** | Behavioral angle: with pay locked in and no cut, LIV players have weak monetary incentive to “grind” for the cut line but strong incentive to finish top‑24 (points paid only there). Expect slightly more aggressive play and fatter tail risk on Sundays. |

---

## Practical tips for a matchup‑probability engine

1. **Scale your stroke‑edge pipeline**  
   \[
   \mu_{54} = 3\,\Delta_{\text{round}}, \qquad
   \sigma_{54} \approx \sqrt{6}\,\sigma_{\text{round}}
   \]  
   Replace the 72‑hole multipliers (× 4 and √8) you use for PGA modeling.

2. **Eliminate MC state‑branching**  
   Model LIV strokes for all three rounds directly; no Bernoulli “made cut?” node required.

3. **Drop tee‑time weather splits**  
   One variance term suffices per round; any wind shift will hit the whole field simultaneously.

4. **Use independent ratings**  
   Feed DataGolf “true strokes‑gained” or your own Elo‑style ratings; don’t trust OWGR for LIV talent gaps.

5. **Widen priors on course effects**  
   When a LIV event hits a first‑time course, shrink course‑fit adjustments toward zero and let generic SG surface.

6. **Expect higher volatility in top‑heavy fields**  
   With only 54 entrants, matchup‑win probability curves flatten: a 1‑stroke skill edge translates to a slightly lower win probability than in a 156‑man draw because common‑shock variance (weather, course conditions) weighs more.

---
