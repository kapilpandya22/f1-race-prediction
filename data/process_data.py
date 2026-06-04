import pandas as pd
import os


def load_raw_qualifying(season: int, race_name: str) -> pd.DataFrame:
    race_clean = race_name.replace(" ", "_")
    path = f"data/raw/{season}_{race_clean}_Q.csv"

    if not os.path.exists(path):
        raise RuntimeError(f"Missing qualifying file: {path}")
    return pd.read_csv(path)

def convert_time_to_seconds(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["q1", "q2", "q3"]:
        df[col] = pd.to_timedelta(df[col], errors="coerce").dt.total_seconds()

    return df

def compute_gap_to_pole(df: pd.DataFrame) -> pd.DataFrame:

    df["best_qualifying_time"] = df[["q3", "q2", "q1"]].bfill(axis=1).iloc[:, 0]

    valid_times = df["best_qualifying_time"].dropna()

    if valid_times.empty:
        df["gap_to_pole"] = float("nan")
        df["gap_to_pole_norm"] = 0
        return df

    pole_time = valid_times.min()
    df["gap_to_pole"] = (df["best_qualifying_time"] - pole_time).clip(lower=0)

    # ✅ ADD THIS BLOCK
    mean_gap = df["gap_to_pole"].mean()
    std_gap = df["gap_to_pole"].std()

    if std_gap == 0 or pd.isna(std_gap):
        df["gap_to_pole_norm"] = 0
    else:
        df["gap_to_pole_norm"] = (df["gap_to_pole"] - mean_gap) / std_gap
    
    df["gap_to_pole_norm"] = -df["gap_to_pole_norm"]

    df["gap_to_pole_norm"] = df["gap_to_pole_norm"].fillna(0)
    df["gap_to_pole_norm"] = df["gap_to_pole_norm"].clip(-3, 3)
    return df

def encode_quali_stage(df: pd.DataFrame) -> pd.DataFrame:


    df["quali_stage"] = 1
    df.loc[df["q2"].notna(), "quali_stage"] = 2
    df.loc[df["q3"].notna(), "quali_stage"] = 3

    df["quali_stage"] = df["quali_stage"].astype(int)

    return df

def select_qualifying_features(df: pd.DataFrame) -> pd.DataFrame:

    df_final = df[[
        "driver",
        "team",
        "position",
        "gap_to_pole_norm",
        "quali_stage"
    ]].copy()

    df_final = df_final.rename(columns={
    "position": "qualifying_position"
    })

    return df_final

def save_processed_qualifying(df: pd.DataFrame, season: int, race_name: str):
    race_clean = race_name.replace(" ", "_")

    path = f"data/processed/{season}_{race_clean}_quali.csv"

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(path, index=False)

    print(f"Saved processed data → {path}")

def process_qualifying(season: int, race_name: str):

    df = load_raw_qualifying(season, race_name)

    print("\n=== QUALI RAW COLUMNS ===")
    print(df.columns)

    # ---------------------------
    # FIX TEAM COLUMN (CRITICAL)
    # ---------------------------
    if "team" not in df.columns:
        print("⚠️ team missing in qualifying → merging from race data")

        race_clean = race_name.replace(" ", "_")
        race_path = f"data/raw/{season}_{race_clean}_R.csv"

        race_df = pd.read_csv(race_path)[["driver", "team"]]

        df = df.merge(
            race_df,
            on="driver",
            how="left"
        )

    # Normalize team names
    df["team"] = df["team"].str.upper().str.strip()

    # Safety check
    if df["team"].isna().any():
        raise ValueError("❌ Some drivers missing team after merge")

    # ---------------------------
    # Continue pipeline
    # ---------------------------
    df = convert_time_to_seconds(df)
    df = compute_gap_to_pole(df)
    df = encode_quali_stage(df)
    df = select_qualifying_features(df)

    save_processed_qualifying(df, season, race_name)

    return df    