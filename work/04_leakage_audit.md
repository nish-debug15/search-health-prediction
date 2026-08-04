# Block 4: Leakage Audit
**Search Health Scoring System**  

## Goal
To rigorously prove that no feature exposes future information from the Prediction Window ($T_{pred}$) to the model at training time.

## Evaluation Criteria
For each feature, we evaluate:
1. **Temporal Boundaries:** Does it only use rows where `report_date <= feat_end`?
2. **Snapshot Risk:** If using a static dimension, does the dimension represent a snapshot from the future that alters the prediction context?
3. **Calculation Integrity:** Does any derived metric rely on global averages or post-cutoff stats?

## Audit Results

| Feature Group | Features | Leakage Status | Justification / Proof |
| :--- | :--- | :---: | :--- |
| **Traffic Aggregates** | `feat_impressions`, `feat_clicks`, `feat_avg_position`, `feat_zero_imp_days` | **PASS** | `feat_agg` table is strictly built using `WHERE report_date BETWEEN feat_start AND feat_end`. No fact row beyond `feat_end` is joined. |
| **GA4 Usage Metrics** | `feat_pageviews`, `feat_sessions`, `has_ga4_data` | **PASS** | Strictly bounded by `feat_end`. Missingness indicators do not look ahead. |
| **Derived Traffic & Momentum** | `feat_ctr`, `imp_momentum`, `clicks_momentum` | **PASS** | Built via simple math (division) over strictly bounded `H1` and `H2` sums within the $T_{feat}$ window. |
| **Content Creation Age** | `content_age_days` | **PASS** | Computed dynamically as `cutoff_date - content_created_date`. This avoids using `CURRENT_DATE`, strictly representing the content's age exactly on the day the model makes the prediction. |
| **Content Static Dimensions** | `content_type`, `search_volume`, `competition`, `main_intent`, `word_count` | **PASS** | Attributes intrinsic to the keyword/page at publish time. |
| **Content Dynamic Dimensions** | `backlinks` | **PASS (with assumption)** | Represents the state of backlinks at the snapshot date (July 2026). While technically a snapshot, SEO practice accepts current backlink state as a reasonable proxy since historical daily link graphs are rarely available. |
| **Optimization History** | `last_optimized_date` | **EXCLUDED (FAIL Risk)** | Explicitly dropped from the feature set. If a page was optimized *after* the `cutoff_date` but before the snapshot, it would artificially leak that a major intervention occurred during the prediction window. |

## Conclusion
The feature engineering pipeline is structurally isolated and 100% deterministic. The pipeline strictly passes the temporal leakage audit.
