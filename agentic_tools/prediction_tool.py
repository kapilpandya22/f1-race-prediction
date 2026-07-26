# agentic_tools/prediction_tool.py

import pandas as pd
from agentic_tools.mapping import get_driver_name
from agentic_tools.path_resolver import get_file_path


class PredictionTool:

    def get_predictions(
        self,
        race_name,
        model="logistic"
    ):

        path = get_file_path(
            race_name=race_name,
            model=model,
            file_type="predictions"
        )

        return pd.read_csv(path)

    def get_top_predictions(
        self,
        race_name,
        model="logistic",
        top_n=10
    ):

        df = self.get_predictions(
            race_name,
            model
        )

        results = (
            df[
                [
                    "driver",
                    "rank",
                    "pred_top3_prob"
                ]
            ]
            .sort_values("rank")
            .head(top_n)
            .to_dict("records")
        )

        for row in results:

            row["driver_code"] = row["driver"]

            row["driver_name"] = (
                get_driver_name(
                    row["driver"]
                )
            )

            del row["driver"]

        return results