import pandas as pd
labels = pd.read_parquet('data/labels.parquet')
features = pd.read_parquet('data/features.parquet')
df = pd.merge(labels, features[['client_hash_id', 'content_hash_id', 'cutoff_date', 'split_role']], on=['client_hash_id', 'content_hash_id', 'cutoff_date'])
train_df = df[df['split_role'].isin(['train_1', 'train_2'])]
print(train_df['label'].value_counts(normalize=True))
print(train_df['label'].value_counts())
