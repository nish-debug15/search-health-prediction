# Block 2: Label Specification & Question Lock
**Search Health Scoring System**  
*Status: FROZEN / LOCKED*  
*Date: July 2026*

---

## 1. Research Question

> **"Can historical search signals predict whether a page's search visibility will grow, remain stable, or decline over a future 30-day window?"**

This framing establishes an observational, directional prediction task designed to act as an early-warning and opportunity-identification system for content SEO management. It avoids causal claims while providing actionable categorization for content triage.

---

## 2. Temporal Window Design

Each predictive instance is defined relative to a specific **Cutoff Date ($t_0$)**:

* **Feature Window ($T_{feat}$)**: The **30 days immediately preceding** $t_0$ (inclusive of $t_0 - 30\text{d}$ through $t_0 - 1\text{d}$). All input features, aggregates, trend indicators, and quality metrics must be computed strictly using data available within this historical window or static dimension tables.
* **Prediction Window ($T_{pred}$)**: The **30 days immediately following** $t_0$ (inclusive of $t_0$ through $t_0 + 29\text{d}$). This window is used exclusively for computing the target label.
* **No Artificial Gap**: While Google Search Console (GSC) operational reporting exhibits an inherent 2–3 day data processing lag in real-time production, our modeling evaluates historical prediction checkpoints where all data is finalized. No artificial gap is introduced between $T_{feat}$ and $T_{pred}$, ensuring continuity of search visibility tracking.

---

## 3. Label Definition & Empirical Threshold Lock

### Target Variable Computation
For each qualified content page $(c, p)$ at cutoff $t_0$, the target label is derived from the percentage change in total GSC impressions between the prediction window and the feature window:

$$\Delta\% = \frac{\text{Impressions}_{pred} - \text{Impressions}_{feat}}{\text{Impressions}_{feat}}$$

### 3-Class Classification Scheme (Locked Threshold $X = \pm 20\%$)
Based on empirical feasibility testing across 160,731 qualified pages in the April $\to$ May 2026 window, we lock the classification threshold at **$X = 20\%$**:

| Label Class | Mathematical Definition | Interpretation | Empirical Share (Apr $\to$ May 2026) |
| :--- | :--- | :--- | :--- |
| **Growing** | $\Delta\% > +20.0\%$ | Material expansion in search visibility | **24.9%** (40,011 pages) |
| **Stable** | $-20.0\% \le \Delta\% \le +20.0\%$ | Consistent search visibility within normal noise | **21.7%** (34,945 pages) |
| **Declining** | $\Delta\% < -20.0\%$ | Material erosion or decay in search visibility | **53.4%** (85,775 pages) |

### Threshold Sensitivity & Justification
During label feasibility analysis (`02_label_feasibility.py`), we tested threshold values ranging from $\pm 10\%$ to $\pm 50\%$:

| Threshold ($X$) | % Growing | % Stable | % Declining | Feasibility Assessment |
| :---: | :---: | :---: | :---: | :--- |
| $\pm 10\%$ | 28.9% | 11.0% | 60.1% | Stable class too narrow; captures normal weekly noise |
| $\pm 15\%$ | 26.8% | 16.3% | 56.9% | Moderate balance, but sensitive to minor algorithm shifts |
| **$\pm 20\%$ (LOCKED)** | **24.9%** | **21.7%** | **53.4%** | **Optimal SEO practical relevance; clear separation of classes** |
| $\pm 25\%$ | 23.2% | 26.9% | 49.9% | Highly balanced across top 2 classes, but dilutes strong signals |
| $\pm 30\%$ | 21.8% | 31.9% | 46.3% | Requires severe swings to trigger growth/decline |
| $\pm 50\%$ | 17.1% | 51.5% | 31.4% | Majority stable; fails to identify early decay warnings |

**Why $\pm 20\%$ is locked:**
1. **SEO Practicality**: In professional search engine optimization, a $\pm 20\%$ shift over 30 days represents a genuine change in SERP visibility (ranking shifts, SERP feature gain/loss, or content obsolescence) rather than normal day-to-day impression variance.
2. **Class Separation**: It achieves a robust distribution where Growing (~25%) and Stable (~22%) represent distinct, meaningful cohorts.
3. **Macro F1 Alignment**: While Declining (~53%) forms the largest class due to natural content decay over time and dataset expansion dynamics, our evaluation metric (Macro F1) ensures models must perform equally well on all three classes rather than defaulting to the majority class.

---

## 4. Minimum Activity Filter

* **Rule**: A content page must have **$\text{Impressions}_{feat} \ge 10$** within the 30-day feature window to be included in the dataset for that cutoff date.
* **Justification**: 
  * Pages with fewer than 10 impressions over 30 days represent zero-signal or unindexed content.
  * Without this filter, extreme low-volume noise distorts percentage calculations (e.g., an increase from 1 impression to 3 impressions yields a $+200\%$ change, erroneously classifying dead content as "Growing").
  * Feasibility testing confirmed that applying $\ge 10$ impressions retains over 160,000 active pages per window in the 2026 panel, providing ample sample size while eliminating statistical noise.

---

## 5. Primary Evaluation Metric

* **Metric**: **Macro F1-Score** (Unweighted arithmetic mean of class-wise F1-scores):
  $$\text{Macro F1} = \frac{\text{F1}_{\text{growing}} + \text{F1}_{\text{stable}} + \text{F1}_{\text{declining}}}{3}$$
* **Justification**:
  * Accuracy would be misleadingly high for naive models predicting "Declining" for all instances (~53% accuracy).
  * Macro F1 treats all three outcomes with equal importance. A successful recommendation engine must accurately identify **Growing** pages (to protect/expand) and **Stable** pages (to monitor) just as effectively as **Declining** pages (to refresh/prune).
  * Secondary reporting metrics will include weighted F1, class-wise precision/recall, and confusion matrices.

---

## 6. Time-Aware Window Split Diagram

To prevent temporal leakage and respect the unbalanced, growing nature of the panel (~80x row growth from early 2025 to mid 2026), all data splits are **strictly ordered in time**. No random K-Fold or stratified shuffling is permitted across time boundaries.

```
DATASET TIMELINE (Jan 2025 ----------------------------------------------------------> June 2026)
[Early 2025: Low Volume / Onboarding]
                                       |--- TRAIN WINDOW 1 ---|
                                       Feat: Jan 16 - Feb 14
                                       Pred: Feb 15 - Mar 16  (Cutoff: Feb 15, 2026)
                                       
                                                |--- TRAIN WINDOW 2 ---|
                                                Feat: Feb 13 - Mar 14
                                                Pred: Mar 15 - Apr 13  (Cutoff: Mar 15, 2026)
                                                
                                                         |--- VALIDATION WINDOW ---|
                                                         Feat: Mar 16 - Apr 14
                                                         Pred: Apr 15 - May 14  (Cutoff: Apr 15, 2026)
                                                         
                                                                  |--- TEST WINDOW (OUT-OF-TIME) ---|
                                                                  Feat: Apr 15 - May 14
                                                                  Pred: May 15 - Jun 13  (Cutoff: May 15, 2026)
```

### Split Assignments (Block 6 Lock):
1. **Training Set**: Historical cutoff dates in Q1 2026 (specifically Cutoffs `2026-02-15` and `2026-03-15`). This utilizes periods where client onboarding has stabilized (~54–55 clients, ~320k–330k pages) to train robust feature representations.
2. **Validation Set**: Cutoff `2026-04-15` (Feature: Mar 16 – Apr 14, 2026; Predict: Apr 15 – May 14, 2026). Used for hyperparameter tuning, threshold selection, and model selection.
3. **Test Set (Out-of-Time)**: Cutoff `2026-05-15` (Feature: Apr 15 – May 14, 2026; Predict: May 15 – June 13, 2026). Strictly reserved for final baseline vs. candidate model evaluation in Block 7 and explainability in Block 8.

---

## 7. Specification Freeze Commitment

By committing this document, the following parameters are **officially frozen**:
* **Target variable**: 3-class classification via 30-day future impression percentage change.
* **Thresholds**: $\pm 20.0\%$ cutoff for Growing / Stable / Declining.
* **Activity filter**: $\text{Impressions}_{feat} \ge 10$.
* **Primary evaluation metric**: Macro F1-Score.
* **Split methodology**: Strict time-aware ordering (no random splitting).

*No downstream block (Blocks 3–12) may alter these definitions or thresholds.*
