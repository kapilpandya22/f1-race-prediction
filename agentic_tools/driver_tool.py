import pandas as pd

from agentic_tools.path_resolver import get_file_path
from agentic_tools.mapping import DRIVER_MAP


class DriverTool:

    def get_driver(
        self,
        race_name,
        driver,
        model="logistic"
    ):

        path = get_file_path(
            race_name=race_name,
            model=model,
            file_type="predictions_with_features"
        )

        df = pd.read_csv(path)

        row = df[df["driver"] == driver]

        if row.empty:
            return None

        result = row.iloc[0].to_dict()

        cleaned = {}

        for key, value in result.items():

            if pd.isna(value):
                cleaned[key] = None
            else:
                cleaned[key] = value

        cleaned["driver_name"] = DRIVER_MAP.get(
            cleaned["driver"],
            cleaned["driver"]
        )

        return cleaned

    def get_driver_summary(
        self,
        race_name,
        driver,
        model="logistic"
    ):

        d = self.get_driver(
            race_name=race_name,
            driver=driver,
            model=model
        )

        if d is None:
            return None

        summary = {

            # Identity
            "driver_code": d["driver"],
            "driver_name": d["driver_name"],

            # Prediction
            "rank": int(d["rank"]),
            "podium_probability": round(
                d["pred_top3_prob"] * 100,
                2
            ),

            # Top model features
            "qualifying_position": d["qualifying_position"],
            "quali_stage": d["quali_stage"],
            "gap_to_pole_norm": d["gap_to_pole_norm"],
            "points_per_race": d["points_per_race"],

            # Supporting features
            "long_run_pace": d["fp_long_run_pace"],
            "avg_finish_last5": d["avg_finish_last5"],
            "reliability": d["reliability"],

            # Context
            "track_type": d["track_type"],
            "wet_track": bool(d["wet_track_flag"])
        }

        # Remove None values
        summary = {
            key: value
            for key, value in summary.items()
            if value is not None
        }

        return summary