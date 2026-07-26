# agentic_tools/path_resolver.py

from pathlib import Path

BASE_DIR = Path("/Users/paridhishukla/Downloads/f1-ml-project 2/outputs/predictions")


def get_file_path(
    race_name: str,
    model: str = "logistic",
    file_type: str = "predictions"
):
    """
    file_type:
        predictions
        predictions_with_features
        feature_importance
    """

    race_folder = (
        "2026_" +
        race_name.replace(" ", "_")
    )

    return (
        BASE_DIR
        / model
        / race_folder
        / f"{file_type}.csv"
    )