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
│   ├── preprocessing.py             
│   ├── eda.py                       
│   ├── features.py                  
│   ├── attrition_model.py         
│   ├── performance_model.py        
│   ├── clustering.py                
│   └── insights.py                  
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
