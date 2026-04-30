from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.ml.feature import StringIndexer, OneHotEncoder, StandardScaler, VectorAssembler
from pyspark.ml import Pipeline
from config import (
    DATA_PATH, COLS_TO_DROP, CATEGORICAL_COLS,
    NUMERICAL_COLS, TARGET_ATTRITION
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

        # Drop original categorical columns
        self.df = self.df.drop(*[c for c in CATEGORICAL_COLS if c in self.df.columns])

        # Rename indexed columns
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
        """Spark Paradigm 3: mapInPandas (RDD-style processing)"""
        print("\nParadigm 3: mapInPandas (RDD-style processing)")

        def count_attrition(iterator):
            for pdf in iterator:
                total = len(pdf)
                attrition_count = pdf["Attrition"].sum()
                attrition_rate = round(attrition_count / total * 100, 2)
                pdf["attrition_rate"] = attrition_rate
                yield pdf

        result = self.df.mapInPandas(count_attrition, schema=self.df.schema)

        total = result.count()
        attrition_count = result.filter(F.col("Attrition") == 1).count()
        attrition_rate = round(attrition_count / total * 100, 2)

        print(f" mapInPandas Processing:")
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

    def save(self, output_path="/Volumes/workspace/default/project_clouddb/employees_clean.csv"):
        """Save cleaned DataFrame as CSV."""
        self.df.select(
            [c for c in self.df.columns
             if c not in ["features_vec", "scaled_features"]]
        ).write.csv(output_path, header=True, mode="overwrite")
        print(f"\n Saved → {output_path}")
        return self

    def run(self):
        self.load_data()
        self.drop_useless_columns()
        self.encode_target()
        self.encode_categoricals_dataframe()
        self.explore_with_sql()
        self.process_with_rdd()
        self.scale_numerical()
        self.save()


if __name__ == "__main__":
    preprocessor = Preprocessor()
    preprocessor.run()
