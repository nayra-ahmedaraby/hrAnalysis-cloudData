

DATA_PATH = "/Volumes/workspace/default/project_clouddb/HR-Employee-Attrition.csv"
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
