import pandas as pd
import os
from data.calendar import F1_2026_SCHEDULE
from data.load_target import load_multiple_race_results

# ---------------------------
# MAIN PIPELINE FUNCTION
# ---------------------------
def process_reliability(season: int, race_list: list, target_race: str):

    # STEP 1: load ONLY past races
    df = load_multiple_race_results(season, race_list[:-1])

    # STEP 2: add dummy target race if missing
    if target_race not in df["race"].values:
        drivers = df["driver"].unique()

        target_df = pd.DataFrame({
            "driver": drivers,
            "race": target_race,
            "dnf_flag": pd.NA,
            "status": ""
        })

        df = pd.concat([df, target_df], ignore_index=True)

    # ✅ ALWAYS define race_order (outside if)
    race_order = {race: i for i, race in enumerate(race_list)}
    df["race_order"] = df["race"].map(race_order)

    # sort AFTER everything is ready
    df = df.sort_values(by=["driver", "race_order"])

    # ---------------------------
    # CHECK
    # ---------------------------
    if "dnf_flag" not in df.columns:
        raise ValueError("dnf_flag missing — check raw race data pipeline")

    print("\n=== RAW DNF CHECK ===")
    print(df[["driver", "race", "status", "dnf_flag"]].head(20))

    # ---------------------------
    # DNF RATE
    # ---------------------------
    df["dnf_flag"] = pd.to_numeric(df["dnf_flag"], errors="coerce").fillna(0)
    df["dnf_rate"] = (
        df.groupby("driver")["dnf_flag"]
        .transform(lambda x: x.shift(1).ewm(span=5, min_periods=1).mean())
    )

    # ---------------------------
    # RELIABILITY
    # ---------------------------
    df["reliability"] = 1 - df["dnf_rate"]

    # ---------------------------
    # SAVE DEBUG
    # ---------------------------
    os.makedirs("outputs/debug", exist_ok=True)
    df.to_csv(f"outputs/debug/{season}_reliability_full.csv", index=False)

    # ---------------------------
    # FINAL FEATURES (target race row)
    # ---------------------------
    features = df.groupby("driver").tail(1).copy()

    # fallback for first race
    features["reliability"] = features["reliability"].fillna(
        1 - features["dnf_flag"].fillna(0).astype(float)
    )

    features["reliability"] = features["reliability"].clip(0, 1)

    print("\n=== RELIABILITY OUTPUT ===")
    print(features.sort_values("reliability"))

    print("\n=== FINAL RELIABILITY (ALL DRIVERS) ===")
    print(features.sort_values("reliability"))

    features.to_csv(
        f"outputs/debug/{season}_reliability_final.csv",
        index=False
    )

    return features