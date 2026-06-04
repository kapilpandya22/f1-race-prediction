import pandas as pd
import os
from data.load_target import build_target
from data.load_data import fetch_and_store_race
from data.load_data import fetch_and_store_qualifying
from data.load_data import fetch_and_store_practice
from features.feature_list import FEATURE_COLS as feature_cols
from models.logistic import train_logistic, predict_logistic
from models.random_forest import train_rf, predict_rf
from models.xgboost import train_xgb, predict_xgb
from data.calendar import (
    F1_2023_SCHEDULE,
    F1_2024_SCHEDULE,
    F1_2025_SCHEDULE
)



# ---------------------------------------------------------------------------------
# LOGISTIC REGRESSION
# ---------------------------------------------------------------------------------
def prepare_training_data(final_df, season, race_name):

    target_df = build_target(season, race_name)

    df = final_df.copy()

    # ✅ FIX: standardize driver names BEFORE merge
    df["driver"] = df["driver"].str.upper().str.strip()
    target_df["driver"] = target_df["driver"].str.upper().str.strip()

    df = df.merge(target_df, on="driver", how="left")

    missing = df["target_top3"].isna().sum()
    print(f"Missing targets: {missing}")

    return df


def build_training_dataset(train_seasons: list, race_history_2026: list):

    from features.build_features import run_pipeline

    all_data = []

    schedule_map = {
        2023: F1_2023_SCHEDULE,
        2024: F1_2024_SCHEDULE,
        2025: F1_2025_SCHEDULE
    }

    # ---------------------------
    # PAST SEASONS
    # ---------------------------
    for season in train_seasons:
        for race in schedule_map[season]:

            print(f"Processing: {season} - {race}")

            race_clean = race.replace(" ", "_")

            r_path = f"data/raw/{season}_{race_clean}_R.csv"
            q_path = f"data/raw/{season}_{race_clean}_Q.csv"
            fp2_path = f"data/raw/{season}_{race_clean}_FP2.csv"
            fp1_path = f"data/raw/{season}_{race_clean}_FP1.csv"

            # --- VALIDATION ONLY ---
            if not os.path.exists(r_path):
                print(f"⚠️ Missing race → fetching: {season} {race}")
                fetch_and_store_race(season, race)

                if not os.path.exists(r_path):
                    raise RuntimeError(f"Still missing after fetch: {r_path}")

            if not os.path.exists(q_path):
                print(f"⚠️ Missing qualifying → fetching: {season} {race}")
                fetch_and_store_qualifying(season, race)

            if not (os.path.exists(fp2_path) or os.path.exists(fp1_path)):
                print(f"⚠️ Missing practice → fetching: {season} {race}")
                try:
                    fetch_and_store_practice(season, race, "FP2")
                except:
                    fetch_and_store_practice(season, race, "FP1")

            # --- BUILD FEATURES ---
            df = run_pipeline(target_race=race, season=season)

            if df.empty:
                print(f"⚠️ Skipping {season} {race}")
                continue

            df = prepare_training_data(df, season, race)
            df["season"] = season
            df["race"] = race

            all_data.append(df)

    # ---------------------------
    # CURRENT SEASON (2026)
    # ---------------------------
    for race in race_history_2026:

        print(f"Processing: 2026 - {race}")

        race_clean = race.replace(" ", "_")

        r_path = f"data/raw/2026_{race_clean}_R.csv"
        q_path = f"data/raw/2026_{race_clean}_Q.csv"
        fp2_path = f"data/raw/2026_{race_clean}_FP2.csv"
        fp1_path = f"data/raw/2026_{race_clean}_FP1.csv"

        # --- VALIDATION AND FETCH ---
        if not os.path.exists(r_path):
            print(f"⚠️ Missing race → fetching: 2026 {race}")
            fetch_and_store_race(2026, race)

            if not os.path.exists(r_path):
                raise RuntimeError(f"Still missing after fetch: {r_path}")

        if not os.path.exists(q_path):
            print(f"⚠️ Missing qualifying → fetching: 2026 {race}")
            fetch_and_store_qualifying(2026, race)

        if not (os.path.exists(fp2_path) or os.path.exists(fp1_path)):
            print(f"⚠️ Missing practice → fetching: 2026 {race}")
            try:
                fetch_and_store_practice(2026, race, "FP2")
            except:
                fetch_and_store_practice(2026, race, "FP1")

        df = run_pipeline(target_race=race, season=2026)

        if df.empty:
            print(f"⚠️ Skipping 2026 {race}")
            continue

        df = prepare_training_data(df, 2026, race)
        df["season"] = 2026
        df["race"] = race

        all_data.append(df)

    # ---------------------------
    # FINAL
    # ---------------------------
    if len(all_data) == 0:
        raise ValueError("No training data built")

    df = pd.concat(all_data, ignore_index=True)

    print("\n=== TRAIN DATA SUMMARY ===")
    print(df.groupby("season")["race"].nunique())

    return df

from data.load_target import build_target

def build_test_dataset(final_df, season, race_name):

    df = final_df.copy()

    race_clean = (
        race_name
        .replace(" ", "_")
    )

    result_path = (
        f"data/golden/"
        f"{season}_{race_clean}_R.csv"
    )

    # ---------------------------
    # FUTURE RACE
    # ---------------------------
    if not os.path.exists(result_path):

        print(
            f"🟢 Future race detected: "
            f"{race_name}"
        )

        df["target_top3"] = None

        return df

    # ---------------------------
    # PAST RACE
    # ---------------------------
    target_df = build_target(
        season,
        race_name
    )

    df["driver"] = (
        df["driver"]
        .str.upper()
        .str.strip()
    )

    target_df["driver"] = (
        target_df["driver"]
        .str.upper()
        .str.strip()
    )

    df = df.merge(
        target_df,
        on="driver",
        how="left"
    )

    return df

def run_logistic_model(train_df, final_df, season, race_name, race_history, train_seasons):
  
    # Remove target race from training (safety)
    train_df = train_df[train_df["race"] != race_name].copy()

    test_df = build_test_dataset(final_df, season, race_name).copy()
    test_df["race"] = race_name   # ✅ FIX
    train_df["driver"] = train_df["driver"].str.upper().str.strip()
    test_df["driver"] = test_df["driver"].str.upper().str.strip()
    # ---------------------------
    # DEBUG CHECKS (MOVE HERE)
    # ---------------------------
    print("\n=== TRAIN DATA CHECK ===")

    print("\nRaces per season:")
    print(train_df.groupby("season")["race"].nunique())

    print("\nSample races per season:")
    for s in train_df["season"].unique():
        print(f"\nSeason {s}:")
        print(train_df[train_df["season"] == s]["race"].unique()[:5])

    print("\nChecking leakage...")

    if race_name in train_df["race"].values:
        print("❌ ERROR: Target race leaked into training!")
    else:
        print("✅ No leakage — correct split")

    print("\n=== TEST DATA ===")
    print(test_df["race"].unique())

    # ---------------------------
    # MODEL
    # ---------------------------
    train_df = train_df.dropna(subset=["target_top3"])
    
    train_df.loc[:, "sample_weight"] = train_df["season"].map({
        2023: 1.0,
        2024: 1.3,
        2025: 1.7,
        2026: 2.0
    })
    weights = train_df["sample_weight"]

    missing = set(feature_cols) - set(train_df.columns)
    if missing:
        raise ValueError(f"Missing features in TRAIN: {missing}")

    missing = set(feature_cols) - set(test_df.columns)
    if missing:
        raise ValueError(f"Missing features in TEST: {missing}")
    
    
    print("\n=== FEATURES USED ===")
    print(feature_cols)
    X_train, X_test = prepare_features(train_df, test_df, feature_cols)
    y_train = train_df["target_top3"]

    model, scaler = train_logistic(X_train, y_train, sample_weight=weights)
    model.feature_names_ = X_train.columns.tolist()
    probs = predict_logistic(model, scaler, X_test)
    
    # raw probabilities (for ranking)
    test_df["pred_rank_score"] = probs

    # clipped probabilities (for display / metrics)
    test_df["pred_top3_prob"] = probs.clip(0.01, 0.99)
    test_df = test_df.sort_values(by="pred_rank_score", ascending=False).reset_index(drop=True)
    test_df["rank"] = test_df.index + 1

    return test_df, model


# ---------------------------------------------------------------------------------
# RANDOM FOREST
# ---------------------------------------------------------------------------------
def run_rf_model(train_df, final_df, season, race_name, race_history, train_seasons):

    
    # remove leakage
    train_df = train_df[train_df["race"] != race_name].copy()

    test_df = build_test_dataset(final_df, season, race_name).copy()
    test_df["race"] = race_name
    train_df["driver"] = train_df["driver"].str.upper().str.strip()
    test_df["driver"] = test_df["driver"].str.upper().str.strip()
    # ---------------------------
    # PREP DATA
    # ---------------------------
    train_df = train_df.dropna(subset=["target_top3"])
   
  
    train_df.loc[:, "sample_weight"] = train_df["season"].map({
        2023: 1.0,
        2024: 1.3,
        2025: 1.7,
        2026: 2.0
    })

    weights = train_df["sample_weight"]
    
    missing = set(feature_cols) - set(train_df.columns)
    if missing:
        raise ValueError(f"Missing features in TRAIN: {missing}")

    missing = set(feature_cols) - set(test_df.columns)
    if missing:
        raise ValueError(f"Missing features in TEST: {missing}")
    
    print("\n=== FEATURES USED ===")
    print(feature_cols)
    X_train, X_test = prepare_features(train_df, test_df, feature_cols)
    y_train = train_df["target_top3"]


    # ---------------------------
    # TRAIN
    # ---------------------------
    model = train_rf(X_train, y_train, sample_weight=weights)
    model.feature_names_ = X_train.columns.tolist()
    probs = predict_rf(model, X_test)
    
    # ---------------------------
    # OUTPUT
    # ---------------------------
    # REAL → for ranking
    test_df["pred_rank_score"] = probs

    # CLEAN → for humans
    test_df["pred_top3_prob"] = probs.clip(0.01, 0.99)

    # IMPORTANT
    test_df = test_df.sort_values(by="pred_rank_score", ascending=False).reset_index(drop=True)
    test_df["rank"] = test_df.index + 1

    return test_df, model

def prepare_features(train_df, test_df, feature_cols):

    X_train = train_df[feature_cols].copy()
    X_test  = test_df[feature_cols].copy()

    # enforce column order
    X_test = X_test[X_train.columns]

    # force numeric
    X_train = X_train.apply(pd.to_numeric, errors="coerce")
    X_test  = X_test.apply(pd.to_numeric, errors="coerce")

    means = X_train.mean(numeric_only=True)

    # drop fully empty columns
    empty_cols = means[means.isna()].index.tolist()

    if empty_cols:
        print(f"Dropping empty features: {empty_cols}")
        X_train = X_train.drop(columns=empty_cols)
        X_test = X_test.drop(columns=empty_cols)
        means = X_train.mean()

    # fill remaining
    X_train = X_train.fillna(means)
    X_test  = X_test.fillna(means)

    # 🚨 HARD CHECK (this is key)
    if X_train.isna().any().any():
        raise ValueError("NaNs still in X_train after preprocessing")

    if X_test.isna().any().any():
        raise ValueError("NaNs still in X_test after preprocessing")
    
    print("Train shape:", X_train.shape)
    print("Test shape:", X_test.shape)
    
    if list(X_train.columns) != list(X_test.columns):
        raise ValueError("Train/Test feature mismatch after preprocessing")

    return X_train.astype(float), X_test.astype(float)

def run_xgb_model(train_df, final_df, season, race_name, race_history, train_seasons):

    # remove leakage
    train_df = train_df[train_df["race"] != race_name].copy()

    test_df = build_test_dataset(final_df, season, race_name).copy()
    test_df["race"] = race_name

    train_df["driver"] = train_df["driver"].str.upper().str.strip()
    test_df["driver"] = test_df["driver"].str.upper().str.strip()

    # ---------------------------
    # PREP
    # ---------------------------
    train_df = train_df.dropna(subset=["target_top3"])

    train_df["sample_weight"] = train_df["season"].map({
        2023: 1.0,
        2024: 1.3,
        2025: 1.7,
        2026: 2.0
    })

    weights = train_df["sample_weight"]

    missing = set(feature_cols) - set(train_df.columns)
    if missing:
        raise ValueError(f"Missing features in TRAIN: {missing}")

    missing = set(feature_cols) - set(test_df.columns)
    if missing:
        raise ValueError(f"Missing features in TEST: {missing}")

    print("\n=== FEATURES USED ===")
    print(feature_cols)

    X_train, X_test = prepare_features(train_df, test_df, feature_cols)
    y_train = train_df["target_top3"]

    # ---------------------------
    # TRAIN
    # ---------------------------
    model = train_xgb(X_train, y_train, sample_weight=weights)
    model.feature_names_ = X_train.columns.tolist()

    probs = predict_xgb(model, X_test)

    # ---------------------------
    # OUTPUT
    # ---------------------------
    test_df["pred_rank_score"] = probs
    test_df["pred_top3_prob"] = probs.clip(0.01, 0.99)

    test_df = test_df.sort_values(by="pred_rank_score", ascending=False).reset_index(drop=True)
    test_df["rank"] = test_df.index + 1

    return test_df, model