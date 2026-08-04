# Predictive Modeling of Search Engine Visibility Decay: A Machine Learning Approach for Proactive SEO

**Nishit Patel**  
*Machine Learning Capstone*  
*FlyRank ML Internship • August 2026*

A machine learning capstone project exploring whether historical search signals can predict the future health of web pages and generate ranked, actionable recommendations.

**Status:** Completed ✅  
**Champion Model:** Random Forest (`n_estimators=100`, `max_depth=10`, `class_weight='balanced'`)  
**Primary Metric (Macro F1):** 0.4871 (outperforming the Momentum Heuristic baseline of 0.4399)

---

## 📖 Research Paper
The full technical methodology, data pipeline, and failure analysis have been compiled into a professional academic publication.
* View the source text: [`research_paper.md`](research_paper.md)
* View the formatted HTML publication: [`docs/index.html`](docs/index.html) *(Optimized for GitHub Pages)*

---

## 🎯 Objectives
- Explore and understand the FlyRank Search Intelligence dataset.
- Engineer predictive, leakage-free search-performance features over a 30-day rolling window.
- Build a robust machine learning pipeline strictly partitioned by time (no random splits).
- Evaluate candidate models against a naive majority class and a rule-based momentum baseline.
- Interpret predictions using SHAP (SHapley Additive exPlanations).
- Construct a deterministic Recommendation Engine to map model probabilities to actionable SEO interventions (e.g., Investigate, Refresh, Prune).

---

## 📂 Final Repository Structure

```text
.
├── data/                            # Processed parquet dataset files
├── docs/                            # HTML documentation and academic paper build
│   ├── assets/                      # Generated analytical charts (PNGs)
│   └── index.html                   # Professional Anthropic-style editorial UI
├── work/                            # Python execution scripts
│   ├── 01_raw_data_extraction.py
│   ├── 02_cleaning.py
│   ├── 03_imputation.py
│   ├── ...
│   ├── 11_generate_charts.py
│   ├── champion_model.joblib        # Serialized Champion Random Forest
│   └── champion_features.txt        # Feature list
├── build_docs.py                    # Script to compile markdown & LaTeX to HTML
├── research_paper.md                # Final written report
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack
- **Data Engineering:** DuckDB, Pandas, NumPy, PyArrow (Parquet)
- **Machine Learning:** Scikit-learn, XGBoost
- **Interpretability:** SHAP
- **Visualization:** Matplotlib, Seaborn
- **Documentation Build:** Python Markdown, MathJax (KaTeX)

---

## 📊 Dataset
Built on the **FlyRank ML Internship Search Intelligence** dataset (approx. 93.4M raw warehouse rows, 548,528 qualified modeling instances).

> **Disclaimer:** This public repository exclusively contains normalized, anonymized features. It explicitly excludes all client-identifiable information, domains, URLs, raw queries, credentials, and private exports.

## 📄 License
Created for educational and research purposes during the FlyRank ML Internship (August 2026).
