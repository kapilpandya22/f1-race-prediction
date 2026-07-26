# agentic_tools/test_prediction_tool.py

from prediction_tool import PredictionTool

tool = PredictionTool()

top3 = tool.get_top_predictions(
    race_name="Australian Grand Prix",
    model="logistic",
    top_n=3
)

print(top3)