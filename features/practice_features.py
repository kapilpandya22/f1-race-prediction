import os
import pandas as pd

def load_practice_data(season, race_name):

    base = f"data/raw/{season}_{race_name.replace(' ', '_')}"

    # Try FP2 first
    fp2_path = f"{base}_FP2.csv"
    if os.path.exists(fp2_path):
        print(f"✅ Using FP2 for {season} {race_name}")
        return pd.read_csv(fp2_path)

    # Fallback to FP1
    fp1_path = f"{base}_FP1.csv"
    if os.path.exists(fp1_path):
        print(f"⚠️ FP2 missing → using FP1 for {season} {race_name}")
        return pd.read_csv(fp1_path)

    print(f"❌ No FP2 or FP1 found for {season} {race_name}")
    return pd.DataFrame()

def convert_lap_time(df: pd.DataFrame) -> pd.DataFrame:
    df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").dt.total_seconds()
    return df

def filter_valid_laps(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["LapTime"].notnull()]
    df = df[df["LapTime"] > 0]
    return df

def get_long_runs(df: pd.DataFrame, min_laps: int = 5):

    long_run_data = []
    df = df.sort_values(by=["driver", "Stint"])
    for (driver, stint), group in df.groupby(["driver", "Stint"]):
        if len(group) >= min_laps:
            long_run_data.append(group)

    if not long_run_data:
        return pd.DataFrame()
    
    
    return pd.concat(long_run_data)

def compute_practice_features(df: pd.DataFrame):

    # 🔥 normalize lap time (CRITICAL)
    df["LapTime_norm"] = df["LapTime"] / df["LapTime"].min()

    features = df.groupby("driver").agg(
        fp_long_run_pace=("LapTime_norm", "mean"),
        fp_consistency=("LapTime_norm", "std")
    ).reset_index()

    # handle NaN
    features["fp_consistency"] = features["fp_consistency"].fillna(0)

    # 🔥 relative consistency
    features["fp_consistency_norm"] = (
        features["fp_consistency"] / features["fp_long_run_pace"]
    )

    # 🔥 ranking (VERY IMPORTANT)
    features["fp_rank"] = features["fp_long_run_pace"].rank()
    features["fp_percentile"] = features["fp_long_run_pace"].rank(pct=True)

    return features

def process_practice(season: int, race_name: str):

    df = load_practice_data(season, race_name)
    print(f"Laps loaded: {len(df)}")

    if df.empty:
        return pd.DataFrame(columns=[
            "driver",
            "fp_long_run_pace",
            "fp_consistency"
        ])

    df = convert_lap_time(df)
    df = filter_valid_laps(df)
    df = get_long_runs(df)

    if df.empty:
        return pd.DataFrame(columns=[
            "driver",
            "fp_long_run_pace",
            "fp_consistency"
        ])

    features = compute_practice_features(df)

    return features

