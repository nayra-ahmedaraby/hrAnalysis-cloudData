# 🟠 Member 4 (Part 2): Employee Clustering Module
# Perform K-means clustering to segment employees into personas and analyze cluster characteristics

# ═══════════════════════════════════════════════════════════════
# ADDED: Missing imports for clustering to match project requirements
# ═══════════════════════════════════════════════════════════════
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from pyspark.sql import SparkSession
# ═══════════════════════════════════════════════════════════════
from src.config import (
    PROCESSED_DATA_PATH, FEATURES_DATA_PATH, REPORTS_PATH, MODELS_PATH, ID_COL
)

# ═══════════════════════════════════════════════════════════════
# Class — EmployeeClustering
# ═══════════════════════════════════════════════════════════════

class EmployeeClustering:

    def __init__(self, spark=None):

        self.spark = spark or (
            SparkSession.builder
            .appName("EmployeeClustering")
            .master("local[*]")
            .getOrCreate()
        )

        self.spark.sparkContext.setLogLevel("ERROR")

        self.pdf = None
        self.cluster_df = None

        self.scaler = StandardScaler()

        self.best_k = None
        self.best_score = None

    # ==========================================================
    # Load Data
    # ==========================================================
    def load_data(self, path=None):
        # Prefer features file (engagement, tenure, etc.); fall back to processed.
        path = path or FEATURES_DATA_PATH
        try:
            df = self.spark.read.csv(path, header=True, inferSchema=True)
        except Exception:
            df = self.spark.read.csv(PROCESSED_DATA_PATH, header=True, inferSchema=True)

        self.pdf = df.toPandas()

        # Merge in attrition risk_score if available (improves clustering separation)
        try:
            risks = pd.read_csv(f"{REPORTS_PATH}/risk_scores.csv")
            if ID_COL in self.pdf.columns and ID_COL in risks.columns:
                self.pdf = self.pdf.merge(
                    risks[[ID_COL, "risk_score"]], on=ID_COL, how="left"
                )
        except Exception:
            pass

        print(f"[load_data] {len(self.pdf)} rows")

        return self

    # ==========================================================
    # Prepare Features
    # ==========================================================
    def prepare_features(self):

        features = [
            "EngagementScore",
            "TenureRatio",
            "PromotionVelocity",
            "IncomeDeviation",
            "LoyaltyIndex",
        ]

        if "risk_score" in self.pdf.columns:
            features.append("risk_score")

        available = [
            f for f in features
            if f in self.pdf.columns
        ]

        X = self.pdf[available].fillna(0)

        self.feature_names = available

        self.X_scaled = self.scaler.fit_transform(X)

        return self

    # ==========================================================
    # Find Optimal K
    # ==========================================================
    def find_optimal_k(self, max_k=10):

        inertias = []
        silhouettes = []

        k_values = range(2, max_k + 1)

        for k in k_values:

            kmeans = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            labels = kmeans.fit_predict(self.X_scaled)

            inertia = kmeans.inertia_

            sil = silhouette_score(
                self.X_scaled,
                labels
            )

            inertias.append(inertia)
            silhouettes.append(sil)

            print(f"K={k} | Silhouette={sil:.4f}")

        best_idx = np.argmax(silhouettes)

        self.best_k = list(k_values)[best_idx]

        self.best_score = silhouettes[best_idx]

        return self

    # ==========================================================
    # Apply Clustering
    # ==========================================================
    def apply_clustering(self):

        kmeans = KMeans(
            n_clusters=self.best_k,
            random_state=42,
            n_init=10
        )

        clusters = kmeans.fit_predict(self.X_scaled)

        self.pdf["Cluster"] = clusters

        self.cluster_df = self.pdf

        # ═══════════════════════════════════════════════════════════════
        # ADDED: Save clustering model to match project requirements
        # ═══════════════════════════════════════════════════════════════
        joblib.dump(kmeans, f"{MODELS_PATH}/clustering_model.pkl")
        print(f"[SAVED] Clustering model: {MODELS_PATH}/clustering_model.pkl")
        # ═══════════════════════════════════════════════════════════════

        return self

    # ==========================================================
    # Profile Clusters
    # ==========================================================
    def profile_clusters(self):

        profiles = (
            self.cluster_df
            .groupby("Cluster")[self.feature_names]
            .mean()
            .round(3)
        )

        personas = []

        for cluster_id, row in profiles.iterrows():

            risk = row.get("risk_score", 0)
            engagement = row.get("EngagementScore", 0)

            if risk > 0.6:
                persona = "High Attrition Risk"

            elif engagement > 3:
                persona = "Highly Engaged"

            elif row.get("LoyaltyIndex", 0) > 3:
                persona = "Loyal Long-Term Employees"

            else:
                persona = "Average Workforce"

            personas.append(persona)

        profiles["Persona"] = personas

        self.personas_df = profiles.reset_index()

        print(self.personas_df)

        return self

    # ==========================================================
    # Save Outputs
    # ==========================================================
    def save_outputs(self):

        self.cluster_df.to_csv(
            os.path.join(REPORTS_PATH, "employees_with_clusters.csv"),
            index=False,
        )

        self.personas_df.to_csv(
            os.path.join(REPORTS_PATH, "personas.csv"),
            index=False,
        )

        # Persist silhouette score & chosen K
        with open(os.path.join(REPORTS_PATH, "clustering_summary.txt"), "w", encoding="utf-8") as f:
            f.write(f"best_k={self.best_k}\nsilhouette_score={self.best_score:.4f}\n")

        print(f" Outputs saved (best_k={self.best_k}, silhouette={self.best_score:.4f})")

        return self

    # ==========================================================
    # Run
    # ==========================================================
    def run(self):

        (
            self.load_data()
                .prepare_features()
                .find_optimal_k()
                .apply_clustering()
                .profile_clusters()
                .save_outputs()
        )

        print(" EmployeeClustering completed")

        return self