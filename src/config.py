# Project configuration — paths are Databricks Volume paths.

DATA_PATH               = "/Volumes/workspace/default/project/data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"
PROCESSED_DATA_PATH     = "/Volumes/workspace/default/project/data/processed/employees_clean.csv"
FEATURES_DATA_PATH      = "/Volumes/workspace/default/project/data/processed/employees_features.csv"

FIGURES_PATH            = "/Volumes/workspace/default/project/figures"
REPORTS_PATH            = "/Volumes/workspace/default/project/reports"
MODELS_PATH             = "/Volumes/workspace/default/project/models"
DASHBOARD_PATH          = "/Volumes/workspace/default/project/dashboard"
DOCS_PATH               = "/Volumes/workspace/default/project/docs"

ATTRITION_MODEL_PATH    = f"{MODELS_PATH}/attrition/attrition_model.pkl"
PERFORMANCE_MODEL_PATH  = f"{MODELS_PATH}/performance_regression_model.pkl"
PERFORMANCE_CLF_PATH    = f"{MODELS_PATH}/performance_classification_model.pkl"
CLUSTERING_MODEL_PATH   = f"{MODELS_PATH}/clustering_model.pkl"


# Targets
TARGET_ATTRITION   = "Attrition"
TARGET_PERFORMANCE = "PerformanceRating"

# EmployeeNumber is the join key — DO NOT drop it.
ID_COL = "EmployeeNumber"

# Constant / useless columns to drop (EmployeeNumber kept!)
COLS_TO_DROP = ["EmployeeCount", "Over18", "StandardHours"]

CATEGORICAL_COLS = [
    "BusinessTravel",
    "Department",
    "EducationField",
    "Gender",
    "JobRole",
    "MaritalStatus",
    "OverTime",
]

NUMERICAL_COLS = [
    "Age", "DailyRate", "DistanceFromHome", "Education",
    "EnvironmentSatisfaction", "HourlyRate", "JobInvolvement",
    "JobLevel", "JobSatisfaction", "MonthlyIncome", "MonthlyRate",
    "NumCompaniesWorked", "PercentSalaryHike", "RelationshipSatisfaction",
    "StockOptionLevel", "TotalWorkingYears", "TrainingTimesLastYear",
    "WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager",
]

# Model settings
TEST_SIZE     = 0.2
RANDOM_STATE  = 42
CV_FOLDS      = 5
N_CLUSTERS    = 4
