# HR Analytics Project - Team Collaboration


this is the tree of the project:

```hr-analytics/
│
├── README.md
├── requirements.txt
├── .gitignore
├── main.py                          # entry point to run the entire pipeline
│
├── data/
│   ├── raw/
│   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
│   └── processed/                   # output preprocessed data 
│
├── src/
│   ├── __init__.py
│   ├── config.py                    # paths, constants, column names
│   │
│   ├── preprocessing.py             # 🔵 Member 1: class Preprocessor
│   ├── eda.py                       # 🟢 Member 2: class EDAAnalyzer
│   ├── features.py                  # 🟡 Member 3: class FeatureEngineer
│   ├── attrition_model.py           # 🟡 Member 3: class AttritionModel
│   ├── performance_model.py         # 🟠 Member 4: class PerformanceModel
│   ├── clustering.py                # 🟠 Member 4: class EmployeeClustering
│   └── insights.py                  # 🔴 Member 5: class InsightsGenerator
│
├── outputs/
│   ├── figures/                     # EDA plots
│   ├── models/                      # saved models
│   └── reports/                     # CSVs for high-risk employees, personas
│
├── dashboard/
│   └── HR_Analytics.pbix            # Power BI
│
└── docs/
    ├── final_report.pdf
    └── presentation.pptx
```
