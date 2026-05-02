# 🟡 Member 3 (Part 2): Attrition Prediction Model
# Build, compare, and evaluate Attrition models
# Models: Logistic Regression, Random Forest, Gradient Boosting
# Output: Evaluation metrics, Top 10 features, Risk scores

from src.config import PROCESSED_DATA_PATH, REPORTS_PATH, MODELS_PATH

# =========================
# 1. Load processed data
# =========================
df = spark.read.csv(
    PROCESSED_DATA_PATH,
    header=True,
    inferSchema=True
)

# Convert Spark → Pandas for sklearn modeling
pdf = df.toPandas()

# =========================
# 2. Prepare features
# =========================
from sklearn.model_selection import train_test_split

X = pdf.drop("Attrition", axis=1)
y = pdf["Attrition"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# =========================
# 3. Handle class imbalance
# =========================
class_weight = "balanced"

# =========================
# 4. Train models
# =========================
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# Logistic Regression
lr = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)
lr.fit(X_train, y_train)

# Random Forest
rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)
rf.fit(X_train, y_train)

# Gradient Boosting
gbt = GradientBoostingClassifier(random_state=42)
gbt.fit(X_train, y_train)

# =========================
# 5. Evaluation
# =========================
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)
import pandas as pd

models = {
    "Logistic Regression": lr,
    "Random Forest": rf,
    "Gradient Boosting": gbt
}

evaluation_results = {}

for name, model in models.items():
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    evaluation_results[name] = {
        "ROC_AUC": roc_auc_score(y_test, probs),
        "Report": classification_report(y_test, preds, output_dict=True),
        "ConfusionMatrix": confusion_matrix(y_test, preds)
    }

    print(f"\n===== {name} =====")
    print(classification_report(y_test, preds))
    print("ROC-AUC:", roc_auc_score(y_test, probs))
    print("Confusion Matrix:\n", confusion_matrix(y_test, preds))

# =========================
# 6. Select best model
# =========================
# (Using Random Forest as best-performing baseline)
best_model = rf

# =========================
# 7. Top 10 important features
# =========================
importances = best_model.feature_importances_

top_features = (
    pd.Series(importances, index=X.columns)
      .sort_values(ascending=False)
      .head(10)
)

print("\nTop 10 Important Features:")
print(top_features)

# =========================
# 8. Risk score per employee
# =========================
pdf["risk_score"] = best_model.predict_proba(X)[:, 1]

# =========================
# 9. Save outputs (executed by owner)
# =========================
pdf["risk_score"].to_csv(
    f"{REPORTS_PATH}/risk_scores.csv",
    index=False
)

top_features.to_csv(
    f"{REPORTS_PATH}/top_10_features.csv"
)

print("\n✅ Attrition model completed.")
print("📁 Outputs: risk_scores.csv, top_10_features.csv")
