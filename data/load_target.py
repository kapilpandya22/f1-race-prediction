import pandas as pd
import os


def load_single_race_result(season: int, race_name: str):

    race_clean = race_name.replace(" ", "_")

    if season == 2026:
        path = f"data/golden/{season}_{race_clean}_R.csv"
    else:
        path = f"data/raw/{season}_{race_clean}_R.csv"

    print(f"Loading race results from: {path}")

    if not os.path.exists(path):
        if season == 2026:
            print(f"⚠️ No results yet for {race_name} (future race)")
            return pd.DataFrame(columns=["driver", "position"])
        else:
            raise RuntimeError(f"❌ Missing race file: {path}")

    df = pd.read_csv(path)

    if "dnf_flag" not in df.columns:
        print(f"\n❌ BROKEN FILE DETECTED: {path}")
        print(df.columns)
        raise RuntimeError("dnf_flag missing here")

    df["race"] = race_name

    return df[["driver", "position", "dnf_flag", "status"]]


def load_multiple_race_results(season: int, race_list: list):

    all_data = []

    for race in race_list:
        race_clean = race.replace(" ", "_")
        path = f"data/raw/{season}_{race_clean}_R.csv"

        df = pd.read_csv(path)

        if "dnf_flag" not in df.columns:
            print(f"\n❌ BROKEN FILE DETECTED: {path}")
            print(df.columns)
            raise RuntimeError("dnf_flag missing here")

        # ensure consistency
        if "status" not in df.columns:
            df["status"] = ""

        df["status"] = df["status"].fillna("").str.lower()
        df["position"] = pd.to_numeric(df["position"], errors="coerce")

        df["race"] = race
        all_data.append(df)

    # ✅ FIX: check BEFORE concat
    if len(all_data) == 0:
        print("⚠️ No past races available")
        return pd.DataFrame(columns=["driver", "position", "dnf_flag", "status", "race"])

    df = pd.concat(all_data, ignore_index=True)

    return df


def create_top3_target(df: pd.DataFrame):

    df = df.copy()

    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    df["target_top3"] = (df["position"] <= 3).fillna(False).astype(int)

    return df[["driver", "target_top3"]]


def build_target(season: int, race_name: str):

    df = load_single_race_result(season, race_name)

    df = create_top3_target(df)

    return df