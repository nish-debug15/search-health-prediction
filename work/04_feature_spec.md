# Block 4: Feature Specification
**Search Health Scoring System**  
*Status: COMPLETED*  

---

## Overview
This specification details the 14 engineered features produced in Block 4. All features are strictly constructed using data from the 30-day feature window ($T_{feat}$) or time-invariant static properties from `dim_content`, mapped perfectly to the qualified modeling instances from Block 3.

## Feature Categories

### 1. Traffic Aggregates (Window = $T_{feat}$)
| Feature Name | Type | Description | Source | Imputation/Handling |
| :--- | :--- | :--- | :--- | :--- |
| `feat_impressions` | Numeric | Sum of daily GSC impressions. | `gsc_impressions` | None (qualified pages have $\ge 10$) |
| `feat_clicks` | Numeric | Sum of daily GSC clicks. | `gsc_clicks` | None |
| `feat_zero_imp_days` | Numeric | Number of days in $T_{feat}$ with 0 or null impressions. | `gsc_impressions` | Derived logically |
| `feat_avg_position` | Numeric | Average ranking position across days. | `gsc_avg_position` | Leave as Null if no data |

### 2. Derived Traffic & Engagement (Window = $T_{feat}$)
| Feature Name | Type | Description | Source | Imputation/Handling |
| :--- | :--- | :--- | :--- | :--- |
| `feat_ctr` | Numeric | Click-Through Rate: `(clicks * 100) / impressions`. | Derived | Safe division |
| `feat_pageviews` | Numeric | Sum of GA4 pageviews. | `ga4_pageviews` | Imputed to 0 if null |
| `feat_sessions` | Numeric | Sum of GA4 sessions. | `ga4_sessions` | Imputed to 0 if null |
| `has_ga4_data` | Binary | 1 if any GA4 data exists, else 0. | `ga4_sessions` | Missingness indicator |

### 3. Momentum Ratios (Split $T_{feat}$ into H1 and H2)
We split the 30-day feature window into H1 (Days 1–15) and H2 (Days 16–30) to capture short-term velocity before the cutoff date.
| Feature Name | Type | Description | Source | Formula |
| :--- | :--- | :--- | :--- | :--- |
| `imp_momentum` | Numeric | Growth velocity of impressions. | `gsc_impressions` | `(H2 + 1) / (H1 + 1)` |
| `clicks_momentum` | Numeric | Growth velocity of clicks. | `gsc_clicks` | `(H2 + 0.1) / (H1 + 0.1)` |

### 4. Content Dimension Features (Static & Age)
| Feature Name | Type | Description | Source | Imputation/Handling |
| :--- | :--- | :--- | :--- | :--- |
| `content_type` | Categorical | Type of content piece. | `dim_content` | None |
| `search_volume` | Numeric | Target keyword monthly search volume. | `dim_content` | Leave Null |
| `competition` | Numeric | Keyword competition (0-1). | `dim_content` | Leave Null |
| `main_intent` | Categorical | Search intent (Informational, etc). | `dim_content` | None |
| `backlinks` | Numeric | Number of inbound links. | `dim_content` | Leave Null |
| `word_count` | Numeric | Total word count. | `dim_content` | Leave Null |
| `content_age_days` | Numeric | Age of content relative to prediction cutoff date. | `dim_content.content_created_date` | `cutoff_date - content_created_date` |
