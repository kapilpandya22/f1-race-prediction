print("START")
from benchmark_tool import BenchmarkTool

tool = BenchmarkTool()

print("BASE DIR:")
print(tool.BASE_DIR)

print("\nLogistic:")
print(tool.get_model_summary("logistic"))

print("\nRandom Forest:")
print(tool.get_model_summary("random_forest"))

print("\nXGBoost:")
print(tool.get_model_summary("xgboost"))

print("\nBest Model:")
print(tool.get_best_model())