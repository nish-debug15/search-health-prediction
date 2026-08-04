# -*- coding: utf-8 -*-
"""06_baseline.py — Establish train/val/test split and evaluate naive baseline."""

import duckdb
import pandas as pd
from sklearn.metrics import classification_report, f1_score
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 80)
print("BLOCK 6: TIME-AWARE SPLIT & BASELINE")
print("=" * 80)

FEATURES = "data/features.parquet"
LABELS = "data/labels.parquet"

con = duckdb.connect()

print("1. Joining Features and Labels...")
con.execute(f"""
    CREATE TABLE dataset AS
    SELECT f.*, l.label, l.pct_change
    FROM read_parquet('{FEATURES}') f
    JOIN read_parquet('{LABELS}') l 
      USING (client_hash_id, content_hash_id, cutoff_date)
""")

print("2. Generating Rule-Based Baseline Predictions on Test Set...")
# Baseline Logic: Predict based on recent momentum (last 15 days vs previous 15 days)
# If momentum > 1.1 -> growing. If < 0.9 -> declining. Else -> stable.
test_df = con.execute("""
    SELECT 
        label AS y_true,
        CASE 
            WHEN imp_momentum > 1.10 THEN 'growing'
            WHEN imp_momentum < 0.90 THEN 'declining'
            ELSE 'stable'
        END AS y_pred
    FROM dataset
    WHERE split_role = 'test'
""").fetchdf()

y_true = test_df['y_true']
y_pred = test_df['y_pred']

print("\n--- Baseline Model Performance (Test Set) ---")
print("Rule: imp_momentum > 1.1 (Growing), < 0.9 (Declining), Else (Stable)\n")

# Calculate metrics
# Note: target_names will be automatically mapped to sorted unique labels: declining, growing, stable
labels_order = ['declining', 'growing', 'stable']
report = classification_report(y_true, y_pred, labels=labels_order, target_names=labels_order)
print(report)

macro_f1 = f1_score(y_true, y_pred, average='macro', labels=labels_order)
print(f"BASELINE MACRO F1: {macro_f1:.4f}")

print("\n3. Writing results to work/06_split_and_baseline.md...")

md_content = f"""# Block 6: Time-Aware Split & Baseline
**Search Health Scoring System**  
*Status: COMPLETED*  

## 1. Time-Aware Split Diagram

As established in Block 2 and implemented in Block 3, our splits are strictly ordered in time to prevent temporal leakage:

```text
DATASET TIMELINE (Jan 2026 -----------------------------------------> June 2026)

|--- TRAIN_1 ---| (100,192 instances)
Feat: Jan 16 - Feb 14  |  Pred: Feb 15 - Mar 16  (Cutoff: Feb 15)

         |--- TRAIN_2 ---| (128,713 instances)
         Feat: Feb 13 - Mar 14  |  Pred: Mar 15 - Apr 13  (Cutoff: Mar 15)

                  |--- VALIDATION ---| (151,248 instances)
                  Feat: Mar 16 - Apr 14  |  Pred: Apr 15 - May 14  (Cutoff: Apr 15)

                           |--- TEST (OOT) ---| (168,375 instances)
                           Feat: Apr 15 - May 14  |  Pred: May 15 - Jun 13  (Cutoff: May 15)
```

## 2. Baseline Model Performance

Before training advanced machine learning models (Block 7), we must establish a naive baseline. 

**Baseline Strategy (Recent Momentum Predictor)**:
The most intuitive SEO heuristic is that whatever direction traffic was moving in the last 15 days, it will continue in the next 30 days. We use the engineered `imp_momentum` feature:
* Predict **Growing**: if `imp_momentum` > 1.10
* Predict **Declining**: if `imp_momentum` < 0.90
* Predict **Stable**: otherwise

**Test Set Evaluation (Out-of-Time Cutoff: May 15, 2026)**
* Total Instances: 168,375
* **Macro F1-Score: {macro_f1:.4f}**

```text
{report}
```

**Conclusion**: The Machine Learning models in Block 7 must strictly beat a Macro F1 of **{macro_f1:.4f}** on the out-of-time Test set to be considered viable.
"""

Path("work/06_split_and_baseline.md").write_text(md_content, encoding="utf-8")

print("\n" + "=" * 80)
print("Block 6 Split & Baseline complete.")
print("=" * 80)
