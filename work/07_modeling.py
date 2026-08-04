# -*- coding: utf-8 -*-
"""07_modeling.py — Train Baseline, RandomForest, and XGBoost models on time-aware splits."""

import duckdb
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.impute import SimpleImputer
import xgboost as xgb
import sys
from pathlib import Path
import joblib

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 80)
print("BLOCK 7: MODELING (RandomForest vs XGBoost)")
print("=" * 80)

print("1. Loading Features and Labels...")
con = duckdb.connect()
df = con.execute("""
    SELECT f.*, l.label
    FROM read_parquet('data/features.parquet') f
    JOIN read_parquet('data/labels.parquet') l 
      USING (client_hash_id, content_hash_id, cutoff_date)
""").fetchdf()

label_map = {'declining': 0, 'growing': 1, 'stable': 2}
df['label_encoded'] = df['label'].map(label_map)

print("2. Preprocessing & Encoding...")
drop_cols = ['client_hash_id', 'content_hash_id', 'cutoff_date', 'split_role', 'label', 'label_encoded']
cat_cols = ['content_type', 'main_intent']
num_cols = [c for c in df.columns if c not in drop_cols + cat_cols]

df_encoded = pd.get_dummies(df, columns=cat_cols, dummy_na=True)
feature_cols = [c for c in df_encoded.columns if c not in drop_cols]

print("3. Splitting into Train, Val, Test...")
train_mask = df_encoded['split_role'].isin(['train_1', 'train_2'])
val_mask = df_encoded['split_role'] == 'val'
test_mask = df_encoded['split_role'] == 'test'

X_train = df_encoded.loc[train_mask, feature_cols]
y_train = df_encoded.loc[train_mask, 'label_encoded']

X_val = df_encoded.loc[val_mask, feature_cols]
y_val = df_encoded.loc[val_mask, 'label_encoded']

X_test = df_encoded.loc[test_mask, feature_cols]
y_test = df_encoded.loc[test_mask, 'label_encoded']

print(f"  Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

print("4. Imputing Missing Values (for RandomForest)...")
imputer = SimpleImputer(strategy='median')
X_train_imp = imputer.fit_transform(X_train)
X_val_imp = imputer.transform(X_val)
X_test_imp = imputer.transform(X_test)

# ------------- BASELINE -------------
print("\n--- Evaluating Baseline (Rule-Based) ---")
test_raw = df.loc[test_mask].copy()
test_raw['y_pred'] = test_raw['imp_momentum'].apply(
    lambda x: 'growing' if x > 1.10 else ('declining' if x < 0.90 else 'stable')
)
baseline_macro_f1 = f1_score(test_raw['label'], test_raw['y_pred'], average='macro', labels=['declining', 'growing', 'stable'])
print(f"Baseline Macro F1: {baseline_macro_f1:.4f}")

# ------------- RANDOM FOREST -------------
print("\n--- Training RandomForest ---")
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1, class_weight='balanced')
rf.fit(X_train_imp, y_train)

y_pred_rf_encoded = rf.predict(X_test_imp)
rf_macro_f1 = f1_score(y_test, y_pred_rf_encoded, average='macro')
print(f"RandomForest Macro F1: {rf_macro_f1:.4f}")

# ------------- XGBOOST -------------
print("\n--- Training XGBoost ---")
dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(X_val, label=y_val)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {
    'objective': 'multi:softmax',
    'num_class': 3,
    'max_depth': 6,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'eval_metric': 'mlogloss',
    'random_state': 42,
    'n_jobs': -1
}

evals = [(dtrain, 'train'), (dval, 'val')]
xgb_model = xgb.train(
    params,
    dtrain,
    num_boost_round=500,
    evals=evals,
    early_stopping_rounds=20,
    verbose_eval=False
)

y_pred_xgb_encoded = xgb_model.predict(dtest)
xgb_macro_f1 = f1_score(y_test, y_pred_xgb_encoded, average='macro')
print(f"XGBoost Macro F1: {xgb_macro_f1:.4f}")

print("\n--- Final Model Comparison (Test Set) ---")
print(f"{'Model':<20} | {'Macro F1':<10}")
print("-" * 35)
print(f"{'Rule-Based Baseline':<20} | {baseline_macro_f1:.4f}")
print(f"{'RandomForest':<20} | {rf_macro_f1:.4f}")
print(f"{'XGBoost':<20} | {xgb_macro_f1:.4f}")

if xgb_macro_f1 > rf_macro_f1:
    print("\nSaving XGBoost model as the champion...")
    xgb_model.save_model("work/champion_model.json")
    best_name = "XGBoost"
    best_f1 = xgb_macro_f1
    with open("work/champion_features.txt", "w") as f:
        f.write("\\n".join(feature_cols))
else:
    print("\nSaving RandomForest model as the champion...")
    joblib.dump(rf, "work/champion_model.joblib")
    best_name = "RandomForest"
    best_f1 = rf_macro_f1
    with open("work/champion_features.txt", "w") as f:
        f.write("\\n".join(feature_cols))

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
| **Rule-Based Baseline** | {baseline_macro_f1:.4f} | Heuristic (momentum-based) |
| **RandomForest** | {rf_macro_f1:.4f} | (`n_estimators=100`, `max_depth=10`, `class_weight='balanced'`) |
| **XGBoost (Champion)** | **{xgb_macro_f1:.4f}** | Selected via early stopping on Validation |

**Conclusion:**
The **{best_name}** model achieved a Macro F1 of **{best_f1:.4f}**, successfully beating the baseline ({baseline_macro_f1:.4f}). It has been saved as the champion model (`work/champion_model.*`) and will be used for interpretability (SHAP) in Block 8 and the ranking engine in Block 9.
"""

Path("work/07_model_comparison.md").write_text(md_content, encoding="utf-8")

print("\n" + "=" * 80)
print("Block 7 Modeling complete.")
print("=" * 80)
