# Block 3: Exclusions & Clean Dataset
**Search Health Scoring System**  
*Status: COMPLETED*  
*Date: August 2026*

---

## 1. Exclusion Criteria & Data Integrity

To ensure our predictive model trains strictly on reliable, active content pages, we established and verified several exclusion rules across the 2026 panel (Jan–Jun).

### 1.1 Join & Structural Integrity
All daily performance rows were validated against the dimension tables to ensure referential integrity.
* **Missing Keys**: 0 rows with null `client_hash_id` or `content_hash_id`.
* **Invalid Dates**: 0 rows with missing `report_date`.
* **Orphans**: 0 orphaned fact rows. Every `(client_hash_id, content_hash_id)` in the fact table successfully joined to `dim_content`. No structural exclusions were required.

### 1.2 Client-Level Exclusions (GSC vs. GA4)
* **Zero GSC Activity**: Out of 70 total clients present in the 2026 data, **5 clients had 0 total GSC impressions** across the entire timeline. Pages from these clients are naturally excluded by our minimum activity filter.
* **Missing GA4 Data Strategy**: As identified in Block 1, 37.6% of rows have null GA4 metrics due to clients without GA4 integrations. **We do NOT exclude these clients**, as our prediction target is based entirely on GSC search visibility. Excluding them would introduce extreme selection bias. Instead, missing GA4 metrics will be handled via feature engineering (imputation to 0 + binary `has_ga4_data` flags) in Block 4.

### 1.3 Minimum Activity Filter (Locked from Block 2)
The most significant data reduction occurs during the transition from the raw daily fact table to the modeling instance level. For a page to qualify at a given cutoff date ($t_0$), it must:
1. Appear in both the feature window ($T_{feat}$) and prediction window ($T_{pred}$).
2. Accumulate $\ge 10$ GSC impressions across the 30-day feature window ($T_{feat}$).

---

## 2. Exclusion Audit (Waterfall)

The following waterfall demonstrates the impact of our exclusions across the four locked modeling cutoff windows:

| Metric | `train_1` (Feb 15) | `train_2` (Mar 15) | `val` (Apr 15) | `test` (May 15) |
| :--- | :--- | :--- | :--- | :--- |
| **Total Active Pages in Window** | 337,899 | 362,619 | 375,627 | 399,247 |
| **Present in Both (Feat & Pred)** | 269,067 | 319,584 | 346,198 | 375,627 |
| **Non-Zero Impressions in Both** | 118,480 | 148,308 | 168,261 | 192,404 |
| **Qualified ($\ge 10$ Feat Imp)** | **100,192** | **128,713** | **151,248** | **168,375** |

*(Note: About 70-75% of "active" pages fail the minimum activity filter, confirming that the vast majority of indexed URLs are ultra-low-volume or zero-signal pages that should not be modeled.)*

---

## 3. Clean Dataset Output

The final, filtered base dataset has been compiled and saved locally. 

* **File Location**: `data/clean_qualified_instances.parquet` (Excluded from git tracking via `.gitignore`)
* **Format**: ZSTD-compressed Parquet
* **Total Instances**: **548,528** (Union of `train_1`, `train_2`, `val`, and `test`)
* **Instance Definition**: Each row uniquely represents a `(client_hash_id, content_hash_id, cutoff_date)` combination, serving as the exact foundation for Feature Engineering (Block 4) and Label Generation (Block 5).

### Clean Panel Summary

| Split Role | Cutoff Date | Qualified Instances | Avg Feature Impressions | Median Feature Impressions |
| :--- | :--- | :--- | :--- | :--- |
| **Train 1** | 2026-02-15 | 100,192 | 1,582.5 | 296.0 |
| **Train 2** | 2026-03-15 | 128,713 | 1,786.1 | 316.0 |
| **Validation** | 2026-04-15 | 151,248 | 1,916.5 | 310.0 |
| **Test** | 2026-05-15 | 168,375 | 1,636.5 | 220.0 |

This completes Block 3. The pipeline is now ready for Block 4: Feature Engineering.
