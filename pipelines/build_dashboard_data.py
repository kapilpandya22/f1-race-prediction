import os
import glob
import pandas as pd
from pipelines.update_metadata import (
    update_track_metadata,
    update_weather_metadata
)

from pipelines.fill_weather_history import (
    fill_weather_history
)



GOLDEN_DIR = "data/golden"
OUTPUT_DIR = "data/golden/dashboard"


def load_all_race_files():

    race_files = glob.glob(
        os.path.join(
            GOLDEN_DIR,
            "*_R.csv"
        )
    )

    dfs = []

    for file in race_files:

        df = pd.read_csv(file)

        dfs.append(df)

    if len(dfs) == 0:
        raise RuntimeError(
            "No golden race files found"
        )

    return pd.concat(
        dfs,
        ignore_index=True
    )
    
def build_driver_standings(df):

    standings = (
        df.groupby(
            ["driver", "team"],
            as_index=False
        )
        .agg(
            points=("points", "sum"),
            wins=("winner", "sum"),
            podiums=("podium", "sum"),
            dnfs=("dnf_flag", "sum"),
            races=("race", "nunique")
        )
        .sort_values(
            "points",
            ascending=False
        )
    )

    standings.to_csv(
        f"{OUTPUT_DIR}/driver_standings.csv",
        index=False
    )

    print(
        "✅ driver_standings.csv"
    )
    
def build_constructor_standings(df):

    standings = (
        df.groupby(
            "team",
            as_index=False
        )
        .agg(
            points=("points", "sum"),
            wins=("winner", "sum"),
            podiums=("podium", "sum"),
            dnfs=("dnf_flag", "sum"),
            races=("race", "nunique")
        )
        .sort_values(
            "points",
            ascending=False
        )
    )

    standings.to_csv(
        f"{OUTPUT_DIR}/constructor_standings.csv",
        index=False
    )

    print(
        "✅ constructor_standings.csv"
    )

def build_driver_season_stats(df):

    stats = (
        df.groupby(
            ["driver", "team"],
            as_index=False
        )
        .agg(
            races=("race", "nunique"),

            points=("points", "sum"),

            wins=("winner", "sum"),
            podiums=("podium", "sum"),

            avg_finish=("position", "mean"),

            best_finish=("position", "min"),
            worst_finish=("position", "max"),

            avg_grid=("grid_position", "mean"),

            positions_gained_avg=(
                "positions_gained",
                "mean"
            ),

            dnfs=("dnf_flag", "sum")
        )
    )

    consistency = (
        df.groupby("driver")["position"]
        .std()
        .reset_index(name="position_std")
    )

    stats = stats.merge(
        consistency,
        on="driver",
        how="left"
    )

    stats["consistency_score"] = (
        1 / (stats["position_std"] + 1)
    )

    stats.drop(
        columns=["position_std"],
        inplace=True
    )

    stats.to_csv(
        f"{OUTPUT_DIR}/driver_season_stats.csv",
        index=False
    )

    print(
        "✅ driver_season_stats.csv"
    )
 
def build_team_season_stats(df):

    stats = (
        df.groupby(
            "team",
            as_index=False
        )
        .agg(
            races=("race", "nunique"),

            points=("points", "sum"),

            wins=("winner", "sum"),
            podiums=("podium", "sum"),

            avg_finish=("position", "mean"),

            avg_grid=("grid_position", "mean"),

            dnfs=("dnf_flag", "sum")
        )
    )

    stats["reliability_score"] = (
        1 -
        (
            stats["dnfs"]
            /
            (
                stats["races"] * 2
            )
        )
    )

    stats.to_csv(
        f"{OUTPUT_DIR}/team_season_stats.csv",
        index=False
    )

    print(
        "✅ team_season_stats.csv"
    )

def build_driver_race_stats(df):

    cols = [

        "season",
        "round",
        "race",

        "driver",
        "team",

        "grid_position",
        "position",

        "positions_gained",

        "points",

        "winner",
        "podium",

        "finished_race",
        "dnf_flag",

        "status"
    ]

    race_stats = df[cols].copy()

    race_stats.to_csv(
        f"{OUTPUT_DIR}/driver_race_stats.csv",
        index=False
    )

    print(
        "✅ driver_race_stats.csv"
    )
    
    
    
def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    update_track_metadata()

    update_weather_metadata()
    
    print("🚀 RUNNING WEATHER HISTORY")
    fill_weather_history()     # NEW
    
    df = load_all_race_files()
    
    TEAM_MAP = {

        "Red Bull": "Red Bull Racing",
        "Red Bull Racing": "Red Bull Racing",

        "Racing Bulls": "RB F1 Team",
        "RB F1 Team": "RB F1 Team",

        "Alpine": "Alpine F1 Team",
        "Alpine F1 Team": "Alpine F1 Team",

        "Cadillac": "Cadillac F1 Team",
        "Cadillac F1 Team": "Cadillac F1 Team"
    }

    df["team"] = (
        df["team"]
        .replace(TEAM_MAP)
    )
    
    build_driver_standings(df)

    build_constructor_standings(df)

    build_driver_season_stats(df)

    build_team_season_stats(df)

    build_driver_race_stats(df)

    print(
        "\n🚀 Dashboard data built successfully"
    )


if __name__ == "__main__":
    main()     