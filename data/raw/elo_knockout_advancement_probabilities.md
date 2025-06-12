### Modelling **win – draw – loss** probabilities from Elo ratings  

*(updated with knockout‑match advancement logic)*  

Below is a self‑contained cheat‑sheet that shows **how the chances of a win, tie or loss change as the Elo rating gap between two soccer teams widens**,  
**and** how to extend those probabilities to knockout situations where matches cannot end in a draw.

<!-- --------------------------------------------------------- -->
## 1  Classic 90‑minute probabilities  

We start with the Davidson extension of Elo that yields 3‑way probabilities (win / draw / loss).  
The formulas and worked table are identical to the earlier version (see Section A in the appendix).

<!-- --------------------------------------------------------- -->
## 2  From 90 minutes to “team advances” in knock‑out play  

When draws are not allowed, the match moves to **extra‑time** (usually 30 min) and, if still level, to **penalty kicks**.  
Define

* \(P_W, P_D, P_L\): win/draw/loss probabilities **after 90 minutes** from Section 1.  
* \(D = R_A - R_B\): Elo gap (positive favours Team A).  

**Step 1 – extra time (ET)**  
Treat ET as a 30‑minute mini‑match with the same logistic mechanics but one third the duration:

\[
\alpha_{\text{ET}} = 10^{(D/3)/400},\qquad
p_{\text{ET}}^{\text{win\*}} = \frac{\alpha_{\text{ET}}}{1+\alpha_{\text{ET}}}.
\]

Empirically ≈40 % of ET periods finish still level.  
We therefore split the conditional outcomes given a draw at 90 min as  

\[
\begin{aligned}
P_{\text{ET}}^{\text{win}} &= (1-\delta)\,p_{\text{ET}}^{\text{win\*}},\\
P_{\text{ET}}^{\text{loss}} &= (1-\delta)\,(1-p_{\text{ET}}^{\text{win\*}}),\\
P_{\text{ET}}^{\text{draw}} &= \delta,
\end{aligned}
\qquad\text{with}\;\delta\approx0.40.
\]

**Step 2 – penalty shoot‑out**  
Data show shoot‑outs are close to a coin‑flip with a slight lean to the better team.  
A simple calibration is  

\[
P_{\text{pen}}^{\text{win}} = 0.50 + 0.03\,(D/400),\quad\text{clipped to }[0.40,0.60].
\]

**Step 3 – probability that Team A advances**

\[
\boxed{\;
P_{\text{adv}} = P_W + P_D\,\bigl(P_{\text{ET}}^{\text{win}} + P_{\text{ET}}^{\text{draw}}\,P_{\text{pen}}^{\text{win}}\bigr)
\;}
\]

The bracket is the chance of prevailing *conditional* on being level after 90 min.

---

### Worked example table  

| Elo gap | Win 90′ | Draw 90′ | Loss 90′ | **Advance %** |
|-------:|-------:|-------:|-------:|-----------:|
| ‑200 | 18.7 % | 22.2 % | 59.1 % | 28.4 % |
| ‑100 | 27.3 % | 24.3 % | 48.4 % | 38.6 % |
|  0 | 37.5 % | 25.0 % | 37.5 % | 50.0 % |
| +100 | 48.5 % | 24.3 % | 27.3 % | 61.4 % |
| +200 | 59.1 % | 22.2 % | 18.7 % | 71.6 % |

*Interpretation* – With a 200‑point Elo edge, Team A has **≈71 %** chance to reach the next round;  
an underdog 200 points weaker still advances **≈28 %** of the time thanks to draws and the lottery of penalties.

---

## 3  Practical checklist for an LLM or code pipeline  

1. **Retrieve Elo ratings** for both clubs on match‑day.  
2. **Compute 90‑min win/draw/loss** via Davidson (Section 1).  
3. **If knockout:**  
   * Compute ET win/draw/loss using the 30‑minute adjustment and \(\delta\).  
   * Evaluate penalty edge with the 3 % rule (or your own calibration).  
   * Apply the boxed formula for \(P_{\text{adv}}\).  
4. **Return** probabilities for (a) regulation result, (b) advancing.  
5. **Optionally adjust** for home advantage (\(+60\) Elo), travel fatigue, or red‑card forecasts.

---

## 4  Caveats  

* The 40 % ET‑draw rate and 3 % shoot‑out edge are broad averages across top‑level men’s football;  
  recalibrate for specific competitions.  
* Small Elo gaps (<50 pts) make the coin‑flip nature of penalties dominate.  
* Use Monte‑Carlo simulations for compound tournaments where successive draws accumulate fatigue.  

---

### Appendix A – 90‑minute Davidson table  

*(unchanged from earlier cheat‑sheet; included for completeness)*  

| Elo gap \(D\) | **Win** | **Draw** | **Loss** |
|---:|---:|---:|---:|
| ‑400 | 7.6 % | 16.1 % | 76.3 % |
| ‑300 | 12.2 % | 19.3 % | 68.5 % |
| ‑200 | 18.7 % | 22.2 % | 59.1 % |
| ‑100 | 27.3 % | 24.3 % | 48.4 % |
|  0 | 37.5 % | 25.0 % | 37.5 % |
| +100 | 48.5 % | 24.3 % | 27.3 % |
| +200 | 59.1 % | 22.2 % | 18.7 % |
| +300 | 68.5 % | 19.3 % | 12.2 % |
| +400 | 76.3 % | 16.1 % | 7.6 % |

---

*Prepared June 2025; parameters are easily tweaked in code to fit your own dataset.*  
