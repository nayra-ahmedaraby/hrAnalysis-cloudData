# 🟡 Member 3 (Part 1): Feature Engineering Module
# Create polynomial features, interaction features, aggregate statistics, and normalize/scale numeric data
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import TARGET_ATTRITION

CLEAN_PATH    = "/Volumes/workspace/default/project_clouddb/employees_clean.csv"
FEATURES_PATH = "/Volumes/workspace/default/project_clouddb/employees_features.csv"


class FeatureEngineer:
   

    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("HR_FeatureEngineering") \
            .getOrCreate()
        self.df = None

    def load_data(self):
        """Read the cleaned & encoded CSV from Preprocessor output"""
        self.df = self.spark.read.csv(
            CLEAN_PATH,
            header=True,
            inferSchema=True
        )
        print(f" Loaded: {self.df.count()} rows | {len(self.df.columns)} columns")
        return self

    def build_engagement_score(self):
        
        self.df = self.df.withColumn(
            "EngagementScore",
            (
                F.col("JobSatisfaction")        +
                F.col("EnvironmentSatisfaction") +
                F.col("JobInvolvement")          +
                F.col("WorkLifeBalance")
            ) / 4.0
        )
        print(" [1] EngagementScore")
        return self

    def build_tenure_ratio(self):
        """
        TenureRatio = YearsAtCompany / TotalWorkingYears
        Close to 1 = spent most of career here = loyal.
        """
        self.df = self.df.withColumn(
            "TenureRatio",
            F.when(
                F.col("TotalWorkingYears") > 0,
                F.col("YearsAtCompany") / F.col("TotalWorkingYears")
            ).otherwise(0.0)
        )
        print(" [2] TenureRatio")
        return self

    def build_promotion_velocity(self):
        """
        PromotionVelocity = JobLevel / YearsAtCompany
        Low value + long tenure = stagnating = flight risk.
        """
        self.df = self.df.withColumn(
            "PromotionVelocity",
            F.when(
                F.col("YearsAtCompany") > 0,
                F.col("JobLevel") / F.col("YearsAtCompany")
            ).otherwise(F.col("JobLevel").cast("double"))
        )
        print(" [3] PromotionVelocity")
        return self

    def build_income_deviation(self):
        """
        IncomeDeviation = MonthlyIncome - avg(MonthlyIncome) per JobLevel
        Negative = underpaid vs peers = higher attrition risk.
        """
        avg_by_level = self.df.groupBy("JobLevel").agg(
            F.avg("MonthlyIncome").alias("_peer_avg")
        )
        self.df = self.df.join(avg_by_level, on="JobLevel", how="left")
        self.df = self.df.withColumn(
            "IncomeDeviation",
            F.col("MonthlyIncome") - F.col("_peer_avg")
        ).drop("_peer_avg")
        print(" [4] IncomeDeviation")
        return self

    def build_loyalty_index(self):
        """
        LoyaltyIndex = YearsAtCompany / (NumCompaniesWorked + 1)
        High = long stay, few past employers = loyal employee.
        """
        self.df = self.df.withColumn(
            "LoyaltyIndex",
            F.col("YearsAtCompany") / (F.col("NumCompaniesWorked") + 1)
        )
        print(" [5] LoyaltyIndex")
        return self

    def summarize(self):
        """Stats and Attrition correlation for the 5 new features."""
        features = [
            "EngagementScore", "TenureRatio", "PromotionVelocity",
            "IncomeDeviation", "LoyaltyIndex",
        ]
        print("\n Feature Stats:")
        self.df.select(features).describe().show()

        print(" Correlation with Attrition:")
        for feat in features:
            corr = self.df.stat.corr(feat, TARGET_ATTRITION)
            tag  = "High risk" if corr > 0 else " Low risk"
            print(f"   {feat:<22}  corr = {corr:+.4f}  ({tag})")
        return self

    def save(self):
        self.df.write.csv(FEATURES_PATH, header=True, mode="overwrite")
        print(f"\n Saved → {FEATURES_PATH}")
        return self

    def run(self):
        print("=" * 50)
        print("  Member 1 — Part 2: Feature Engineering")
        print("=" * 50)
        self.load_data()
        self.build_engagement_score()
        self.build_tenure_ratio()
        self.build_promotion_velocity()
        self.build_income_deviation()
        self.build_loyalty_index()
        self.summarize()
        self.save()
        print("\n employees_features.csv ready")


if __name__ == "__main__":
    engineer = FeatureEngineer()
    engineer.run()
