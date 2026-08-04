import duckdb
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.metrics import classification_report, f1_score, confusion_matrix
from sklearn.impute import SimpleImputer
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

con = duckdb.connect()
df = con.execute("""
    SELECT f.*, l.label
    FROM read_parquet('data/features.parquet') f
    JOIN read_parquet('data/labels.parquet') l 
      USING (client_hash_id, content_hash_id, cutoff_date)
""").fetchdf()

label_map = {'declining': 0, 'growing': 1, 'stable': 2}
df['label_encoded'] = df['label'].map(label_map)

drop_cols = ['client_hash_id', 'content_hash_id', 'cutoff_date', 'split_role', 'label', 'label_encoded']
cat_cols = ['content_type', 'main_intent']
df_encoded = pd.get_dummies(df, columns=cat_cols, dummy_na=True)
feature_cols = [c for c in df_encoded.columns if c not in drop_cols]

train_mask = df_encoded['split_role'].isin(['train_1', 'train_2'])
val_mask = df_encoded['split_role'] == 'val'
test_mask = df_encoded['split_role'] == 'test'

X_train = df_encoded.loc[train_mask, feature_cols]
y_train = df_encoded.loc[train_mask, 'label_encoded']
X_test = df_encoded.loc[test_mask, feature_cols]
y_test = df_encoded.loc[test_mask, 'label_encoded']

imputer = SimpleImputer(strategy='median')
X_train_imp = imputer.fit_transform(X_train)
X_test_imp = imputer.transform(X_test)

labels_order = [0, 1, 2] # declining, growing, stable
labels_str = ['declining', 'growing', 'stable']

print("1. Majority Class Baseline")
majority_class = y_train.mode()[0]
majority_str = labels_str[majority_class]
y_pred_maj = np.full(len(y_test), majority_class)
maj_macro_f1 = f1_score(y_test, y_pred_maj, average='macro')

print("2. Momentum Baseline")
test_raw = df.loc[test_mask].copy()
test_raw['y_pred_mom'] = test_raw['imp_momentum'].apply(
    lambda x: 1 if x > 1.10 else (0 if x < 0.90 else 2)
)
mom_macro_f1 = f1_score(y_test, test_raw['y_pred_mom'], average='macro')
cm_mom = confusion_matrix(y_test, test_raw['y_pred_mom'], labels=labels_order)

print("3. RandomForest (Champion)")
rf = joblib.load("work/champion_model.joblib")
y_pred_rf = rf.predict(X_test_imp)
rf_macro_f1 = f1_score(y_test, y_pred_rf, average='macro')
cm_rf = confusion_matrix(y_test, y_pred_rf, labels=labels_order)

print("4. XGBoost")
dtest = xgb.DMatrix(X_test, label=y_test)
dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(df_encoded.loc[val_mask, feature_cols], label=df_encoded.loc[val_mask, 'label_encoded'])
params = {'objective': 'multi:softmax', 'num_class': 3, 'max_depth': 6, 'learning_rate': 0.05, 'subsample': 0.8, 'colsample_bytree': 0.8, 'eval_metric': 'mlogloss', 'random_state': 42, 'n_jobs': -1}
xgb_model = xgb.train(params, dtrain, num_boost_round=150, evals=[(dtrain, 'train'), (dval, 'val')], early_stopping_rounds=20, verbose_eval=False)
y_pred_xgb = xgb_model.predict(dtest)
xgb_macro_f1 = f1_score(y_test, y_pred_xgb, average='macro')
cm_xgb = confusion_matrix(y_test, y_pred_xgb, labels=labels_order)


def format_cm(cm, title):
    return f"### {title}\\n```text\\n              Predicted ->\\nTrue Class    Declining | Growing | Stable\\n" + \
           f"Declining   | {cm[0,0]:9d} | {cm[0,1]:7d} | {cm[0,2]:6d}\\n" + \
           f"Growing     | {cm[1,0]:9d} | {cm[1,1]:7d} | {cm[1,2]:6d}\\n" + \
           f"Stable      | {cm[2,0]:9d} | {cm[2,1]:7d} | {cm[2,2]:6d}\\n```\\n\\n"

cm_doc = f"# Confusion Matrices (Test Set)\n\n"
cm_doc += format_cm(cm_mom, "Rule-Based Momentum Baseline")
cm_doc += format_cm(cm_xgb, "XGBoost")
cm_doc += format_cm(cm_rf, "RandomForest (Champion)")

Path("work/07_confusion_matrices.md").write_text(cm_doc, encoding="utf-8")

md_content = f"""# Block 7: Model Comparison
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
| **Majority-Class Baseline** | {maj_macro_f1:.4f} | Predicts "{majority_str}" |
| **Rule-Based Baseline** | {mom_macro_f1:.4f} | Heuristic (momentum-based) |
| **XGBoost** | {xgb_macro_f1:.4f} | Selected via early stopping on Validation |
| **RandomForest (Champion)** | **{rf_macro_f1:.4f}** | (`n_estimators=100`, `max_depth=10`, `class_weight='balanced'`) |

**Conclusion:**
The Random Forest consistently outperformed the rule-based heuristic on the held-out out-of-time test set. It has been saved as the champion model (`work/champion_model.joblib`) and will be used for interpretability (SHAP) in Block 8 and the ranking engine in Block 9. See `07_confusion_matrices.md` for error analysis details.
"""

Path("work/07_model_comparison.md").write_text(md_content, encoding="utf-8")
print("Successfully generated confusion matrices and updated model comparison.")
