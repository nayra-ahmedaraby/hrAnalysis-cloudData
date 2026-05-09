# Member 4 (Part 1) — Performance Prediction
# - Composite Performance Score (PerfScore)
# - Regression on PerfScore (Linear / RF / GBT) → RMSE
# - Classification on PerformanceRating (LR / RF / GBT) → F1
# - Performance drivers (top features)

import os
import joblib
import numpy as np
import pandas as pd

from pyspark.sql import SparkSession

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
)
from sklearn.metrics import mean_squared_error, f1_score
from sklearn.model_selection import train_test_split

from src.config import (
    FEATURES_DATA_PATH,
    PROCESSED_DATA_PATH,
    REPORTS_PATH,
    MODELS_PATH,
    PERFORMANCE_MODEL_PATH,
    PERFORMANCE_CLF_PATH,
    ID_COL,
    RANDOM_STATE,
    TEST_SIZE,
)


class PerformanceModel:

    def __init__(self, spark=None):
        self.spark = spark or (
            SparkSession.builder
            .appName("PerformanceModel")
            .master("local[*]")
            .getOrCreate()
        )
        self.spark.sparkContext.setLogLevel("ERROR")

        self.pdf = None
        self.regression_results = {}
        self.classification_results = {}
        self.best_reg_model = None
        self.best_clf_model = None
        self._reg_feature_cols = []

    # ==========================================================
    def load_data(self):
        # Prefer features file (has EngagementScore etc.). Fall back if missing.
        try:
            df = self.spark.read.csv(FEATURES_DATA_PATH, header=True, inferSchema=True)
        except Exception:
            df = self.spark.read.csv(PROCESSED_DATA_PATH, header=True, inferSchema=True)

        self.pdf = df.toPandas()
        print(f"[load_data] {len(self.pdf)} rows")
        return self

    # ==========================================================
    def build_composite_score(self):
        WEIGHTS = {
            "EngagementScore":   0.30,
            "PerformanceRating": 0.30,
            "LoyaltyIndex":      0.20,
            "TenureRatio":       0.10,
            "PromotionVelocity": 0.10,
        }

        score = pd.Series(0.0, index=self.pdf.index)

        for col, w in WEIGHTS.items():
            if col not in self.pdf.columns:
                continue
            s = self.pdf[col].astype(float).fillna(0)
            if col in ("EngagementScore", "PerformanceRating"):
                s_norm = (s - 1) / 3
            else:
                lo, hi = s.min(), s.max()
                s_norm = (s - lo) / (hi - lo) if hi > lo else 0
            score += w * s_norm

        self.pdf["PerfScore"] = score.round(4)
        print("[PerfScore] built")
        return self

    # ==========================================================
    def _prepare_features(self, target_col):
        EXCLUDE = {target_col, ID_COL, "Attrition", "risk_score", "PerfScore", "Cluster"}
        num_cols = self.pdf.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [c for c in num_cols if c not in EXCLUDE]

        working = self.pdf[feature_cols + [target_col]].dropna()
        X = working[feature_cols]
        y = working[target_col]
        return X, y, feature_cols

    # ==========================================================
    def train_regression(self):
        X, y, feat_cols = self._prepare_features("PerfScore")
        self._reg_feature_cols = feat_cols

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )

        models = {
            "Linear Regression":   LinearRegression(),
            "Random Forest":       RandomForestRegressor(n_estimators=200, max_depth=6, random_state=RANDOM_STATE),
            "Gradient Boosting":   GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=RANDOM_STATE),
        }

        fitted = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            self.regression_results[name] = round(float(rmse), 4)
            fitted[name] = model
            print(f"  {name} → RMSE = {rmse:.4f}")

        best_name = min(self.regression_results, key=self.regression_results.get)
        self.best_reg_model = fitted[best_name]

        os.makedirs(MODELS_PATH, exist_ok=True)
        joblib.dump(self.best_reg_model, PERFORMANCE_MODEL_PATH)
        print(f"[SAVED] regression → {PERFORMANCE_MODEL_PATH}")

        # Persist comparison
        pd.DataFrame(
            [{"Model": k, "RMSE": v} for k, v in self.regression_results.items()]
        ).sort_values("RMSE").to_csv(f"{REPORTS_PATH}/performance_regression_comparison.csv", index=False)
        return self

    # ==========================================================
    def train_classification(self):
        X, y, _ = self._prepare_features("PerformanceRating")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
        )

        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
            "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=6, random_state=RANDOM_STATE, class_weight="balanced"),
            "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=RANDOM_STATE),
        }

        fitted = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            f1 = f1_score(y_test, preds, average="weighted")
            self.classification_results[name] = round(float(f1), 4)
            fitted[name] = model
            print(f"  {name} → F1 = {f1:.4f}")

        best_name = max(self.classification_results, key=self.classification_results.get)
        self.best_clf_model = fitted[best_name]

        joblib.dump(self.best_clf_model, PERFORMANCE_CLF_PATH)
        print(f"[SAVED] classifier → {PERFORMANCE_CLF_PATH}")

        pd.DataFrame(
            [{"Model": k, "F1": v} for k, v in self.classification_results.items()]
        ).sort_values("F1", ascending=False).to_csv(
            f"{REPORTS_PATH}/performance_classification_comparison.csv", index=False
        )
        return self

    # ==========================================================
    def extract_performance_drivers(self):
        m = self.best_reg_model
        if hasattr(m, "feature_importances_"):
            imp = m.feature_importances_
        elif hasattr(m, "coef_"):
            imp = np.abs(m.coef_)
        else:
            return self

        top = (pd.Series(imp, index=self._reg_feature_cols)
               .sort_values(ascending=False)
               .head(15))
        top.to_csv(f"{REPORTS_PATH}/performance_top_features.csv", header=["importance"])
        print("\nTop performance drivers:\n", top)

        # Save PerfScore keyed by EmployeeNumber for downstream consumers
        if ID_COL in self.pdf.columns:
            self.pdf[[ID_COL, "PerfScore"]].to_csv(
                f"{REPORTS_PATH}/performance_scores.csv", index=False
            )
            print(f"[SAVED] performance scores → {REPORTS_PATH}/performance_scores.csv")
        return self

    # ==========================================================
    def run(self):
        (self
            .load_data()
            .build_composite_score()
            .train_regression()
            .train_classification()
            .extract_performance_drivers())
        print("[PerformanceModel] Done.")
        return self


if __name__ == "__main__":
    PerformanceModel().run()
