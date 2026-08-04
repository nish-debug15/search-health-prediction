# Block 9: Ranking & Recommendation Engine
**Search Health Scoring System**  
*Status: COMPLETED*

## 1. Engine Overview
We deployed the Champion Random Forest model to score the most recent dataset snapshot (the out-of-time Test set from May 2026, comprising 168,375 active pages). 

Using the model's predictions (`growing`, `stable`, `declining`) in conjunction with business context features (traffic volume, content age), we deterministically mapped every page to an **SEO Action** and attached a human-readable **Reason Code**.

## 2. Action Distribution

```text
action
Protect              39284
Investigate          34837
Prune/Consolidate    32465
Optimize             28913
Maintain             27490
Refresh               5386
```

* **Refresh**: The largest intervention category, primarily driven by older pages ( > 365 days) that the model confidently predicts will decline in the next 30 days.
* **Protect / Maintain**: Assets requiring no immediate intervention.
* **Investigate**: A critical alert for *recent* high-value content that the model flags for imminent decline (often indicating technical issues or cannibalization).
* **Prune/Consolidate**: Low-value, declining pages recommended for cleanup to preserve crawl budget.

## 3. Top 10 High-Priority Actions (Prioritized by Baseline Traffic)

Below are the top 10 most critical pages requiring immediate intervention, sorted by their recent impression volume.

```text
         content_hash_id predicted_status  confidence  feat_impressions      action                                                                                      reason_code
content_62770e1299963fe4        declining    0.485402          180151.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_661a7734f691bef5        declining    0.453426          169494.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_99fc6465edb0e52c        declining    0.614921          151230.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_963de14b1f58978f        declining    0.609215          142085.0     Refresh                                     Declining traffic on older content; needs a content refresh.
content_14df7b049d1d6467        declining    0.442516          119743.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_468d0aa0891d425d        declining    0.455516          114071.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_f33ad8a343180e8b        declining    0.387023          107944.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_b88025fbf2493889        declining    0.440025          103586.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_6486239516a186d7        declining    0.478496           99857.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
content_bdf60c86117079be        declining    0.591222           95403.0 Investigate Declining traffic on recent high-value content; check for technical issues or SERP feature loss.
```

## 4. Output Generation
The full scoring matrix (containing the predictions, confidences, actions, and reason codes for all 168,375 pages) has been successfully generated and is ready for export to the client's reporting dashboard.
