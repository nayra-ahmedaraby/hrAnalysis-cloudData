

DATA_PATH = "/Volumes/workspace/default/project/data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"

PROCESSED_DATA_PATH = "/Volumes/workspace/default/project/data/processed/hr_processed.csv"
FIGURES_PATH = "/Volumes/workspace/default/project/figures"
REPORTS_PATH = "/Volumes/workspace/default/project/reports"
MODELS_PATH = "/Volumes/workspace/default/project/models"
ATTRITION_MODEL_PATH = f"{MODELS_PATH}/attrition_model.pkl"
PERFORMANCE_MODEL_PATH = f"{MODELS_PATH}/performance_model.pkl"
CLUSTERING_MODEL_PATH = f"{MODELS_PATH}/clustering_model.pkl"

# Target Columns

TARGET_ATTRITION = "Attrition"
TARGET_PERFORMANCE = "PerformanceRating"


# Columns to Drop (useless or single value)

COLS_TO_DROP = ["EmployeeCount", "Over18", "StandardHours", "EmployeeNumber"]


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

# Model Settings

TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5
N_CLUSTERS = 4
