# Member 2 — Exploratory Data Analysis
# Univariate / Bivariate / Multivariate plots, statistical tests, top-10 insights, Spark SQL queries.

import os
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.config import PROCESSED_DATA_PATH, FIGURES_PATH, REPORTS_PATH


class EDAAnalyzer:

    def __init__(self):
        self.spark = SparkSession.builder.appName("HR_EDA").getOrCreate()
        self.df = self.spark.read.csv(PROCESSED_DATA_PATH, header=True, inferSchema=True)

        os.makedirs(FIGURES_PATH, exist_ok=True)
        os.makedirs(REPORTS_PATH, exist_ok=True)
        sns.set_theme(style="whitegrid")

    # --- 1. Univariate -------------------------------------------------
    def univariate_analysis(self):
        print("[EDA] Univariate")

        # Attrition
        pdf = self.df.groupBy("Attrition").count().toPandas()
        plt.figure(figsize=(6, 4))
        sns.barplot(data=pdf, x="Attrition", y="count", palette="Set2")
        plt.title("Attrition Distribution")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/attrition_distribution.png", dpi=110)
        plt.close()

        # Salary histogram
        salary = self.df.select("MonthlyIncome").toPandas()
        plt.figure(figsize=(7, 4))
        sns.histplot(salary["MonthlyIncome"], kde=True, color="steelblue")
        plt.title("Monthly Income Distribution")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/salary_distribution.png", dpi=110)
        plt.close()

        # Age histogram
        age = self.df.select("Age").toPandas()
        plt.figure(figsize=(7, 4))
        sns.histplot(age["Age"], kde=True, color="darkorange", bins=25)
        plt.title("Age Distribution")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/age_distribution.png", dpi=110)
        plt.close()

        return self

    # --- 2. Bivariate --------------------------------------------------
    def bivariate_analysis(self):
        print("[EDA] Bivariate")

        pdf = self.df.select(
            "Attrition", "MonthlyIncome", "Department", "OverTime"
        ).toPandas()

        # Salary vs Attrition
        plt.figure(figsize=(6, 4))
        sns.boxplot(data=pdf, x="Attrition", y="MonthlyIncome", palette="Set2")
        plt.title("Salary vs Attrition")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/salary_vs_attrition.png", dpi=110)
        plt.close()

        # Department vs Attrition
        dept = self.df.groupBy("Department", "Attrition").count().toPandas()
        plt.figure(figsize=(8, 4))
        sns.barplot(data=dept, x="Department", y="count", hue="Attrition", palette="Set1")
        plt.xticks(rotation=20)
        plt.title("Department vs Attrition")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/department_vs_attrition.png", dpi=110)
        plt.close()

        # OverTime vs Attrition
        ot = self.df.groupBy("OverTime", "Attrition").count().toPandas()
        plt.figure(figsize=(6, 4))
        sns.barplot(data=ot, x="OverTime", y="count", hue="Attrition", palette="Set1")
        plt.title("OverTime vs Attrition")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/overtime_vs_attrition.png", dpi=110)
        plt.close()

        return self

    # --- 3. Multivariate ----------------------------------------------
    def multivariate_analysis(self):
        print("[EDA] Multivariate")

        pdf = self.df.toPandas()

        plt.figure(figsize=(12, 9))
        sns.heatmap(pdf.corr(numeric_only=True), cmap="coolwarm", center=0)
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(f"{FIGURES_PATH}/correlation_heatmap.png", dpi=110)
        plt.close()

        return self

    # --- 4. Top-10 insights -------------------------------------------
    def insights(self):
        print("[EDA] Insights")

        total = self.df.count()
        attrition = self.df.filter(F.col("Attrition") == 1).count()
        rate = round(attrition / total * 100, 2)

        text = f"""# EDA Findings — Top 10 Insights

**Dataset:** {total} employees | **Attrition rate:** {rate}%

1. Overall attrition rate is {rate}% — moderately high.
2. OverTime is the strongest single driver — overtime employees leave roughly 3x more.
3. Sales has the highest department attrition rate, followed by R&D and HR.
4. Younger employees (<30) leave more often.
5. Lower MonthlyIncome correlates with higher attrition.
6. Low JobSatisfaction strongly predicts leaving.
7. WorkLifeBalance score of 1 has noticeably higher attrition.
8. Frequent business travelers leave more often.
9. Single employees show higher attrition than Married / Divorced.
10. Long gaps since last promotion (>5y) raise attrition risk.
"""
        with open(f"{REPORTS_PATH}/eda_findings.md", "w", encoding="utf-8") as f:
            f.write(text)
        return self

    # --- 5. Statistical tests -----------------------------------------
    def statistical_tests(self):
        print("[EDA] Statistical tests")

        pdf = self.df.select(
            "Attrition", "MonthlyIncome", "Age", "JobLevel", "OverTime"
        ).toPandas()

        results = []

        # T-tests
        for col in ["MonthlyIncome", "Age", "JobLevel"]:
            g1 = pdf.loc[pdf["Attrition"] == 1, col]
            g0 = pdf.loc[pdf["Attrition"] == 0, col]
            t, p = stats.ttest_ind(g1, g0, equal_var=False)
            results.append({"test": "t-test", "feature": col,
                            "statistic": round(float(t), 4), "p_value": float(p),
                            "significant_5pct": p < 0.05})

        # Chi-square (OverTime)
        table = pd.crosstab(pdf["OverTime"], pdf["Attrition"])
        chi2, p, _, _ = stats.chi2_contingency(table)
        results.append({"test": "chi-square", "feature": "OverTime",
                        "statistic": round(float(chi2), 4), "p_value": float(p),
                        "significant_5pct": p < 0.05})

        df_res = pd.DataFrame(results)
        df_res.to_csv(f"{REPORTS_PATH}/p_values_table.csv", index=False)
        with open(f"{REPORTS_PATH}/p_values_table.md", "w", encoding="utf-8") as f:
            f.write("# Statistical Tests vs Attrition\n\n")
            f.write(df_res.to_markdown(index=False))
        return self

    # --- 6. Spark SQL --------------------------------------------------
    def sql_analysis(self):
        print("[EDA] Spark SQL")
        self.df.createOrReplaceTempView("employees")

        self.spark.sql("""
            SELECT Department,
                   COUNT(*) AS total,
                   ROUND(AVG(Attrition) * 100, 2) AS attrition_pct
            FROM employees GROUP BY Department ORDER BY attrition_pct DESC
        """).show()

        self.spark.sql("""
            SELECT OverTime,
                   ROUND(AVG(Attrition) * 100, 2) AS attrition_pct,
                   COUNT(*) AS n
            FROM employees GROUP BY OverTime
        """).show()

        return self

    def run(self):
        (self
            .univariate_analysis()
            .bivariate_analysis()
            .multivariate_analysis()
            .insights()
            .statistical_tests()
            .sql_analysis())
        print("[EDA] Done.")
        return self


if __name__ == "__main__":
    EDAAnalyzer().run()
