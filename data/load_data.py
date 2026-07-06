import fastf1
import os
import time
import pandas as pd


# ---------------------------
# CACHE SETUP
# ---------------------------
def enable_cache(cache_dir: str = "data/cache") -> None:
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)



# ---------------------------
# SESSION LOADING
# ---------------------------
def safe_load_session(season, race_name, session_type, retries=3):

    for i in range(retries):
        try:
            session = fastf1.get_session(
                season,
                race_name,
                session_type
            )

            session.load()
            return session

        except Exception as e:

            print("\n========================")
            print(f"Season: {season}")
            print(f"Race: {race_name}")
            print(f"Session: {session_type}")
            print(f"Exception Type: {type(e)}")
            print(f"Exception: {e}")
            print("========================\n")

            print(
                f"⚠️ Retry {i+1} for {race_name} {session_type}"
            )

            time.sleep(2)

    raise RuntimeError(
        f"Failed to load session: {race_name} {session_type}"
    )


# ---------------------------
# RAW QUALIFYING DATA
# ---------------------------
def get_raw_qualifying(session) -> pd.DataFrame:
    results = session.results.copy()

    df = pd.DataFrame({
        "driver": results["Abbreviation"],
        "driver_number": results["DriverNumber"],
        "team": results["TeamName"],
        "position": results["Position"],
        "q1": results["Q1"],
        "q2": results["Q2"],
        "q3": results["Q3"]
    })

    return df

# ---------------------------
# SAVE FUNCTION
# ---------------------------
def save_raw_data(df: pd.DataFrame, season: int, race_name: str, session_type: str):
    race_clean = race_name.replace(" ", "_")

    path = f"data/raw/{season}_{race_clean}_{session_type}.csv"

    os.makedirs("data/raw", exist_ok=True)

    df.to_csv(path, index=False)

    print(f"Saved raw data → {path}")




def fetch_and_store_qualifying(season: int, race_name: str):

    
    race_clean = race_name.replace(" ", "_")
    path = f"data/raw/{season}_{race_clean}_Q.csv"

    # ✅ FILE EXISTS CHECK
    if os.path.exists(path):
        print(f"✔ Qualifying exists: {path}")
        return

    session = safe_load_session(season, race_name, "Q")
    if session.results is None or session.results.empty:
        raise RuntimeError(f"Empty qualifying data for {race_name}")

    df = get_raw_qualifying(session)
    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    save_raw_data(df, season, race_name, "Q")         


# ---------------------------
# RAW PRACTICE LAPS
# ---------------------------
def get_raw_practice_laps(session):
    laps = session.laps.copy()

    df = laps[[
        "Driver",
        "LapTime",
        "Stint",
        "Compound",
        "TyreLife"
    ]].copy()

    df = df.rename(columns={"Driver": "driver"})
    return df

# ---------------------------
# FETCH & SAVE PRACTICE
# ---------------------------
def fetch_and_store_practice(season, race_name, session_type):

    
    race_clean = race_name.replace(" ", "_")
    path = f"data/raw/{season}_{race_clean}_{session_type}.csv"

    # ✅ FILE EXISTS CHECK
    if os.path.exists(path):
        print(f"✔ Practice exists: {path}")
        return

    try:
        session = safe_load_session(season, race_name, session_type)
        
        laps = get_raw_practice_laps(session)
        if laps is None or laps.empty:
            raise RuntimeError(f"No lap data for {race_name} {session_type}")

        os.makedirs("data/raw", exist_ok=True)
        laps.to_csv(path, index=False)

        print(f"✅ Saved practice → {path}")

    except Exception as e:
        raise RuntimeError(f"{session_type} failed for {race_name}: {e}")

# ---------------------------
# RAW RACE RESULTS
# ---------------------------
def get_raw_race_results(session):
    results = session.results.copy()

    df = pd.DataFrame({
        "driver": results["Abbreviation"],
        "team": results["TeamName"],
        "position": results["Position"],
        "status": results["Status"],
        "grid_position": results["GridPosition"],
        "points": results["Points"]
    })
    

    # Convert position to numeric
    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    # Mark DNFs using status
    df["status"] = df["status"].fillna("").str.lower()
    df["dnf_flag"] = df["status"].str.contains(
        "retired|dnf|did not start|dns|withdrawn|disqualified",
        case=False
    ).astype(int)

    # Force DNF positions to NaN
    df.loc[df["dnf_flag"] == 1, "position"] = None

    print("\n=== DEBUG SAVING RACE FILE ===")
    print(df.head())
    print(df.columns)

    return df


# ---------------------------
# FETCH & SAVE RACE
# ---------------------------
def fetch_and_store_race(season: int, race_name: str):

    race_clean = race_name.replace(" ", "_")

    raw_path = f"data/raw/{season}_{race_clean}_R.csv"
    golden_path = f"data/golden/{season}_{race_clean}_R.csv"

    # ---------------------------
    # SKIP LOGIC
    # ---------------------------
    if os.path.exists(raw_path):
        if season != 2026 or os.path.exists(golden_path):
            print(f"✔ Race exists: {race_name}")
            return

    # ---------------------------
    # LOAD SESSION
    # ---------------------------
    session = safe_load_session(season, race_name, "R")

    if session.results is None or session.results.empty:
        raise RuntimeError(f"Empty race data for {race_name}")

    df = get_raw_race_results(session)
    
    # ---------------------------
    # SAVE RAW (ALL SEASONS)
    # ---------------------------
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(raw_path, index=False)
    
    
    df["season"] = season
    df["race"] = race_name
    df["round"] = session.event["RoundNumber"]
    df["podium"] = (df["position"] <= 3).astype(int)
    df["winner"] = (df["position"] == 1).astype(int)
    df["finished_race"] = (df["dnf_flag"] == 0).astype(int)
    df["positions_gained"] = (df["grid_position"] - df["position"])
    
    # ---------------------------
    # REORDER COLUMNS
    # ---------------------------
    df = df[
        [
            "season",
            "round",
            "race",
            "driver",
            "team",
            "grid_position",
            "position",
            "positions_gained",
            "points",
            "podium",
            "winner",
            "finished_race",
            "dnf_flag",
            "status"
        ]
    ]


    # ---------------------------
    # SAVE GOLDEN (ONLY 2026)
    # ---------------------------
    if season == 2026:
        os.makedirs("data/golden", exist_ok=True)
        df.to_csv(golden_path, index=False)
        print(f"✅ Saved raw + golden → {race_name}")
    else:
        print(f"✅ Saved raw only → {race_name}")