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
| **Majority-Class Baseline** | 0.1236 | Predicts "growing" |
| **Rule-Based Baseline** | 0.4399 | Heuristic (momentum-based) |
| **XGBoost** | 0.4600 | Selected via early stopping on Validation |
| **RandomForest (Champion)** | **0.4871** | (`n_estimators=100`, `max_depth=10`, `class_weight='balanced'`) |

**Conclusion:**
The Random Forest consistently outperformed the rule-based heuristic on the held-out out-of-time test set. It has been saved as the champion model (`work/champion_model.joblib`) and will be used for interpretability (SHAP) in Block 8 and the ranking engine in Block 9. See `07_confusion_matrices.md` for error analysis details.
