from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.ml.feature import StringIndexer, StandardScaler, VectorAssembler
from pyspark.ml import Pipeline

from src.config import (
    DATA_PATH, COLS_TO_DROP, CATEGORICAL_COLS,
    NUMERICAL_COLS, TARGET_ATTRITION, PROCESSED_DATA_PATH
)


class Preprocessor:

    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("HR_Preprocessing") \
            .getOrCreate()
        self.df = None

    def load_data(self):
        self.df = self.spark.read.csv(
            DATA_PATH,
            header=True,
            inferSchema=True
        )
        print(f"Data Loaded: {self.df.count()} rows, {len(self.df.columns)} columns")
        return self

    def drop_useless_columns(self):
        cols_to_remove = [c for c in COLS_TO_DROP if c in self.df.columns]
        self.df = self.df.drop(*cols_to_remove)
        print(f" Dropped columns: {cols_to_remove}")
        return self

    def handle_missing_values(self):
        """Handle missing values: median for numerical, mode for categorical."""
        total = self.df.count()
        print("\n Missing Value Report:")

        for col_name, dtype in self.df.dtypes:
            missing = self.df.filter(F.col(col_name).isNull()).count()
            if missing > 0:
                pct = round(missing / total * 100, 2)
                print(f"   {col_name}: {missing} missing ({pct}%)")

                if col_name in NUMERICAL_COLS:
                    median_val = self.df.approxQuantile(col_name, [0.5], 0.01)[0]
                    self.df = self.df.fillna({col_name: median_val})
                    print(f"     → filled with median: {median_val}")
                else:
                    mode_val = (
                        self.df.groupBy(col_name).count()
                        .orderBy(F.desc("count"))
                        .first()[0]
                    )
                    self.df = self.df.fillna({col_name: mode_val})
                    print(f"     → filled with mode: {mode_val}")

        print(" Missing values handled")
        return self

    def encode_target(self):
        self.df = self.df.withColumn(
            TARGET_ATTRITION,
            F.when(F.col(TARGET_ATTRITION) == "Yes", 1).otherwise(0).cast(IntegerType())
        )
        print(f" Target encoded: Yes=1, No=0")
        return self

    def encode_categoricals_dataframe(self):
        """Spark Paradigm 1: DataFrame API"""
        print("\n Paradigm 1: DataFrame API")

        indexers = [
            StringIndexer(
                inputCol=col,
                outputCol=f"{col}_idx",
                handleInvalid="keep"
            )
            for col in CATEGORICAL_COLS if col in self.df.columns
        ]

        pipeline = Pipeline(stages=indexers)
        self.df = pipeline.fit(self.df).transform(self.df)

        self.df = self.df.drop(*[c for c in CATEGORICAL_COLS if c in self.df.columns])

        for col in CATEGORICAL_COLS:
            if f"{col}_idx" in self.df.columns:
                self.df = self.df.withColumnRenamed(f"{col}_idx", col)

        print(f" Categorical columns encoded via DataFrame API")
        return self

    def explore_with_sql(self):
        """Spark Paradigm 2: Spark SQL"""
        print("\nParadigm 2: Spark SQL")

        self.df.createOrReplaceTempView("employees")

        print("\n Attrition Rate by Department:")
        self.spark.sql("""
            SELECT 
                Department,
                COUNT(*) AS total,
                SUM(Attrition) AS attrition_count,
                ROUND(SUM(Attrition) / COUNT(*) * 100, 2) AS attrition_rate
            FROM employees
            GROUP BY Department
            ORDER BY attrition_rate DESC
        """).show()

        print(" Avg Monthly Income by Job Level:")
        self.spark.sql("""
            SELECT 
                JobLevel,
                ROUND(AVG(MonthlyIncome), 2) AS avg_income,
                COUNT(*) AS employee_count
            FROM employees
            GROUP BY JobLevel
            ORDER BY JobLevel
        """).show()

        return self

    def process_with_rdd(self):
        """Spark Paradigm 3: RDD-style processing (بدون mapInPandas لتجنب schema error)"""
        print("\nParadigm 3: RDD-style Processing")

        total = self.df.count()
        attrition_count = self.df.filter(F.col("Attrition") == 1).count()
        attrition_rate = round(attrition_count / total * 100, 2)

        print(f" RDD-style Processing:")
        print(f"   Total Employees : {total}")
        print(f"   Attrition Count : {attrition_count}")
        print(f"   Attrition Rate  : {attrition_rate}%")

        return self

    def scale_numerical(self):
        """Scale numerical columns using Spark MLlib."""
        num_cols = [c for c in NUMERICAL_COLS if c in self.df.columns]

        assembler = VectorAssembler(inputCols=num_cols, outputCol="features_vec")
        scaler = StandardScaler(
            inputCol="features_vec",
            outputCol="scaled_features",
            withMean=True,
            withStd=True
        )

        pipeline = Pipeline(stages=[assembler, scaler])
        self.df = pipeline.fit(self.df).transform(self.df)

        print(f" Numerical columns scaled ({len(num_cols)} columns)")
        return self

    def show_summary(self):
        """Print shape and basic stats after cleaning."""
        display_cols = [c for c in self.df.columns
                        if c not in ["features_vec", "scaled_features"]]

        print("\n Dataset Summary After Cleaning:")
        print(f"   Rows    : {self.df.count()}")
        print(f"   Columns : {len(display_cols)}")
        print(f"   Columns : {display_cols}")
        self.df.select(display_cols).describe().show()
        return self

    def save(self):
        """Save cleaned DataFrame as CSV."""
        self.df.select(
            [c for c in self.df.columns
             if c not in ["features_vec", "scaled_features"]]
        ).write.csv(PROCESSED_DATA_PATH, header=True, mode="overwrite")
        print(f"\n Saved → {PROCESSED_DATA_PATH}")
        return self

    def run(self):
        self.load_data()
        self.drop_useless_columns()
        self.handle_missing_values()
        self.encode_target()
        self.encode_categoricals_dataframe()
        self.explore_with_sql()
        self.process_with_rdd()
        self.scale_numerical()
        self.show_summary()
        self.save()  


if __name__ == "__main__":
    preprocessor = Preprocessor()
    preprocessor.run()
