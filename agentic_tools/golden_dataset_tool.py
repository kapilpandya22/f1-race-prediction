# agentic_tools/golden_dataset_tool.py

import pandas as pd
from pathlib import Path
from agentic_tools.mapping import get_driver_name

class GoldenDatasetTool:

    BASE_DIR = (
    Path(__file__).resolve().parent.parent
    / "data/golden"
    )

    def get_race_results(
        self,
        race_name
    ):

        race_file = (
            race_name
            .replace(" ", "_")
        )

        path = (
            self.BASE_DIR
            / f"2026_{race_file}_R.csv"
        )

        return pd.read_csv(path)

    def get_podium(
        self,
        race_name
    ):

        df = self.get_race_results(
            race_name
        )

        podium = (
            df[df["podium"] == 1]
            .sort_values("position")
        )

        return [
        {
            "position": int(row["position"]),
            "driver_code": row["driver"],
            "driver_name": get_driver_name(
                row["driver"]
            ),
            "team": row["team"]
        }
        for _, row in podium.iterrows()
        ]

    def get_winner(
        self,
        race_name
    ):

        df = self.get_race_results(
            race_name
        )

        winner = df[
            df["winner"] == 1
        ]

        if winner.empty:
            return None

        return winner.iloc[0].to_dict()

    def get_driver_result(
        self,
        race_name,
        driver
    ):

        df = self.get_race_results(
            race_name
        )

        row = df[
            df["driver"] == driver
        ]

        if row.empty:
            return None

        return row.iloc[0].to_dict()