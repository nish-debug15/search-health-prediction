# Block 6: Time-Aware Split & Baseline
**Search Health Scoring System**  
*Status: COMPLETED*  

## 1. Time-Aware Split Diagram

As established in Block 2 and implemented in Block 3, our splits are strictly ordered in time to prevent temporal leakage:

```text
DATASET TIMELINE (Jan 2026 -----------------------------------------> June 2026)

|--- TRAIN_1 ---| (100,192 instances)
Feat: Jan 16 - Feb 14  |  Pred: Feb 15 - Mar 16  (Cutoff: Feb 15)

         |--- TRAIN_2 ---| (128,713 instances)
         Feat: Feb 13 - Mar 14  |  Pred: Mar 15 - Apr 13  (Cutoff: Mar 15)

                  |--- VALIDATION ---| (151,248 instances)
                  Feat: Mar 16 - Apr 14  |  Pred: Apr 15 - May 14  (Cutoff: Apr 15)

                           |--- TEST (OOT) ---| (168,375 instances)
                           Feat: Apr 15 - May 14  |  Pred: May 15 - Jun 13  (Cutoff: May 15)
```

## 2. Baseline Model Performance

Before training advanced machine learning models (Block 7), we must establish a naive baseline. 

**Baseline Strategy (Recent Momentum Predictor)**:
The most intuitive SEO heuristic is that whatever direction traffic was moving in the last 15 days, it will continue in the next 30 days. We use the engineered `imp_momentum` feature:
* Predict **Growing**: if `imp_momentum` > 1.10
* Predict **Declining**: if `imp_momentum` < 0.90
* Predict **Stable**: otherwise

**Test Set Evaluation (Out-of-Time Cutoff: May 15, 2026)**
* Total Instances: 168,375
* **Macro F1-Score: 0.4399**

```text
              precision    recall  f1-score   support

   declining       0.70      0.61      0.65     97110
     growing       0.35      0.58      0.44     38322
      stable       0.30      0.19      0.23     32943

    accuracy                           0.52    168375
   macro avg       0.45      0.46      0.44    168375
weighted avg       0.54      0.52      0.52    168375

```

**Conclusion**: The Machine Learning models in Block 7 must strictly beat a Macro F1 of **0.4399** on the out-of-time Test set to be considered viable.
