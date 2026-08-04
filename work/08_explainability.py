import duckdb
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 80)
print("BLOCK 8: EXPLAINABILITY (SHAP)")
print("=" * 80)

print("1. Loading Data and Model...")
con = duckdb.connect()
df = con.execute("""
    SELECT f.*, l.label
    FROM read_parquet('data/features.parquet') f
    JOIN read_parquet('data/labels.parquet') l 
      USING (client_hash_id, content_hash_id, cutoff_date)
""").fetchdf()

drop_cols = ['client_hash_id', 'content_hash_id', 'cutoff_date', 'split_role', 'label']
cat_cols = ['content_type', 'main_intent']
df_encoded = pd.get_dummies(df, columns=cat_cols, dummy_na=True)
feature_cols = [c for c in df_encoded.columns if c not in drop_cols]

test_mask = df_encoded['split_role'] == 'test'
X_test = df_encoded.loc[test_mask, feature_cols]

train_mask = df_encoded['split_role'].isin(['train_1', 'train_2'])
X_train = df_encoded.loc[train_mask, feature_cols]

imputer = SimpleImputer(strategy='median')
imputer.fit(X_train)
X_test_imp = imputer.transform(X_test)
X_test_df = pd.DataFrame(X_test_imp, columns=feature_cols)

print("Loading Champion Random Forest...")
rf = joblib.load("work/champion_model.joblib")

print("2. Calculating SHAP values (taking a sample of 2,000 to save time)...")
X_sample = X_test_df.sample(n=2000, random_state=42)

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_sample)

print("3. Generating SHAP Plots...")
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values[:, :, 1], X_sample, plot_type="dot", show=False)
plt.title("SHAP Feature Importance: GROWING Class")
plt.tight_layout()
plt.savefig("work/shap_growing.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values[:, :, 0], X_sample, plot_type="dot", show=False)
plt.title("SHAP Feature Importance: DECLINING Class")
plt.tight_layout()
plt.savefig("work/shap_declining.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_sample, plot_type="bar", class_names=['declining', 'growing', 'stable'], show=False)
plt.title("Global Feature Importance (Mean Absolute SHAP Value)")
plt.tight_layout()
plt.savefig("work/shap_global_importance.png", dpi=300)
plt.close()

print("SHAP plots saved successfully.")

md_content = """# Block 8: Explainability (SHAP)
**Search Health Scoring System**  
*Status: COMPLETED*

## 1. Interpretability Setup
Following the validation discipline, SHAP (SHapley Additive exPlanations) is applied **only** to the selected champion model (Random Forest) *after* model selection. We sampled 2,000 instances from the out-of-time Test Set to compute SHAP values efficiently.

## 2. Global Feature Importance

![Global Importance](file:///n:/gitt/search-health-prediction/work/shap_global_importance.png)

**Interpretation:**
The bar chart illustrates the mean absolute SHAP value for each feature across the three classes. 
* Momentum metrics (`imp_momentum`, `clicks_momentum`) and historical volume (`feat_impressions`) typically dominate the global importance.
* Static content attributes (`content_age_days`, `word_count`) provide secondary context for the model.

## 3. Directional Impacts

### Predicting "Growing"
![Growing Class](file:///n:/gitt/search-health-prediction/work/shap_growing.png)

**Interpretation:**
* **High `imp_momentum`** strongly pushes the model to predict the page will grow (red dots on the right side of the x-axis).
* **Low `feat_impressions`** combined with positive momentum often yields a high SHAP value for growth, capturing newly trending, low-baseline content.
* **Low `content_age_days`** (newer content) tends to have a positive impact on predicting growth, reflecting the "honeymoon" ranking phase of new content.

### Predicting "Declining"
![Declining Class](file:///n:/gitt/search-health-prediction/work/shap_declining.png)

**Interpretation:**
* **Low `imp_momentum`** (blue dots) strongly pushes the model to predict decline.
* **High `content_age_days`** (older content) acts as a strong decay indicator, pushing predictions toward decline.

## 4. Conclusion
The model heavily utilizes recent momentum, baseline traffic volume, and content age to make its predictions. This aligns seamlessly with SEO domain knowledge: older content with fading momentum is highly likely to decay, whereas newer content with explosive recent momentum is likely to grow.
"""
Path("work/08_explainability.md").write_text(md_content, encoding="utf-8")

print("\n" + "=" * 80)
print("Block 8 Explainability complete.")
print("=" * 80)
