# Predictive Modeling of Search Engine Visibility Decay: A Machine Learning Approach for Proactive SEO

## 1. Abstract
Search Engine Optimization (SEO) traditionally relies on reactive analytics—diagnosing traffic loss after it has already occurred. This paper introduces a proactive machine learning methodology to forecast short-term search visibility changes (Growth, Stability, or Decline) for individual web pages before they manifest. Utilizing the FlyRank Internship Warehouse dataset, we engineered a deterministic, leakage-free pipeline with a rolling 30-day feature window predicting a subsequent 30-day horizon. Evaluated on a strictly out-of-time test set, our Champion Random Forest classifier achieved a Macro F1 score of 0.4871, successfully outperforming a rule-based momentum heuristic (0.4399). SHAP explainability confirms the model learns robust patterns aligned with SEO intuition, heavily weighting recent momentum, historical volume, and content age. The pipeline culminates in a recommendation engine that assigns automated, prioritized interventions (e.g., Refresh, Prune, Investigate) to mitigate projected decay.

## 2. Introduction
In digital marketing, organic search traffic is highly volatile due to fluctuating user intent, competitor maneuvers, and search engine algorithm updates. Most enterprise SEO practices rely on manual heuristics and lagging indicators to identify decaying content. This research proposes a predictive scoring system that identifies which URLs are most likely to lose visibility over the next 30 days, enabling content teams to intervene proactively. 

## 3. Problem Statement
The primary objective is to classify a web page's future 30-day traffic trajectory into three mutually exclusive categories: **Growing**, **Stable**, or **Declining**. The system must operate without looking ahead (preventing temporal leakage), must outperform standard manual heuristics, and must translate raw predictions into actionable SEO interventions.

## 4. Dataset
We utilized the public `FlyRank/internship-warehouse` dataset, which contains high-resolution daily performance records (Google Search Console, Google Analytics 4) and static content dimensions for thousands of URLs. 
* **Data Scale:** The raw fact table contained over 132 million rows.
* **Qualified Instances:** After rigorously applying an activity filter (requiring $\ge 10$ impressions in the feature window) and ensuring valid join integrity, we extracted a clean modeling dataset of **548,528 valid instances**.

## 5. Methodology
To prevent look-ahead bias, we established strict, rolling observation windows:
* **Feature Window ($T_{feat}$):** 30 days of historical data used to engineer predictive features.
* **Prediction Window ($T_{pred}$):** The subsequent 30 days used exclusively to compute the target label.
This structural isolation guarantees that no future information leaks into the training matrix.

## 6. Feature Engineering
We engineered a matrix of 17 leakage-free features per instance, categorized as follows:
* **Traffic Aggregates:** Total impressions, clicks, average position, and zero-impression days over $T_{feat}$.
* **Derived Engagement:** GA4 sessions, pageviews, and Click-Through Rate (CTR).
* **Momentum Ratios:** Growth velocity comparing the second half of the feature window against the first half (`imp_momentum`, `clicks_momentum`).
* **Content Dimensions:** Time-invariant properties (search volume, keyword intent, content type) and dynamically calculated `content_age_days`.

## 7. Label Definition
The target variable is a multiclass label defined by the relative percentage change in impressions between the Prediction Window and the Feature Window:
$$\Delta\% = \frac{\text{Impressions}_{pred} - \text{Impressions}_{feat}}{\text{Impressions}_{feat}}$$
* **Growing:** $\Delta\% > +20\%$
* **Stable:** $-20\% \le \Delta\% \le +20\%$
* **Declining:** $\Delta\% < -20\%$

## 8. Validation Strategy
We implemented a strict out-of-time (OOT) validation strategy to simulate a real-world production environment and prevent temporal data leakage:
* **Train:** `train_1` (Feb 2026 Cutoff) + `train_2` (Mar 2026 Cutoff) — 228,905 instances
* **Validation:** `val` (Apr 2026 Cutoff) — 151,248 instances
* **Test (OOT):** `test` (May 2026 Cutoff) — 168,375 instances

The primary evaluation metric selected was **Macro F1-Score** to account for significant class imbalance observed across the temporal splits.

## 9. Baseline
We established a rule-based **Momentum Heuristic** as a naive baseline: predicting that the traffic direction observed in the final 15 days of the feature window will continue into the prediction window.
* **Test Set Baseline Macro F1:** 0.4399
* *Analysis:* The baseline is highly reactive, performing adequately at identifying decline but struggling severely to accurately predict stable traffic.

## 10. Modeling Results
Two candidate models (RandomForest, XGBoost) were trained on the identical feature matrix and evaluated against the baseline on the May 2026 Test Set.

| Model | Macro F1-Score | Status |
| :--- | :---: | :--- |
| Rule-Based Baseline | 0.4399 | Momentum Heuristic |
| XGBoost | 0.4589 | Selected via early stopping on Validation |
| **RandomForest (Champion)** | **0.4871** | `n_estimators=100`, `max_depth=10`, `class_weight='balanced'` |

The Random Forest consistently outperformed both the XGBoost candidate and the rule-based heuristic on the held-out out-of-time test set.

## 11. Explainability (SHAP)
To ensure the model learned generalizable domain patterns rather than spurious noise, we applied SHAP (SHapley Additive exPlanations) to the Champion Random Forest model.

The SHAP analysis indicates that the trained model primarily relies on three core factors:
1. **Recent Momentum (`imp_momentum`)**
2. **Historical Volume (`feat_impressions`)**
3. **Content Age (`content_age_days`)**

These learned patterns are broadly consistent with common SEO intuition: older content with fading momentum is highly likely to decay, whereas newer content with explosive recent momentum is likely to grow.

## 12. Recommendation Engine
To translate probabilistic predictions into actionable business strategy, we deployed a deterministic Recommendation Engine over the May 2026 snapshot. The engine maps the predicted status and business context to specific SEO interventions:

| Predicted Status | Business Context | Action |
| :--- | :--- | :--- |
| Growing | Any | **Protect** |
| Stable | High Traffic (`feat_impressions` > 1000) | **Maintain** |
| Stable | Low Traffic (`feat_impressions` \le 1000) | **Optimize** |
| Declining | Old Content (`content_age_days` > 365) | **Refresh** |
| Declining | Recent High-Value Content (`feat_impressions` \ge 100) | **Investigate** |
| Declining | Low-Value Content (`feat_impressions` < 100) | **Prune / Consolidate** |

This output allows content teams to immediately prioritize high-value assets flagged for imminent decline (e.g., triggering an "Investigate" or "Refresh" workflow).

## 13. Failure Analysis
An extensive error analysis on the test set (Overall Error Rate: 47.8%) revealed three primary failure profiles:
1. **The "False Growth" Trap:** Transient, viral spikes in the feature window cause the model to over-predict sustained growth, failing to anticipate rapid regression to the mean.
2. **The "Stability" Illusion:** The inherent daily volatility of SERP rankings makes the $\pm 20\%$ stability band notoriously difficult to hit; the model tends to over-predict directional movement (Growth/Decline) instead.
3. **Macro-Level Distribution Shift:** The model was trained on earlier temporal windows with a higher proportion of growing pages and evaluated on a later out-of-time window with substantially more declining pages.

## 14. Limitations
When evaluating this system for production, the following limitations must be explicitly acknowledged:
* **Feature Sparsity:** The model relies entirely on internal behavioral signals and static keyword dimensions. It lacks external off-page features (e.g., competitor backlink velocity), making it blind to sudden exogenous shocks.
* **Short-Term Volatility:** The 30-day feature window makes the model highly reactive to short-term noise.
* **Imbalanced Shift Bias:** The model appears to have learned patterns from earlier periods that did not fully generalize to the later evaluation window. Continuous, rolling retraining is required in production to mitigate temporal drift.

## 15. Reproducibility
All data cleaning, feature engineering, modeling, and evaluation scripts have been committed to a central repository. The pipeline is 100% deterministic, utilizing fixed random seeds and strictly ordered temporal splits.

## 16. Acknowledgments
This research was made possible by the `FlyRank/internship-warehouse` dataset, which provided the high-resolution, multi-dimensional web traffic data required to build and evaluate this predictive architecture.
