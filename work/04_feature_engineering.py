# -*- coding: utf-8 -*-
"""04_feature_engineering.py — Engineer leakage-free features for modeling."""

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

print("=" * 80)
print("BLOCK 4: FEATURE ENGINEERING")
print("=" * 80)

HF = "hf://datasets/FlyRank/internship-warehouse"
FACT = f"{HF}/fact_content_daily_performance/*/*.parquet"
DIM_CONTENT = f"{HF}/dim_content.parquet"
CLEAN_DATA = "data/clean_qualified_instances.parquet"

print("1. Loading base instances into memory...")
con.execute(f"CREATE TABLE base_instances AS SELECT * FROM read_parquet('{CLEAN_DATA}')")

print("2. Extracting feature window fact records (partition pruned)...")
# The earliest feat_start is 2026-01-16, latest is 2026-05-14.
con.execute(f"""
    CREATE TABLE feat_facts AS 
    SELECT f.*, b.cutoff_date, b.feat_start, b.feat_end 
    FROM read_parquet('{FACT}', hive_partitioning=true) f
    INNER JOIN base_instances b 
      ON f.client_hash_id = b.client_hash_id 
     AND f.content_hash_id = b.content_hash_id
    WHERE f.month IN ('2026-01', '2026-02', '2026-03', '2026-04', '2026-05')
      AND f.report_date BETWEEN b.feat_start AND b.feat_end
""")

print("3. Computing aggregates and momentum features...")
con.execute("""
    CREATE TABLE feat_agg AS
    SELECT 
        client_hash_id, 
        content_hash_id, 
        cutoff_date,
        
        -- Traffic Aggregates
        SUM(gsc_impressions) AS feat_impressions,
        SUM(gsc_clicks) AS feat_clicks,
        COUNT(CASE WHEN gsc_impressions = 0 OR gsc_impressions IS NULL THEN 1 END) AS feat_zero_imp_days,
        AVG(gsc_avg_position) AS feat_avg_position,
        
        -- GA4 Features (Handling missingness)
        MAX(CASE WHEN ga4_sessions IS NOT NULL THEN 1 ELSE 0 END) AS has_ga4_data,
        SUM(COALESCE(ga4_pageviews, 0)) AS feat_pageviews,
        SUM(COALESCE(ga4_sessions, 0)) AS feat_sessions,
        
        -- Momentum (H1 vs H2 of the 30-day window)
        SUM(CASE WHEN report_date <= feat_start + INTERVAL 14 DAY THEN gsc_impressions ELSE 0 END) AS imp_h1,
        SUM(CASE WHEN report_date > feat_start + INTERVAL 14 DAY THEN gsc_impressions ELSE 0 END) AS imp_h2,
        SUM(CASE WHEN report_date <= feat_start + INTERVAL 14 DAY THEN gsc_clicks ELSE 0 END) AS clicks_h1,
        SUM(CASE WHEN report_date > feat_start + INTERVAL 14 DAY THEN gsc_clicks ELSE 0 END) AS clicks_h2
    FROM feat_facts
    GROUP BY client_hash_id, content_hash_id, cutoff_date
""")

print("4. Joining with static dimensions and finalizing features...")
con.execute(f"""
    CREATE TABLE final_features AS
    SELECT 
        b.client_hash_id,
        b.content_hash_id,
        b.split_role,
        b.cutoff_date,
        
        -- Aggregates
        a.feat_impressions,
        a.feat_clicks,
        a.feat_zero_imp_days,
        a.feat_avg_position,
        a.has_ga4_data,
        a.feat_pageviews,
        a.feat_sessions,
        
        -- Derived Traffic Ratios
        (a.imp_h2 + 1.0) / (a.imp_h1 + 1.0) AS imp_momentum,
        (a.clicks_h2 + 0.1) / (a.clicks_h1 + 0.1) AS clicks_momentum,
        (a.feat_clicks * 100.0) / NULLIF(a.feat_impressions, 0) AS feat_ctr,
        
        -- Content Dimension Features
        d.content_type,
        d.search_volume,
        d.competition,
        d.main_intent,
        d.backlinks,
        d.word_count,
        
        -- Temporal feature: age at cutoff (Strictly Leakage-Free)
        DATE_DIFF('day', d.content_created_date, b.cutoff_date) AS content_age_days
        
    FROM base_instances b
    LEFT JOIN feat_agg a 
      ON b.client_hash_id = a.client_hash_id 
     AND b.content_hash_id = a.content_hash_id 
     AND b.cutoff_date = a.cutoff_date
    LEFT JOIN read_parquet('{DIM_CONTENT}') d 
      ON b.client_hash_id = d.client_hash_id 
     AND b.content_hash_id = d.content_hash_id
""")

output_path = 'data/features.parquet'
con.execute(f"COPY (SELECT * FROM final_features) TO '{output_path}' (FORMAT PARQUET, COMPRESSION ZSTD)")
print(f"\nSuccessfully engineered features and saved to {output_path}")

summary = con.execute("SELECT split_role, COUNT(*) as count FROM final_features GROUP BY split_role ORDER BY split_role").fetchdf()
print("\n--- Instances per Split ---")
print(summary.to_string(index=False))

cols = con.execute("DESCRIBE final_features").fetchdf()
feat_cols = [c for c in cols['column_name'] if c not in ['client_hash_id', 'content_hash_id', 'split_role', 'cutoff_date']]
print(f"\n--- Total Engineered Features: {len(feat_cols)} ---")

print("\n--- Sample of final feature matrix (first 1 row) ---")
# limit columns for display to avoid huge spam
print(con.execute("SELECT * FROM final_features LIMIT 1").fetchdf().T)

print("\n" + "=" * 80)
print("Block 4 Feature Engineering complete.")
print("=" * 80)
