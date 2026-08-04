# Block 8: Explainability (SHAP)
**Search Health Scoring System**  
*Status: COMPLETED*

## 1. Interpretability Setup
Following the validation discipline, SHAP (SHapley Additive exPlanations) is applied **only** to the selected champion model (Random Forest) *after* model selection. We sampled 2,000 instances from the out-of-time Test Set to compute SHAP values efficiently.

## 2. Global Feature Importance

![Global Importance](file:///n:/gitt/search-health-prediction/work/shap_global_importance.png)

**Interpretation:**
The bar chart illustrates the mean absolute SHAP value for each feature across the three classes. 
* Momentum metrics (`imp_momentum`, `clicks_momentum`) and historical volume (`feat_impressions`) typically dominate the global importance.
* Static content attributes (`content_age_days`, `word_count`) provide secondary context for the model.

## 3. Directional Impacts

### Predicting "Growing"
![Growing Class](file:///n:/gitt/search-health-prediction/work/shap_growing.png)

**Interpretation:**
* **High `imp_momentum`** strongly pushes the model to predict the page will grow (red dots on the right side of the x-axis).
* **Low `feat_impressions`** combined with positive momentum often yields a high SHAP value for growth, capturing newly trending, low-baseline content.
* **Low `content_age_days`** (newer content) tends to have a positive impact on predicting growth, reflecting the "honeymoon" ranking phase of new content.

### Predicting "Declining"
![Declining Class](file:///n:/gitt/search-health-prediction/work/shap_declining.png)

**Interpretation:**
* **Low `imp_momentum`** (blue dots) strongly pushes the model to predict decline.
* **High `content_age_days`** (older content) acts as a strong decay indicator, pushing predictions toward decline.

## 4. Conclusion
The SHAP analysis indicates that the trained model primarily relies on recent momentum, historical traffic volume, and content age when making predictions. These learned patterns are broadly consistent with common SEO intuition. Older content with fading momentum is highly likely to decay, whereas newer content with explosive recent momentum is likely to grow.
