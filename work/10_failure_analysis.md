# Block 10: Failure Analysis & Limitations
**Search Health Scoring System**  
*Status: COMPLETED*

## 1. Error Analysis Overview
The Champion Random Forest model achieved a Macro F1 score of 0.4871 on the Out-Of-Time (OOT) test set. While this significantly outperforms the baseline heuristic, it still produces an overall error rate of **47.8%** (80,471 misclassifications out of 168,375 pages).

A deep dive into the misclassifications reveals specific operational blind spots.

## 2. Error Breakdown by Class

| True Class | Total Instances | Misclassified | Error Rate | Primary Misclassification |
| :--- | :--- | :--- | :--- | :--- |
| **Declining** | 97,110 | 43,826 | 45.1% | Predicted as Stable |
| **Growing** | 38,322 | 20,981 | 54.7% | Predicted as Declining |
| **Stable** | 32,943 | 15,664 | 47.5% | Predicted as Declining |

## 3. Representative Failure Modes

### Failure Mode A: The "False Growth" Trap (True: Declining, Pred: Growing)
* **Count:** 15,675 pages.
* **Mechanism:** The model relies heavily on recent short-term momentum (e.g., a viral spike in H2 of the feature window). However, these spikes are often transient. The model predicts sustained growth, but the traffic rapidly regresses to the mean in the prediction window.
* **Evidence:** The average 15-day momentum for these false positives was highly inflated (33.56).

### Failure Mode B: The "Stability" Illusion
* **Count:** 15,664 pages.
* **Mechanism:** Predicting stability ($\pm 20\%$ variance) is notoriously difficult in SEO due to the natural daily volatility of SERP features and crawl rates. The model is highly sensitive and tends to "pick a direction" (over-predicting decline 9,396 times and growth 6,268 times) rather than predicting the neutral stable class.

### Failure Mode C: Macro-Level Distribution Shift
* **Mechanism:** The model was trained on earlier temporal windows (Feb/Mar data, where platform-wide growth was ~45%). It was evaluated on a later out-of-time window (May data, where platform-wide growth crashed to ~22% and decline spiked to ~57%). 
* **Impact:** The model appears to have learned patterns from earlier periods that did not fully generalize to the later evaluation window, leading to under-predicting the severity of the May visibility decay.

## 4. Limitations Section

When presenting this model in production or academic literature, the following limitations must be explicitly acknowledged:

1. **Feature Sparsity (Missing Competitor Data):** The model lacks external off-page features (e.g., competitor backlink velocity, algorithmic update rollouts). It relies entirely on internal behavioral signals and static keyword dimensions, making it blind to sudden exogenous shocks.
2. **Short-Term Volatility:** The 30-day feature window makes the model highly reactive to short-term spikes (Failure Mode A). Smoothing features over a 90-day window could improve robustness at the cost of latency.
3. **Imbalanced Shift Bias:** The dataset exhibits extreme temporal distribution shift. A model trained on an earlier observation period with a higher proportion of growing pages will systematically over-predict growth when evaluated on a later observation period with substantially more declining pages. Continuous, rolling retraining is required in production to mitigate this drift.
