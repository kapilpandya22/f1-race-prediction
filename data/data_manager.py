import os 
from data.load_data import (
    fetch_and_store_race,
    fetch_and_store_qualifying,
    fetch_and_store_practice
)
def ensure_race_data(season, race, is_target):
    race_clean = race.replace(" ", "_")

    r_path = f"data/raw/{season}_{race_clean}_R.csv"
    if is_target and os.path.exists(r_path):
        print(f"⚠️ Removing leaked race file for target: {race}")
        os.remove(r_path)
    q_path = f"data/raw/{season}_{race_clean}_Q.csv"

    if not is_target:
        if not os.path.exists(r_path):
            fetch_and_store_race(season, race)

        if not os.path.exists(r_path):
            raise RuntimeError(f"Missing race file after fetch: {r_path}")
        else:
            print(f"✔ Race exists: {season} {race}")


    if not os.path.exists(q_path):
        fetch_and_store_qualifying(season, race)   

    if not os.path.exists(q_path):
        raise RuntimeError(f"Missing qualifying file after fetch: {q_path}")        

    practice_loaded = False

    for session in ["FP2", "FP1"]:

        path = f"data/raw/{season}_{race_clean}_{session}.csv"

        if os.path.exists(path):
            print(f"✔ {session} exists: {season} {race}")
            practice_loaded = True
            break

        try:
            fetch_and_store_practice(season, race, session)
            print(f"✅ Saved {session}")
            practice_loaded = True
            break
        except Exception:
            continue

    if not practice_loaded:
        raise RuntimeError(f"No practice data for {season} {race}")     