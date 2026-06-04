import pandas as pd

POINTS_MAP = {
        1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
        6: 8, 7: 6, 8: 4, 9: 2, 10: 1
    }

def load_race_data(season: int, race_list: list):

    all_data = []

    for race in race_list:
        race_clean = race.replace(" ", "_")
        path = f"data/raw/{season}_{race_clean}_R.csv"

        try:
            df = pd.read_csv(path)
            df["team"] = df["team"].str.upper().str.strip()
            all_data.append(df) 
        except FileNotFoundError:
            raise RuntimeError(f"Missing race file: {path}")

    # ✅ FIX: handle empty case
    if len(all_data) == 0:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


def assign_points(df: pd.DataFrame):

    df = df.copy()  # 🔥 avoid side effects

    df["points"] = df["position"].map(POINTS_MAP).fillna(0)

    return df

def compute_constructor_standings(df: pd.DataFrame):

    team_points = (
        df.groupby("team")["points"]
        .sum()
        .reset_index()
        .sort_values(by="points", ascending=False)
    )

    team_points["constructor_position"] = range(1, len(team_points) + 1)

    return team_points

def compute_points_per_race(df: pd.DataFrame, num_races: int):

    team_points = (
        df.groupby("team")["points"]
        .sum()
        .reset_index()
    )

    team_points["points_per_race"] = team_points["points"] / num_races

    return team_points

def build_constructor_features(df: pd.DataFrame, num_races: int):

    df = assign_points(df)

    standings = compute_constructor_standings(df)
    ppr = compute_points_per_race(df, num_races)

    features = standings.merge(ppr, on="team")

    return features[[
        "team",
        "constructor_position",
        "points_per_race"
    ]]

def process_constructor_features(season: int, race_list: list):

    df = load_race_data(season, race_list[:-1])

    if df.empty:
        return pd.DataFrame(columns=[
            "team",
            "constructor_position",
            "points_per_race"
        ])

    features = build_constructor_features(df, len(race_list[:-1]))

    return features
