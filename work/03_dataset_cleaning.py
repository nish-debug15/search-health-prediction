# -*- coding: utf-8 -*-
"""03_dataset_cleaning.py — Implement & document exclusions, build clean dataset."""

import duckdb
import pandas as pd
import os, sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    for tp in [Path.home() / ".cache" / "huggingface" / "token"]:
        if tp.exists(): HF_TOKEN = tp.read_text().strip()

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute(f"CREATE SECRET hf_secret (TYPE HUGGINGFACE, TOKEN '{HF_TOKEN}');")

HF = "hf://datasets/FlyRank/internship-warehouse"
FACT = f"{HF}/fact_content_daily_performance/*/*.parquet"
DIM_CLIENTS = f"{HF}/dim_clients.parquet"
DIM_CONTENT = f"{HF}/dim_content.parquet"

print("=" * 80)
print("BLOCK 3: EXCLUSIONS & CLEAN DATASET BUILD")
print("=" * 80)

# 1. Join Integrity & Structural Integrity Check (using 2026 data with partition pruning for speed)
print("\n--- 1. Join Integrity & Structural Integrity Check (2026 Panel) ---\n")

integrity_sql = f"""
    WITH fact_summary AS (
        SELECT COUNT(*) AS total_fact_rows,
               COUNT(DISTINCT client_hash_id) AS n_fact_clients,
               COUNT(DISTINCT content_hash_id) AS n_fact_content,
               SUM(CASE WHEN report_date IS NULL THEN 1 ELSE 0 END) AS null_dates,
               SUM(CASE WHEN client_hash_id IS NULL THEN 1 ELSE 0 END) AS null_clients,
               SUM(CASE WHEN content_hash_id IS NULL THEN 1 ELSE 0 END) AS null_content
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE month >= '2026-01' AND month <= '2026-06'
    ),
    dim_cl AS (SELECT COUNT(*) AS total_clients FROM read_parquet('{DIM_CLIENTS}')),
    dim_co AS (SELECT COUNT(*) AS total_content FROM read_parquet('{DIM_CONTENT}')),
    orphans AS (
        SELECT COUNT(DISTINCT f.content_hash_id) AS orphan_content_count
        FROM read_parquet('{FACT}', hive_partitioning=true) f
        LEFT JOIN read_parquet('{DIM_CONTENT}') c USING (client_hash_id, content_hash_id)
        WHERE f.month >= '2026-01' AND f.month <= '2026-06' AND c.content_hash_id IS NULL
    )
    SELECT * FROM fact_summary, dim_cl, dim_co, orphans
"""
res = con.execute(integrity_sql).fetchdf()
print(res.to_string(index=False))

# 2. Check for clients with zero GSC activity
print("\n--- 2. Client-Level GSC Activity Audit ---\n")
client_audit_sql = f"""
    SELECT 
        CASE WHEN total_imp > 0 THEN 'Active GSC' ELSE 'No GSC Data' END AS client_status,
        COUNT(*) AS n_clients
    FROM (
        SELECT client_hash_id, SUM(gsc_impressions) AS total_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE month >= '2026-01' AND month <= '2026-06'
        GROUP BY client_hash_id
    )
    GROUP BY 1
"""
print(con.execute(client_audit_sql).fetchdf().to_string(index=False))

# 3. Build Clean Qualified Instances across our 4 modeling windows
print("\n--- 3. Evaluating Exclusions & Building Clean Panel per Cutoff Window ---\n")

windows = [
    ("train_1", "2026-02-15", "2026-01-16", "2026-02-14", "2026-02-15", "2026-03-16", "'2026-01', '2026-02', '2026-03'"),
    ("train_2", "2026-03-15", "2026-02-13", "2026-03-14", "2026-03-15", "2026-04-13", "'2026-02', '2026-03', '2026-04'"),
    ("val",     "2026-04-15", "2026-03-16", "2026-04-14", "2026-04-15", "2026-05-14", "'2026-03', '2026-04', '2026-05'"),
    ("test",    "2026-05-15", "2026-04-15", "2026-05-14", "2026-05-15", "2026-06-13", "'2026-04', '2026-05', '2026-06'")
]

audit_rows = []
union_queries = []

for role, cutoff, fw_start, fw_end, pw_start, pw_end, months_in in windows:
    step_sql = f"""
        WITH all_pages AS (
            SELECT DISTINCT client_hash_id, content_hash_id
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE month IN ({months_in}) AND report_date BETWEEN '{fw_start}' AND '{pw_end}'
        ),
        feat_stats AS (
            SELECT client_hash_id, content_hash_id,
                   COUNT(*) AS feat_days,
                   SUM(gsc_impressions) AS feat_imp,
                   SUM(gsc_clicks) AS feat_clicks
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE month IN ({months_in}) AND report_date BETWEEN '{fw_start}' AND '{fw_end}'
            GROUP BY 1, 2
        ),
        pred_stats AS (
            SELECT client_hash_id, content_hash_id,
                   COUNT(*) AS pred_days,
                   SUM(gsc_impressions) AS pred_imp,
                   SUM(gsc_clicks) AS pred_clicks
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE month IN ({months_in}) AND report_date BETWEEN '{pw_start}' AND '{pw_end}'
            GROUP BY 1, 2
        ),
        joined AS (
            SELECT a.client_hash_id, a.content_hash_id,
                   COALESCE(f.feat_imp, 0) AS feat_imp,
                   COALESCE(p.pred_imp, 0) AS pred_imp,
                   COALESCE(f.feat_days, 0) AS feat_days,
                   COALESCE(p.pred_days, 0) AS pred_days
            FROM all_pages a
            LEFT JOIN feat_stats f USING (client_hash_id, content_hash_id)
            LEFT JOIN pred_stats p USING (client_hash_id, content_hash_id)
        )
        SELECT 
            '{role}' AS split_role,
            '{cutoff}' AS cutoff_date,
            COUNT(*) AS step0_total_active_in_period,
            SUM(CASE WHEN feat_days > 0 AND pred_days > 0 THEN 1 ELSE 0 END) AS step1_both_windows,
            SUM(CASE WHEN feat_imp > 0 AND pred_imp > 0 THEN 1 ELSE 0 END) AS step2_non_zero_both,
            SUM(CASE WHEN feat_imp >= 10 AND pred_days > 0 THEN 1 ELSE 0 END) AS step3_qualified_min_10_imp
        FROM joined
    """
    row = con.execute(step_sql).fetchdf()
    audit_rows.append(row)
    print(f"Audited {role} (Cutoff {cutoff}): {row['step3_qualified_min_10_imp'].iloc[0]:,} qualified instances out of {row['step0_total_active_in_period'].iloc[0]:,} total.")
    
    q_sql = f"""
        SELECT 
            client_hash_id,
            content_hash_id,
            '{role}' AS split_role,
            DATE '{cutoff}' AS cutoff_date,
            DATE '{fw_start}' AS feat_start,
            DATE '{fw_end}' AS feat_end,
            DATE '{pw_start}' AS pred_start,
            DATE '{pw_end}' AS pred_end,
            SUM(CASE WHEN report_date BETWEEN '{fw_start}' AND '{fw_end}' THEN gsc_impressions ELSE 0 END) AS feat_imp,
            SUM(CASE WHEN report_date BETWEEN '{pw_start}' AND '{pw_end}' THEN gsc_impressions ELSE 0 END) AS pred_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE month IN ({months_in}) AND report_date BETWEEN '{fw_start}' AND '{pw_end}'
        GROUP BY 1, 2
        HAVING feat_imp >= 10 
           AND SUM(CASE WHEN report_date BETWEEN '{pw_start}' AND '{pw_end}' THEN 1 ELSE 0 END) > 0
    """
    union_queries.append(q_sql)

audit_df = pd.concat(audit_rows, ignore_index=True)
print("\n--- Summary Audit Table ---")
print(audit_df.to_string(index=False))

# 4. Save Clean Qualified Instances to Local Parquet
print("\n--- 4. Building & Saving Clean Qualified Instances Dataset ---\n")
Path("data").mkdir(exist_ok=True)
output_parquet = "data/clean_qualified_instances.parquet"

full_union_sql = " UNION ALL ".join(union_queries)
con.execute(f"""
    COPY ({full_union_sql}) TO '{output_parquet}' (FORMAT PARQUET, COMPRESSION ZSTD);
""")

# Verify saved parquet
summary_df = con.execute(f"""
    SELECT split_role, cutoff_date, COUNT(*) AS n_instances,
           ROUND(AVG(feat_imp), 1) AS avg_feat_imp,
           ROUND(MEDIAN(feat_imp), 1) AS med_feat_imp
    FROM read_parquet('{output_parquet}')
    GROUP BY split_role, cutoff_date
    ORDER BY cutoff_date
""").fetchdf()
print(f"Saved clean qualified instances to: {output_parquet}")
print(summary_df.to_string(index=False))

print("\n" + "=" * 80)
print("Block 3 dataset cleaning complete.")
print("=" * 80)
