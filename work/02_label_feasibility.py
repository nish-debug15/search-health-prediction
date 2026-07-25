# -*- coding: utf-8 -*-
"""02_label_feasibility.py — Validate label & window design against actual data."""

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

print("=" * 80)
print("BLOCK 2: LABEL FEASIBILITY ANALYSIS")
print("=" * 80)

# 1. Temporal coverage: how many content pages have data per month?
print("\n--- 1. Monthly content coverage ---\n")
monthly = con.execute(f"""
    SELECT month,
           COUNT(DISTINCT content_hash_id) AS n_content,
           COUNT(DISTINCT client_hash_id) AS n_clients,
           COUNT(*) AS n_rows,
           SUM(gsc_impressions) AS total_impressions,
           SUM(gsc_clicks) AS total_clicks
    FROM read_parquet('{FACT}', hive_partitioning=true)
    GROUP BY month ORDER BY month
""").fetchdf()
print(monthly.to_string(index=False))

# 2. For a 30-day feature window + 30-day prediction window, how many pages
#    have data in BOTH windows?
print("\n--- 2. Window overlap feasibility (30d feature + 30d predict) ---\n")
print("Testing multiple cutoff dates...\n")

cutoffs = [
    ("2026-01-15", "2025-12-16", "2026-01-14", "2026-01-15", "2026-02-13"),
    ("2026-02-15", "2026-01-16", "2026-02-14", "2026-02-15", "2026-03-16"),
    ("2026-03-15", "2026-02-13", "2026-03-14", "2026-03-15", "2026-04-13"),
    ("2026-04-15", "2026-03-16", "2026-04-14", "2026-04-15", "2026-05-14"),
    ("2026-05-01", "2026-04-01", "2026-04-30", "2026-05-01", "2026-05-30"),
    ("2026-05-15", "2026-04-15", "2026-05-14", "2026-05-15", "2026-06-13"),
]

for label, fw_start, fw_end, pw_start, pw_end in cutoffs:
    r = con.execute(f"""
        WITH feature_pages AS (
            SELECT client_hash_id, content_hash_id,
                   SUM(gsc_impressions) AS feat_impressions
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE report_date BETWEEN '{fw_start}' AND '{fw_end}'
            GROUP BY 1, 2
        ),
        predict_pages AS (
            SELECT client_hash_id, content_hash_id,
                   SUM(gsc_impressions) AS pred_impressions
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE report_date BETWEEN '{pw_start}' AND '{pw_end}'
            GROUP BY 1, 2
        )
        SELECT COUNT(*) AS n_pages,
               SUM(CASE WHEN feat_impressions > 0 AND pred_impressions > 0 THEN 1 ELSE 0 END) AS both_active,
               SUM(CASE WHEN feat_impressions > 0 THEN 1 ELSE 0 END) AS feat_active,
               SUM(CASE WHEN pred_impressions > 0 THEN 1 ELSE 0 END) AS pred_active
        FROM feature_pages f
        FULL OUTER JOIN predict_pages p USING (client_hash_id, content_hash_id)
    """).fetchone()
    print(f"  Cutoff {label}: feat=[{fw_start},{fw_end}] pred=[{pw_start},{pw_end}]")
    print(f"    Total pages: {r[0]:,}  Both active: {r[1]:,}  Feat only: {r[2]:,}  Pred only: {r[3]:,}")

# 3. Label distribution test: using impressions % change with ±20% thresholds
print("\n--- 3. Label distribution test (impressions % change, thresholds ±20%) ---\n")

label_test = con.execute(f"""
    WITH feature_window AS (
        SELECT client_hash_id, content_hash_id,
               SUM(gsc_impressions) AS feat_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE report_date BETWEEN '2026-04-01' AND '2026-04-30'
        GROUP BY 1, 2
        HAVING SUM(gsc_impressions) >= 10
    ),
    predict_window AS (
        SELECT client_hash_id, content_hash_id,
               SUM(gsc_impressions) AS pred_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE report_date BETWEEN '2026-05-01' AND '2026-05-30'
        GROUP BY 1, 2
    ),
    joined AS (
        SELECT f.client_hash_id, f.content_hash_id,
               f.feat_imp, COALESCE(p.pred_imp, 0) AS pred_imp,
               (COALESCE(p.pred_imp, 0) - f.feat_imp)::DOUBLE / f.feat_imp AS pct_change
        FROM feature_window f
        LEFT JOIN predict_window p USING (client_hash_id, content_hash_id)
    )
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN pct_change > 0.20 THEN 1 ELSE 0 END) AS growing,
        SUM(CASE WHEN pct_change BETWEEN -0.20 AND 0.20 THEN 1 ELSE 0 END) AS stable,
        SUM(CASE WHEN pct_change < -0.20 THEN 1 ELSE 0 END) AS declining,
        ROUND(AVG(pct_change), 4) AS mean_change,
        ROUND(MEDIAN(pct_change), 4) AS median_change,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY pct_change), 4) AS p25,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pct_change), 4) AS p75
    FROM joined
""").fetchone()

total, growing, stable, declining = label_test[0], label_test[1], label_test[2], label_test[3]
print(f"  Feature: Apr 2026 | Predict: May 2026 | Min impressions: 10")
print(f"  Total pages: {total:,}")
print(f"  Growing (>+20%):  {growing:,} ({growing/total*100:.1f}%)")
print(f"  Stable  (+-20%):  {stable:,} ({stable/total*100:.1f}%)")
print(f"  Declining (<-20%): {declining:,} ({declining/total*100:.1f}%)")
print(f"  Mean change: {label_test[4]}, Median: {label_test[5]}, P25: {label_test[6]}, P75: {label_test[7]}")

# 4. Try different thresholds
print("\n--- 4. Threshold sensitivity ---\n")
for thresh in [0.10, 0.15, 0.20, 0.25, 0.30, 0.50]:
    r = con.execute(f"""
        WITH feature_window AS (
            SELECT client_hash_id, content_hash_id,
                   SUM(gsc_impressions) AS feat_imp
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE report_date BETWEEN '2026-04-01' AND '2026-04-30'
            GROUP BY 1, 2 HAVING SUM(gsc_impressions) >= 10
        ),
        predict_window AS (
            SELECT client_hash_id, content_hash_id,
                   SUM(gsc_impressions) AS pred_imp
            FROM read_parquet('{FACT}', hive_partitioning=true)
            WHERE report_date BETWEEN '2026-05-01' AND '2026-05-30'
            GROUP BY 1, 2
        ),
        joined AS (
            SELECT f.feat_imp, COALESCE(p.pred_imp, 0) AS pred_imp,
                   (COALESCE(p.pred_imp, 0) - f.feat_imp)::DOUBLE / f.feat_imp AS pct_change
            FROM feature_window f LEFT JOIN predict_window p USING (client_hash_id, content_hash_id)
        )
        SELECT COUNT(*) AS total,
               ROUND(100.0 * SUM(CASE WHEN pct_change > {thresh} THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_grow,
               ROUND(100.0 * SUM(CASE WHEN pct_change BETWEEN -{thresh} AND {thresh} THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_stable,
               ROUND(100.0 * SUM(CASE WHEN pct_change < -{thresh} THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_decline
        FROM joined
    """).fetchone()
    print(f"  +/-{thresh:.0%}: Growing={r[1]}% Stable={r[2]}% Declining={r[3]}%  (n={r[0]:,})")

# 5. Check another window pair for consistency
print("\n--- 5. Cross-check: Mar->Apr label distribution ---\n")
r2 = con.execute(f"""
    WITH fw AS (
        SELECT client_hash_id, content_hash_id, SUM(gsc_impressions) AS feat_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE report_date BETWEEN '2026-03-01' AND '2026-03-31'
        GROUP BY 1, 2 HAVING SUM(gsc_impressions) >= 10
    ),
    pw AS (
        SELECT client_hash_id, content_hash_id, SUM(gsc_impressions) AS pred_imp
        FROM read_parquet('{FACT}', hive_partitioning=true)
        WHERE report_date BETWEEN '2026-04-01' AND '2026-04-30'
        GROUP BY 1, 2
    ),
    j AS (
        SELECT (COALESCE(pw.pred_imp, 0) - fw.feat_imp)::DOUBLE / fw.feat_imp AS pct_change
        FROM fw LEFT JOIN pw USING (client_hash_id, content_hash_id)
    )
    SELECT COUNT(*),
           ROUND(100.0 * SUM(CASE WHEN pct_change > 0.20 THEN 1 ELSE 0 END) / COUNT(*), 1),
           ROUND(100.0 * SUM(CASE WHEN pct_change BETWEEN -0.20 AND 0.20 THEN 1 ELSE 0 END) / COUNT(*), 1),
           ROUND(100.0 * SUM(CASE WHEN pct_change < -0.20 THEN 1 ELSE 0 END) / COUNT(*), 1)
    FROM j
""").fetchone()
print(f"  Mar->Apr (+-20%): Growing={r2[1]}% Stable={r2[2]}% Declining={r2[3]}%  (n={r2[0]:,})")

# 6. Pages with sufficient history for multiple windows
print("\n--- 6. Temporal depth per content page ---\n")
depth = con.execute(f"""
    SELECT
        CASE
            WHEN n_months >= 12 THEN '12+ months'
            WHEN n_months >= 6 THEN '6-11 months'
            WHEN n_months >= 3 THEN '3-5 months'
            ELSE '1-2 months'
        END AS depth_bucket,
        COUNT(*) AS n_pages
    FROM (
        SELECT content_hash_id, COUNT(DISTINCT month) AS n_months
        FROM read_parquet('{FACT}', hive_partitioning=true)
        GROUP BY content_hash_id
    )
    GROUP BY 1 ORDER BY 1
""").fetchdf()
print(depth.to_string(index=False))

print("\n" + "=" * 80)
print("Block 2 feasibility analysis complete.")
print("=" * 80)
