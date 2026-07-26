from feature_importance_tool import FeatureImportanceTool

tool = FeatureImportanceTool()

print(
    tool.get_top_features(
        "Australian Grand Prix",
        "logistic",
        5
    )
)