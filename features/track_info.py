import pandas as pd

# Street = 1, Permanent = 0

TRACK_TYPE = {
    # Street Circuits
    "Monaco Grand Prix": 1,
    "Singapore Grand Prix": 1,
    "Las Vegas Grand Prix": 1,
    "Azerbaijan Grand Prix": 1,
    "Saudi Arabian Grand Prix": 1,
    "Miami Grand Prix": 1,
    "Canadian Grand Prix": 1,  # semi-street
    "Spanish Grand Prix": 1,

    # Permanent Circuits
    "Australian Grand Prix": 0,
    "Chinese Grand Prix": 0,
    "Japanese Grand Prix": 0,
    "Bahrain Grand Prix": 0,
    "Barcelona Grand Prix": 0,
    "Austrian Grand Prix": 0,
    "British Grand Prix": 0,
    "Belgian Grand Prix": 0,
    "Hungarian Grand Prix": 0,
    "Dutch Grand Prix": 0,
    "Italian Grand Prix": 0,
    "Emilia Romagna Grand Prix": 0,
    "United States Grand Prix": 0,
    "Mexico City Grand Prix": 0,
    "São Paulo Grand Prix": 0,
    "Qatar Grand Prix": 0,
    "Abu Dhabi Grand Prix": 0
}

OVERTAKING_DIFFICULTY = {
    # Very Hard
    "Monaco Grand Prix": 0.95,
    "Singapore Grand Prix": 0.85,
    "Hungarian Grand Prix": 0.80,
    "Barcelona Grand Prix": 0.75,

    # Medium
    "Australian Grand Prix": 0.50,
    "Japanese Grand Prix": 0.50,
    "Saudi Arabian Grand Prix": 0.50,
    "Dutch Grand Prix": 0.60,
    "Azerbaijan Grand Prix": 0.60,
    "Miami Grand Prix": 0.55,
    "Canadian Grand Prix": 0.55,
    "Spanish Grand Prix": 0.70,

    # Easy
    "Bahrain Grand Prix": 0.30,
    "Italian Grand Prix": 0.30,
    "Emilia Romagna Grand Prix": 0.55,
    "Las Vegas Grand Prix": 0.35,
    "Qatar Grand Prix": 0.40,
    "United States Grand Prix": 0.40,
    "British Grand Prix": 0.40,
    "Belgian Grand Prix": 0.45,
    "Mexico City Grand Prix": 0.45,
    "São Paulo Grand Prix": 0.50,
    "Chinese Grand Prix": 0.50,
    "Abu Dhabi Grand Prix": 0.60
}



def get_track_features(race_name: str):

    if race_name not in TRACK_TYPE:
        print(f"⚠️ Unknown track: {race_name}")

    track_type = TRACK_TYPE.get(race_name, 0)
    overtaking = OVERTAKING_DIFFICULTY.get(race_name, 0.5)

    # Madrid special case
    if "Madrid" in race_name:
        track_type = 1
        overtaking = 0.70

    return {
        "track_type": track_type,
        "overtaking_difficulty": overtaking
    }

def build_track_dataframe(race_name: str, drivers: list):

    track_info = get_track_features(race_name)

    df = pd.DataFrame({
        "driver": drivers,
        "track_type": track_info["track_type"],
        "overtaking_difficulty": track_info["overtaking_difficulty"]
    })

    return df