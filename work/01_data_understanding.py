# -*- coding: utf-8 -*-
"""01_data_understanding.py — Explore the FlyRank Internship Warehouse star schema."""

import duckdb
import pandas as pd
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.max_colwidth", 60)
pd.set_option("display.width", 220)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    for tp in [Path.home() / ".cache" / "huggingface" / "token", Path.home() / ".huggingface" / "token"]:
        if tp.exists():
            HF_TOKEN = tp.read_text().strip()
            break
if not HF_TOKEN:
    sys.exit("[ERROR] No HF_TOKEN found. Add it to .env or set as env var.")

DATASET = "FlyRank/internship-warehouse"
HF_BASE = f"hf://datasets/{DATASET}"

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute(f"CREATE SECRET hf_secret (TYPE HUGGINGFACE, TOKEN '{HF_TOKEN}');")
print(f"[OK] DuckDB {duckdb.__version__}, HF auth ready.\n")

KNOWN_TABLES = ["dim_clients", "dim_content", "dim_queries", "fact_daily", "bridge_content_query"]
SENSITIVE_KEYWORDS = ["url", "domain", "query", "keyword", "site", "host", "page_path"]

# ── Discovery ────────────────────────────────────────────────────────────
print("=" * 90)
print(f"BLOCK 1: DATA UNDERSTANDING — {DATASET}")
print("=" * 90)
print("\n--- Step 1: Table Discovery ---\n")

discovered = []
for tname in KNOWN_TABLES:
    patterns = [
        f"{HF_BASE}/data/{tname}-*.parquet",
        f"{HF_BASE}/{tname}-*.parquet",
        f"{HF_BASE}/data/{tname}/*.parquet",
        f"{HF_BASE}/data/{tname}.parquet",
    ]
    for pat in patterns:
        try:
            con.execute(f"SELECT 1 FROM read_parquet('{pat}') LIMIT 1").fetchone()
            print(f"  [OK] {tname:30s} -> {pat}")
            discovered.append((tname, pat))
            break
        except:
            continue
    else:
        print(f"  [--] {tname:30s} -> not found")

print(f"\n  Discovered {len(discovered)} tables.")
if not discovered:
    sys.exit("[ERROR] No tables found. Check HF token & dataset access.")

# ── Profiling ─────────────────────────────────────────────────────────────
print("\n--- Step 2: Table Profiling ---\n")

inventory = []

for tname, tpath in discovered:
    print("=" * 90)
    print(f"  TABLE: {tname}")
    print("=" * 90)

    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{tpath}')").fetchdf()
    print(f"\n  Columns ({len(schema)}):")
    for _, r in schema.iterrows():
        print(f"    {r['column_name']:50s} {r['column_type']}")

    cnt = con.execute(f"SELECT COUNT(*) FROM read_parquet('{tpath}')").fetchone()[0]
    print(f"\n  Rows: {cnt:,}")

    sample = con.execute(f"SELECT * FROM read_parquet('{tpath}') LIMIT 5").fetchdf()
    sensitive = [c for c in sample.columns if any(k in c.lower() for k in SENSITIVE_KEYWORDS)]
    safe_sample = sample.copy()
    for sc in sensitive:
        safe_sample[sc] = "[REDACTED]"
    print(f"\n  Sample (5 rows):\n{safe_sample.to_string(index=False)}")

    cols = list(schema["column_name"])
    null_sql = ", ".join(f'SUM(CASE WHEN "{c}" IS NULL THEN 1 ELSE 0 END) AS "{c}__n"' for c in cols)
    nulls = con.execute(f"SELECT {null_sql} FROM read_parquet('{tpath}')").fetchdf()
    print("\n  Missing values:")
    any_miss = False
    for c in cols:
        n = int(nulls[f"{c}__n"].iloc[0])
        if n > 0:
            print(f"    {c:50s} {n:>12,}  ({n / cnt * 100:.1f}%)")
            any_miss = True
    if not any_miss:
        print("    (none)")

    date_cols = schema[schema["column_type"].str.upper().str.contains("DATE|TIMESTAMP", na=False)]["column_name"].tolist()
    str_cols = schema[schema["column_type"].str.upper().str.contains("VARCHAR", na=False)]["column_name"].tolist()
    date_like_str = [c for c in str_cols if any(k in c.lower() for k in ["date", "time", "day", "month", "year", "week", "start", "end"])]
    all_dates = date_cols + date_like_str

    if all_dates:
        print("\n  Date ranges:")
        for dc in all_dates:
            try:
                r = con.execute(f'SELECT MIN("{dc}"), MAX("{dc}"), COUNT(DISTINCT "{dc}") FROM read_parquet(\'{tpath}\')').fetchone()
                print(f"    {dc:50s} {r[0]}  ->  {r[1]}  ({r[2]:,} unique)")
            except Exception as e:
                print(f"    {dc:50s} (error: {e})")

    num_cols = schema[schema["column_type"].str.upper().str.contains(r"INT|BIGINT|DOUBLE|FLOAT|DECIMAL|REAL|NUMERIC", na=False)]["column_name"].tolist()
    if num_cols:
        print("\n  Numeric stats:")
        for nc in num_cols[:20]:
            try:
                s = con.execute(
                    f'SELECT MIN("{nc}"), MAX("{nc}"), ROUND(AVG("{nc}"),2), ROUND(MEDIAN("{nc}"),2), '
                    f'ROUND(STDDEV("{nc}"),2), COUNT(DISTINCT "{nc}") FROM read_parquet(\'{tpath}\')'
                ).fetchone()
                print(f"    {nc:50s} min={s[0]}  max={s[1]}  mean={s[2]}  med={s[3]}  std={s[4]}  uniq={s[5]:,}")
            except Exception as e:
                print(f"    {nc:50s} (error: {e})")

    safe_str = [c for c in str_cols if c not in sensitive]
    if safe_str:
        print("\n  String cardinality:")
        for sc in safe_str[:10]:
            try:
                u = con.execute(f"SELECT COUNT(DISTINCT \"{sc}\") FROM read_parquet('{tpath}')").fetchone()[0]
                print(f"    {sc:50s} {u:>12,} unique")
                if u <= 25:
                    top = con.execute(f'SELECT "{sc}", COUNT(*) AS n FROM read_parquet(\'{tpath}\') GROUP BY "{sc}" ORDER BY n DESC LIMIT 15').fetchdf()
                    for _, tr in top.iterrows():
                        print(f"      > {tr.iloc[0]}: {tr.iloc[1]:,}")
            except:
                pass

    if sensitive:
        print("\n  Sensitive columns (values hidden):")
        for sc in sensitive:
            try:
                u = con.execute(f"SELECT COUNT(DISTINCT \"{sc}\") FROM read_parquet('{tpath}')").fetchone()[0]
                print(f"    {sc:50s} {u:>12,} unique")
            except:
                pass

    try:
        dist = con.execute(f"SELECT COUNT(*) FROM (SELECT DISTINCT * FROM read_parquet('{tpath}'))").fetchone()[0]
        dups = cnt - dist
        print(f"\n  Duplicate rows: {dups:,} ({dups / cnt * 100:.2f}%)")
    except Exception as e:
        print(f"\n  Duplicate check: {e}")

    inventory.append({
        "name": tname, "path": tpath, "rows": cnt, "columns": len(schema),
        "schema": schema.to_dict("records"), "date_cols": all_dates,
        "num_cols": num_cols, "str_cols": str_cols, "sensitive_cols": sensitive,
    })
    print()

# ── Join Keys ─────────────────────────────────────────────────────────────
print("\n--- Step 3: Join Key Analysis ---\n")

col_sets = [(t["name"], {r["column_name"] for r in t["schema"]}) for t in inventory]
for i in range(len(col_sets)):
    for j in range(i + 1, len(col_sets)):
        common = col_sets[i][1] & col_sets[j][1]
        if common:
            print(f"  {col_sets[i][0]}  <-->  {col_sets[j][0]}:  {sorted(common)}")

print("\n  Key columns per table:")
for tbl in inventory:
    keys = [r["column_name"] for r in tbl["schema"]
            if any(k in r["column_name"].lower() for k in ["_id", "_key", "_hash"]) or r["column_name"].lower().endswith("id")]
    if keys:
        print(f"    {tbl['name']:30s} {keys}")

# ── Summary ───────────────────────────────────────────────────────────────
print("\n\n--- Step 4: Summary ---\n")
print(f"  {'Table':<30s} {'Rows':>15s} {'Cols':>6s}")
print(f"  {'-'*30} {'-'*15} {'-'*6}")
total_rows = 0
for t in inventory:
    print(f"  {t['name']:<30s} {t['rows']:>15,} {t['columns']:>6}")
    total_rows += t["rows"]
print(f"\n  Total: {total_rows:,} rows")
print("\n" + "=" * 90)
print("Block 1 complete.")
print("=" * 90)
