# Entry point — runs the full HR Analytics pipeline.
#
#   python main.py
#
# Stages:
#   1. Preprocessing       (Member 1)
#   2. Feature engineering (Member 1)
#   3. EDA                 (Member 2)
#   4. Attrition model     (Member 3)
#   5. Performance model   (Member 4)
#   6. Clustering          (Member 4)
#   7. Insights            (Member 5)
#   8. PDF report          (Member 5)


def run_pipeline():

    print("\n=== [1/8] Preprocessing ===")
    from src.preprocessing import Preprocessor
    Preprocessor().run()

    print("\n=== [2/8] Feature engineering ===")
    from src.features import FeatureEngineer
    FeatureEngineer().run()

    print("\n=== [3/8] EDA ===")
    from src.eda import EDAAnalyzer
    EDAAnalyzer().run()

    print("\n=== [4/8] Attrition model ===")
    from src.attrition_model import AttritionModel
    AttritionModel().run()

    print("\n=== [5/8] Performance model ===")
    from src.performance_model import PerformanceModel
    PerformanceModel().run()

    print("\n=== [6/8] Clustering ===")
    from src.clustering import EmployeeClustering
    EmployeeClustering().run()

    print("\n=== [7/8] Insights ===")
    from src.insights import InsightsGenerator
    InsightsGenerator().run()

    print("\n=== [8/8] PDF report ===")
    from src.report_generator import ReportGenerator
    ReportGenerator().build()


if __name__ == "__main__":
    run_pipeline()
