# -*- coding: utf-8 -*-
"""05_label_generation.py — Generate strictly isolated labels from prediction window data."""

import duckdb
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 80)
print("BLOCK 5: LABEL GENERATION")
print("=" * 80)

CLEAN_DATA = "data/clean_qualified_instances.parquet"
OUTPUT_DATA = "data/labels.parquet"

con = duckdb.connect()

print("1. Computing percentage change and applying frozen thresholds (X = +/- 20%)...")
con.execute(f"""
    CREATE TABLE labels AS
    SELECT 
        client_hash_id,
        content_hash_id,
        cutoff_date,
        split_role,
        feat_imp,
        pred_imp,
        (pred_imp - feat_imp)::DOUBLE / feat_imp AS pct_change,
        CASE 
            WHEN ((pred_imp - feat_imp)::DOUBLE / feat_imp) > 0.20 THEN 'growing'
            WHEN ((pred_imp - feat_imp)::DOUBLE / feat_imp) BETWEEN -0.20 AND 0.20 THEN 'stable'
            WHEN ((pred_imp - feat_imp)::DOUBLE / feat_imp) < -0.20 THEN 'declining'
        END AS label
    FROM read_parquet('{CLEAN_DATA}')
""")

print("2. Saving labels to parquet...")
con.execute(f"COPY (SELECT client_hash_id, content_hash_id, cutoff_date, label, pct_change FROM labels) TO '{OUTPUT_DATA}' (FORMAT PARQUET, COMPRESSION ZSTD)")

print(f"Successfully generated labels and saved to {OUTPUT_DATA}")

print("\n--- 3. Sanity Checks & Label Distribution ---")
distribution = con.execute("""
    SELECT 
        split_role,
        COUNT(*) AS total_instances,
        ROUND(100.0 * SUM(CASE WHEN label = 'growing' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_growing,
        ROUND(100.0 * SUM(CASE WHEN label = 'stable' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_stable,
        ROUND(100.0 * SUM(CASE WHEN label = 'declining' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_declining
    FROM labels
    GROUP BY split_role
    ORDER BY split_role
""").fetchdf()

print(distribution.to_string(index=False))

# Verify missingness
null_labels = con.execute("SELECT COUNT(*) FROM labels WHERE label IS NULL").fetchone()[0]
if null_labels > 0:
    print(f"\n[WARNING] Found {null_labels} instances with NULL labels!")
else:
    print("\n[OK] 0 instances with NULL labels. All instances successfully labeled.")

print("\n" + "=" * 80)
print("Block 5 Label Generation complete.")
print("=" * 80)
