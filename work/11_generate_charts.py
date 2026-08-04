import os
import shutil
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix
from sklearn.impute import SimpleImputer

# Ensure output directory exists
os.makedirs('docs/assets', exist_ok=True)

# Set global style for professional look
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Arial']

print("1. Generating Label Distribution Chart...")
# Known distribution for train_1 + train_2
labels = ['Growing', 'Declining', 'Stable']
counts = [98588, 74910, 55407]
colors = ['#3b82f6', '#ef4444', '#94a3b8']

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(labels, counts, color=colors, alpha=0.9, edgecolor='black', linewidth=1)
ax.set_title('Training Set Label Distribution (Feb & Mar 2026)', fontsize=14, pad=15, fontweight='bold')
ax.set_ylabel('Number of Pages', fontsize=12)
ax.set_xlabel('Classification', fontsize=12)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1000,
            f'{height:,}', ha='center', va='bottom', fontsize=11, fontweight='500')

sns.despine(left=True)
plt.tight_layout()
plt.savefig('docs/assets/label_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

print("2. Generating Model Comparison Chart...")
models = ['Majority Class', 'Rule-Based\n(Momentum)', 'XGBoost', 'Random Forest\n(Champion)']
f1_scores = [0.1236, 0.4399, 0.4600, 0.4871]
colors = ['#cbd5e1', '#94a3b8', '#64748b', '#3b82f6']

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(models, f1_scores, color=colors, alpha=0.9, edgecolor='black', linewidth=1)
ax.set_title('Model Performance Comparison (Test Set Macro F1)', fontsize=14, pad=15, fontweight='bold')
ax.set_ylabel('Macro F1 Score', fontsize=12)
ax.set_ylim(0, 0.55)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{height:.4f}', ha='center', va='bottom', fontsize=11, fontweight='500')

sns.despine(left=True)
plt.tight_layout()
plt.savefig('docs/assets/model_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("3. Generating Confusion Matrix Chart...")
# Need to load data to generate actual confusion matrix for champion model
con = duckdb.connect()
df = con.execute("""
    SELECT f.*, l.label
    FROM read_parquet('data/features.parquet') f
    JOIN read_parquet('data/labels.parquet') l 
      USING (client_hash_id, content_hash_id, cutoff_date)
""").fetchdf()

label_map = {'declining': 0, 'growing': 1, 'stable': 2}
rev_map = {0: 'Declining', 1: 'Growing', 2: 'Stable'}
df['label_encoded'] = df['label'].map(label_map)

drop_cols = ['client_hash_id', 'content_hash_id', 'cutoff_date', 'split_role', 'label', 'label_encoded']
cat_cols = ['content_type', 'main_intent']
df_encoded = pd.get_dummies(df, columns=cat_cols, dummy_na=True)
feature_cols = [c for c in df_encoded.columns if c not in drop_cols]

test_mask = df_encoded['split_role'] == 'test'
train_mask = df_encoded['split_role'].isin(['train_1', 'train_2'])

X_train = df_encoded.loc[train_mask, feature_cols]
X_test = df_encoded.loc[test_mask, feature_cols]
y_test = df_encoded.loc[test_mask, 'label_encoded'].values

imputer = SimpleImputer(strategy='median')
imputer.fit(X_train)
X_test_imp = imputer.transform(X_test)

rf = joblib.load("work/champion_model.joblib")
y_pred = rf.predict(X_test_imp)

cm = confusion_matrix(y_test, y_pred, labels=[0, 2, 1]) # Ordering: Declining, Stable, Growing
target_names = ['Declining', 'Stable', 'Growing']

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt=',d', cmap='Blues',
            xticklabels=target_names, yticklabels=target_names, ax=ax,
            annot_kws={"size": 12, "weight": "bold"}, cbar=False)

ax.set_title('Confusion Matrix: Champion Random Forest (Test Set)', fontsize=14, pad=15, fontweight='bold')
ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('docs/assets/confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

print("4. Copying SHAP charts to docs/assets...")
shutil.copy2('work/shap_global_importance.png', 'docs/assets/shap_global_importance.png')
shutil.copy2('work/shap_declining.png', 'docs/assets/shap_declining.png')

print("Charts successfully generated and saved to docs/assets/")
