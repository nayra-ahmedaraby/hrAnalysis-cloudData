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


def run_pipeline():

    print("\n=== [1/7] Preprocessing ===")
    from src.preprocessing import Preprocessor
    Preprocessor().run()

    print("\n=== [2/7] Feature engineering ===")
    from src.features import FeatureEngineer
    FeatureEngineer().run()

    print("\n=== [3/7] EDA ===")
    from src.eda import EDAAnalyzer
    EDAAnalyzer().run()

    print("\n=== [4/7] Attrition model ===")
    from src.attrition_model import AttritionModel
    AttritionModel().run()

    print("\n=== [5/7] Performance model ===")
    from src.performance_model import PerformanceModel
    PerformanceModel().run()

    print("\n=== [6/7] Clustering ===")
    from src.clustering import EmployeeClustering
    EmployeeClustering().run()

    print("\n=== [7/7] Insights ===")
    from src.insights import InsightsGenerator
    InsightsGenerator().run()


if __name__ == "__main__":
    run_pipeline()
