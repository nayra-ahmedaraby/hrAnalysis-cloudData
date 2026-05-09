import os
import joblib
import numpy as np
import pandas as pd

from pyspark.sql import SparkSession

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix,
)

from src.config import (
    FEATURES_DATA_PATH,
    PROCESSED_DATA_PATH,
    REPORTS_PATH,
    ATTRITION_MODEL_PATH,
    ID_COL,
    TARGET_ATTRITION,
    TEST_SIZE,
    RANDOM_STATE,
    CV_FOLDS,
)


class AttritionModel:

    def __init__(self, spark=None):
        self.spark = spark or (
            SparkSession.builder.appName("AttritionModel").getOrCreate()
        )

        self.pdf = None
        self.X = None
        self.y = None
        self.feature_cols = None
        self.results = {}
        self.best_model = None
        self.best_name = None

    def load_data(self):
        try:
            df = self.spark.read.csv(FEATURES_DATA_PATH, header=True, inferSchema=True)
        except Exception:
            df = self.spark.read.csv(PROCESSED_DATA_PATH, header=True, inferSchema=True)

        self.pdf = df.toPandas()
        print(f"[load] {len(self.pdf)} rows")
        return self

    def prepare_features(self):
        exclude = {TARGET_ATTRITION, ID_COL, "PerfScore", "Cluster", "risk_score"}
        num_cols = self.pdf.select_dtypes(include=[np.number]).columns.tolist()
        self.feature_cols = [c for c in num_cols if c not in exclude]

        self.X = self.pdf[self.feature_cols].fillna(0)
        self.y = self.pdf[TARGET_ATTRITION].astype(int)
        print(f"[prepare] {len(self.feature_cols)} features | classes = {self.y.value_counts().to_dict()}")
        return self

    def train_models(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y,
            test_size=TEST_SIZE,
            stratify=self.y,
            random_state=RANDOM_STATE,
        )

        models = {
            "Logistic Regression": LogisticRegression(
                max_iter=1000, class_weight="balanced"
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=200, random_state=RANDOM_STATE, class_weight="balanced"
            ),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=200, random_state=RANDOM_STATE
            ),
        }

        for name, model in models.items():
            print(f"\n[CV] {name}")
            cv_auc = cross_val_score(
                model, X_train, y_train, cv=CV_FOLDS, scoring="roc_auc", n_jobs=-1
            ).mean()

            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]

            self.results[name] = {
                "cv_roc_auc": round(float(cv_auc), 4),
                "f1":         round(f1_score(y_test, preds), 4),
                "precision":  round(precision_score(y_test, preds), 4),
                "recall":     round(recall_score(y_test, preds), 4),
                "roc_auc":    round(roc_auc_score(y_test, probs), 4),
                "confusion":  confusion_matrix(y_test, preds).tolist(),
                "_model":     model,
            }
            print(f"  CV ROC-AUC={cv_auc:.4f}  test ROC-AUC={self.results[name]['roc_auc']}")

        self.best_name = max(self.results, key=lambda k: self.results[k]["roc_auc"])
        self.best_model = self.results[self.best_name]["_model"]
        print(f"\n[best] {self.best_name}")
        return self

    def save_comparison(self):
        os.makedirs(REPORTS_PATH, exist_ok=True)
        rows = [{
            "Model":      name,
            "CV_ROC_AUC": r["cv_roc_auc"],
            "ROC_AUC":    r["roc_auc"],
            "F1":         r["f1"],
            "Precision":  r["precision"],
            "Recall":     r["recall"],
        } for name, r in self.results.items()]

        cmp = pd.DataFrame(rows).sort_values("ROC_AUC", ascending=False)
        cmp.to_csv(f"{REPORTS_PATH}/attrition_models_comparison.csv", index=False)

        with open(f"{REPORTS_PATH}/attrition_models_comparison.md", "w", encoding="utf-8") as f:
            f.write("# Attrition Models Comparison\n\n")
            f.write(cmp.to_markdown(index=False))
            f.write(f"\n\n**Best model:** {self.best_name}\n")

        os.makedirs(os.path.dirname(ATTRITION_MODEL_PATH), exist_ok=True)
        joblib.dump(self.best_model, ATTRITION_MODEL_PATH)
        print(f"[saved] {ATTRITION_MODEL_PATH}")
        return self

    def top_features(self):
        m = self.best_model
        if hasattr(m, "feature_importances_"):
            imp = m.feature_importances_
        elif hasattr(m, "coef_"):
            imp = np.abs(m.coef_[0])
        else:
            return self

        top = (pd.Series(imp, index=self.feature_cols)
               .sort_values(ascending=False)
               .head(10))
        top = top.round(4)
        top.to_csv(f"{REPORTS_PATH}/top_10_features.csv",
                   header=["importance"], index_label="feature")
        print("\nTop 10 features:\n", top)
        return self

    def risk_scores(self):
        probs = self.best_model.predict_proba(self.X)[:, 1]

        out = pd.DataFrame({
            ID_COL: self.pdf[ID_COL] if ID_COL in self.pdf.columns
                    else np.arange(1, len(self.pdf) + 1),
            "risk_score": np.round(probs, 4),
        })
        out["risk_band"] = pd.cut(
            out["risk_score"],
            bins=[-0.01, 0.30, 0.60, 1.01],
            labels=["Low", "Medium", "High"],
        )
        out.to_csv(f"{REPORTS_PATH}/risk_scores.csv", index=False)
        print(f"[saved] {REPORTS_PATH}/risk_scores.csv")
        return self

    def run(self):
        (self
            .load_data()
            .prepare_features()
            .train_models()
            .save_comparison()
            .top_features()
            .risk_scores())
        print("\n[AttritionModel] Done.")
        return self


if __name__ == "__main__":
    AttritionModel().run()
