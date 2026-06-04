import pandas as pd


def merge_all_features(
    quali_df,
    practice_df,
    driver_df,
    constructor_df,
    track_df,
    weather_df,
    reliability_df
):

    # ---------------------------
    # BASE
    # ---------------------------
    df = quali_df.copy()

    # ---------------------------
    # MERGES
    # ---------------------------
    df = df.merge(practice_df, on="driver", how="left", suffixes=("", "_practice"))
    df = df.merge(driver_df, on="driver", how="left", suffixes=("", "_driver"))
    df = df.merge(constructor_df, on="team", how="left", suffixes=("", "_constructor"))
    df = df.merge(track_df, on="driver", how="left")
    df = df.merge(weather_df, on="driver", how="left")
    reliability_df = reliability_df.drop(columns=["team"], errors="ignore")
    df = df.merge(reliability_df, on="driver", how="left")

    # 🔥 MOVE DEBUG HERE
    print("\n=== JUST BEFORE GROUPBY ===")
    print(df.columns)

    # ---------------------------
    # DEBUG
    # ---------------------------
    print("Drivers in quali:", set(quali_df["driver"]))
    print("Drivers in practice:", set(practice_df["driver"]))

    missing_practice = set(quali_df["driver"]) - set(practice_df["driver"])
    if missing_practice:
        print("⚠️ Missing practice drivers:", missing_practice)

    # ---------------------------
    # SAFE FILLING
    # ---------------------------
    df["fp_long_run_pace"] = df["fp_long_run_pace"].fillna(df["fp_long_run_pace"].mean())
    df["fp_consistency"] = df["fp_consistency"].fillna(0)

    df["avg_finish_last5"] = df["avg_finish_last5"].fillna(df["avg_finish_last5"].mean())
    df["reliability"] = df["reliability"].fillna(0.8)

    # ---------------------------
    # FEATURE ENGINEERING
    # ---------------------------

    # 1. Quali × Pace
    df["quali_x_pace"] = df["qualifying_position"] * df["fp_long_run_pace"]

    # 2. Form × Quali
    df["form_x_quali"] = df["avg_finish_last5"] * df["qualifying_position"]

    # 3. Teammate gap (SAFE)
    team_mean = df.groupby("team")["gap_to_pole_norm"].transform("mean")
    df["teammate_gap"] = df["gap_to_pole_norm"] - team_mean
    df["teammate_gap"] = df["teammate_gap"].fillna(0)
    

    return df