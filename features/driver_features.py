import pandas as pd
import os
from data.load_data import fetch_and_store_race
from data.load_data import fetch_and_store_qualifying
from data.load_data import fetch_and_store_practice

# ---------------------------
# LOAD MULTIPLE RACES
# ---------------------------
def load_multiple_races(season: int, race_list: list):

    all_data = []

    for race in race_list:
        race_clean = race.replace(" ", "_")
        path = f"data/raw/{season}_{race_clean}_R.csv"

        # ✅ FIX: check if file exists
        if not os.path.exists(path):
            print(f"⚠️ Missing race file → fetching: {race}")
            fetch_and_store_race(season, race)

            if not os.path.exists(path):
                raise RuntimeError(f"Still missing after fetch: {path}")

        df = pd.read_csv(path)
        df["race"] = race

        all_data.append(df)

    # ✅ FIX: handle empty case
    if len(all_data) == 0:
        print("❌ No race data available for driver features")
        return pd.DataFrame(columns=["driver", "position", "race"])

    return pd.concat(all_data, ignore_index=True)


# ---------------------------
# COMPUTE DRIVER FORM
# ---------------------------
def compute_driver_form(df: pd.DataFrame, window: int = 5):

    # ✅ Ensure correct ordering inside each driver group
    df = df.sort_values(by=["driver", "race_order"]).copy()

    df["avg_finish_last5"] = (
        df.groupby("driver")["position"]
        .transform(lambda x: x.shift(1).rolling(window, min_periods=1).mean())
    )

    return df



# ---------------------------
# MAIN PIPELINE FUNCTION
# ---------------------------
def process_driver_features(season: int, race_list: list, target_race: str):

    if len(race_list) <= 1:
        return pd.DataFrame(columns=["driver", "avg_finish_last5"])

    df = load_multiple_races(season, race_list[:-1])

    # 🔥 normalize driver names
    df["driver"] = df["driver"].str.upper().str.strip()

    # race ordering
    race_order = {race: i for i, race in enumerate(race_list)}
    df["race_order"] = df["race"].map(race_order)

    df = df.sort_values(by=["driver", "race_order"])

    # 🔥 better signal
    df["finish_score"] = (22 - df["position"]) / 22

    # rolling mean
    df["avg_finish_last5"] = (
        df.groupby("driver")["finish_score"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    )

    # 🔥 trend
    df["finish_trend"] = (
        df.groupby("driver")["position"]
        .transform(lambda x: x.shift(1).diff())
    )

    # 🔥 consistency
    df["finish_std_last5"] = (
        df.groupby("driver")["position"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).std())
    )

    features = df.groupby("driver").tail(1)[
        ["driver", "avg_finish_last5", "finish_trend", "finish_std_last5"]
    ]

    return features.reset_index(drop=True)



