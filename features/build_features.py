import pandas as pd
from pipelines.race_logic import get_previous_races
from data.process_data import process_qualifying
from features.practice_features import process_practice
from features.driver_features import process_driver_features
from features.constructor_features import process_constructor_features
from features.track_info import build_track_dataframe
from features.weather import build_weather_features
from features.reliability import process_reliability
from features.merge_features import merge_all_features
from data.load_data import (fetch_and_store_qualifying, fetch_and_store_practice)
from data.load_data import enable_cache
enable_cache()

def get_next_race(schedule, race_history):
    for race in schedule:
        if race not in race_history:
            return race
    return None

def add_interaction_features(df):

    # ---------------------------
    # NORMALIZATION
    # ---------------------------
    grid_size = df["qualifying_position"].dropna().max()
    if pd.isna(grid_size) or grid_size == 0:
        grid_size = 20  # fallback

    df["quali_norm"] = df["qualifying_position"] / grid_size

    # ---------------------------
    # INTERACTIONS
    # ---------------------------
    df["quali_x_pace"] = df["quali_norm"] * df["fp_long_run_pace"]
    df["pace_consistency"] = df["fp_long_run_pace"] * df["fp_consistency"]
    df["form_x_quali"] = df["avg_finish_last5"] * df["quali_norm"]
    df["rain_x_quali"] = (df["rain_probability"] *    df["quali_norm"])

    # ---------------------------
    # HANDLE MISSING
    # ---------------------------
    df["quali_x_pace"] = df["quali_x_pace"].fillna(0)
    df["pace_consistency"] = df["pace_consistency"].fillna(0)
    df["form_x_quali"] = df["form_x_quali"].fillna(0)

    return df

def run_pipeline(target_race: str, season: int, is_evaluation=False):

    from data.calendar import (
        F1_2023_SCHEDULE,
        F1_2024_SCHEDULE,
        F1_2025_SCHEDULE,
        F1_2026_SCHEDULE
    )

    schedule_map = {
        2023: F1_2023_SCHEDULE,
        2024: F1_2024_SCHEDULE,
        2025: F1_2025_SCHEDULE,
        2026: F1_2026_SCHEDULE
    }

    schedule = schedule_map[season]

    race_history = get_previous_races(schedule, target_race)
    race_list = race_history + [target_race]

    print(f"Building features: {season} - {target_race}")
    # ---------------------------
    # ENSURE DATA EXISTS (AUTO-FETCH)
    # ---------------------------
    print("\n=== DATA CHECK ===")

    # Qualifying
    fetch_and_store_qualifying(season, target_race)

    # Practice (try FP2, fallback FP1)
    try:
        fetch_and_store_practice(season, target_race, "FP2")
    except:
        fetch_and_store_practice(season, target_race, "FP1")

    # ---------------------------
    # FEATURES ONLY (NO FETCHING)
    # ---------------------------
    quali_df = process_qualifying(season, target_race)

    practice_df = process_practice(season, target_race)

    driver_df = process_driver_features(
        season=season,
        race_list=race_list,
        target_race=target_race
    )

    constructor_df = process_constructor_features(
        season=season,
        race_list=race_list
    )

    track_df = build_track_dataframe(
        race_name=target_race,
        drivers=quali_df["driver"].tolist()
    )

    weather_df = build_weather_features(
        race_name=target_race,
        drivers=quali_df["driver"].tolist()
    )

    reliability_df = process_reliability(
        season=season,
        race_list=race_list,
        target_race=target_race
    )

    final_df = merge_all_features(
        quali_df,
        practice_df,
        driver_df,
        constructor_df,
        track_df,
        weather_df,
        reliability_df
    )

    final_df["fp_long_run_pace"] = final_df["fp_long_run_pace"].fillna(final_df["fp_long_run_pace"].mean())
    final_df["fp_consistency"] = final_df["fp_consistency"].fillna(final_df["fp_consistency"].mean())
    final_df["reliability"] = final_df["reliability"].fillna(final_df["reliability"].mean())
    final_df["qualifying_position"] = final_df["qualifying_position"].fillna(final_df["qualifying_position"].mean())
    final_df["avg_finish_last5"] = final_df["avg_finish_last5"].fillna(final_df["avg_finish_last5"].mean())
    final_df = add_interaction_features(final_df)
    
    if final_df.empty:
        raise RuntimeError(f"Empty feature set for {season} {target_race}")
    print(final_df[[
        "qualifying_position",
        "fp_long_run_pace",
        "quali_x_pace",
        "form_x_quali"
    ]].head())
    
    return final_df    
  
if __name__ == "__main__":
    df = run_pipeline("Japanese Grand Prix")
    print(df.head())


       