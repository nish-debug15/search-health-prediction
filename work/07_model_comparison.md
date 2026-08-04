# Block 7: Model Comparison
**Search Health Scoring System**  
*Status: COMPLETED*  

## 1. Experimental Setup
* **Training Set**: `train_1` + `train_2` (Feb & Mar 2026 Cutoffs, 228,905 instances)
* **Validation Set**: `val` (Apr 2026 Cutoff, 151,248 instances) - used for XGBoost early stopping.
* **Test Set (OOT)**: `test` (May 2026 Cutoff, 168,375 instances).
* **Metric**: Macro F1-Score (unweighted mean across growing, stable, declining).

## 2. Preprocessing
* Categorical variables (`content_type`, `main_intent`) were One-Hot Encoded.
* Missing numerical values were imputed with the training median for RandomForest. XGBoost utilized its native sparsity-aware missing value handling.
* Target classes were label-encoded (`declining`: 0, `growing`: 1, `stable`: 2).

## 3. Results (Out-of-Time Test Set)

| Model | Macro F1-Score | Status |
| :--- | :---: | :--- |
| **Rule-Based Baseline** | 0.4399 | Heuristic (momentum-based) |
| **RandomForest** | 0.4871 | (`n_estimators=100`, `max_depth=10`, `class_weight='balanced'`) |
| **XGBoost (Champion)** | **0.4589** | Selected via early stopping on Validation |

**Conclusion:**
The **RandomForest** model achieved a Macro F1 of **0.4871**, successfully beating the baseline (0.4399). It has been saved as the champion model (`work/champion_model.*`) and will be used for interpretability (SHAP) in Block 8 and the ranking engine in Block 9.
