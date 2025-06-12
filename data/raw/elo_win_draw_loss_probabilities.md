### Modelling **win – draw – loss** probabilities from Elo ratings  

Below is a self‑contained cheat‑sheet that shows **how the chances of a win, tie or loss change as the Elo rating gap between two soccer teams widens**.  
It combines the standard Elo “expected‑score” calculus with the Davidson extension that explicitly allows for draws.  
All symbols and parameters are explained so you can plug the formulas straight into code, spreadsheets or betting models.

---

## 1.  Starting point – Elo’s expected‑score formula  

For two teams *A* and *B* with ratings \(R_A\) and \(R_B\):

\[
E_A \;=\; \frac{1}{1 + 10^{(R_B - R_A)/400}}, 
\qquad 
E_B = 1-E_A
\]

\(E_A\) is the *expected score* (1 = win, 0.5 = draw, 0 = loss) of team *A*; it rises smoothly as the rating gap increases.  This logistic form is standard in chess and football Elo implementations.  

---

## 2.  Adding draws – the Davidson extension  

The classic Elo model treats a draw as “half a win”, not as a separate outcome.  
Davidson (1970) showed that a single extra parameter \(\nu>0\) lets us split the 3‑way probabilities analytically:

\[
\begin{aligned}
P_A(\text{win}) &= \frac{\alpha_A}{\alpha_A + \alpha_B + \nu\sqrt{\alpha_A\alpha_B}},\\[3pt]
P(\text{draw}) &= \frac{\nu\sqrt{\alpha_A\alpha_B}}{\alpha_A + \alpha_B + \nu\sqrt{\alpha_A\alpha_B}},\\[3pt]
P_A(\text{loss}) &= 1 - P_A(\text{win}) - P(\text{draw}),
\end{aligned}
\quad\text{with}\quad 
\alpha_i = 10^{R_i/400}.
\]

Setting \(\nu\approx0.67\) reproduces the empirically observed ~25 % draw rate when two equally rated sides meet.  

---

## 3.  Worked probabilities for typical Elo gaps  

*Assume neutral venue and \(\nu=0.667\).  Positive differences favour Team A.*

| Elo gap \(D = R_A-R_B\) | **Team A win** | **Draw** | **Team A loss** |
|---:|---:|---:|---:|
| ‑400 | 7.6 % | 16.1 % | 76.3 % |
| ‑300 | 12.2 % | 19.3 % | 68.5 % |
| ‑200 | 18.7 % | 22.2 % | 59.1 % |
| ‑100 | 27.3 % | 24.2 % | 48.5 % |
|  0 | 37.5 % | 25.0 % | 37.5 % |
| +100 | 48.5 % | 24.2 % | 27.3 % |
| +200 | 59.1 % | 22.2 % | 18.7 % |
| +300 | 68.5 % | 19.3 % | 12.2 % |
| +400 | 76.3 % | 16.1 % | 7.6 % |

*Reading the table*  

* A 100‑point edge (≈ 0.6 goals on neutral ground) lifts the favourite’s win probability from 37.5 % to **48.5 %** and trims the draw chance slightly.  
* A huge 400‑point gulf all but eliminates the underdog’s hopes (only ~7.6 % to win).  
* Draw likelihood peaks (~25 %) when both teams are evenly matched and shrinks as the contest becomes one‑sided.

---

## 4.  How to use the formulas in practice  

1. **Compute \(D = R_A - R_B\)** from any Elo database (ClubElo, FiveThirtyEight SPI‑Elo, etc.).  
2. **Convert to \(\alpha\)** values: \(\alpha_A = 10^{R_A/400}\), \(\alpha_B = 10^{R_B/400}\).  
3. **Choose \(\nu\)**:  
   * 0.60–0.70 fits top‑division men’s football (average draw ≈ 25 %).  
   * Tweak up for defensive leagues (e.g. Serie A), down for high‑scoring ones (e.g. MLS).  
4. **Plug into the Davidson equations** above to get \(P(\text{win}),P(\text{draw}),P(\text{loss})\).  
5. **Apply context modifiers** (home advantage, red cards, fatigue) if needed – those can be modelled as Elo adjustments or separate factors.  

---

## 5.  Caveats & extensions  

* **Home advantage** shifts ratings by ~60 Elo points for the host; include it as \(R_A+H\).  
* **Penalty shoot‑outs**: tournaments that cannot end in a draw need conditional probabilities \(P(\text{win}|\text{no draw})\).  
* **Calibration**: re‑fit \(\nu\) on league‑specific data every season to stay aligned with tactical trends.  
* **Over‑dispersion**: if match‑to‑match variance is large, consider a Bayesian update or a hierarchical Davidson‑Bradley‑Terry model.  

---

### Quick reference  

\[
\boxed{\;P_A(\text{win}) = \dfrac{10^{D/400}}{10^{D/400}+1+\nu\sqrt{10^{D/400}}}\;},\quad
\boxed{\;P(\text{draw}) = \dfrac{\nu\sqrt{10^{D/400}}}{10^{D/400}+1+\nu\sqrt{10^{D/400}}}\;}.
\]

Use \(\nu\approx0.67\) for mainstream men’s football; adjust as needed for other competitions.  

With these formulas you can move seamlessly from a simple Elo rating sheet to fully probabilistic match forecasts that respect the natural frequency of draws in the sport.
