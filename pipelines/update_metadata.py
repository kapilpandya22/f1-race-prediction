import os
import glob
import pandas as pd    


TRACK_METADATA_PATH = "data/golden/dashboard/track_metadata.csv"
WEATHER_PATH = "data/golden/dashboard/weather.csv"


# =====================================
# TRACK METADATA
# =====================================

TRACK_METADATA = {

    "Australian Grand Prix": {
        "country": "Australia",
        "circuit": "Albert Park Circuit",
        "track_length_km": 5.278,
        "laps": 58,
        "race_distance_km": 306.124,
        "track_type": "Street",
        "overtaking_difficulty": "Medium",
        "turns": 14
    },

    "Chinese Grand Prix": {
        "country": "China",
        "circuit": "Shanghai International Circuit",
        "track_length_km": 5.451,
        "laps": 56,
        "race_distance_km": 305.066,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 16
    },

    "Japanese Grand Prix": {
        "country": "Japan",
        "circuit": "Suzuka Circuit",
        "track_length_km": 5.807,
        "laps": 53,
        "race_distance_km": 307.471,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 18
    },

    "Miami Grand Prix": {
        "country": "United States",
        "circuit": "Miami International Autodrome",
        "track_length_km": 5.412,
        "laps": 57,
        "race_distance_km": 308.326,
        "track_type": "Street",
        "overtaking_difficulty": "Medium",
        "turns": 19
    },

    "Canadian Grand Prix": {
        "country": "Canada",
        "circuit": "Circuit Gilles Villeneuve",
        "track_length_km": 4.361,
        "laps": 70,
        "race_distance_km": 305.270,
        "track_type": "Permanent",
        "overtaking_difficulty": "Easy",
        "turns": 14
    },

    "Monaco Grand Prix": {
        "country": "Monaco",
        "circuit": "Circuit de Monaco",
        "track_length_km": 3.337,
        "laps": 78,
        "race_distance_km": 260.286,
        "track_type": "Street",
        "overtaking_difficulty": "Very Hard",
        "turns": 19
    },

    "Barcelona Grand Prix": {
        "country": "Spain",
        "circuit": "Circuit de Barcelona-Catalunya",
        "track_length_km": 4.657,
        "laps": 66,
        "race_distance_km": 307.236,
        "track_type": "Permanent",
        "overtaking_difficulty": "Hard",
        "turns": 14
    },

    "Austrian Grand Prix": {
        "country": "Austria",
        "circuit": "Red Bull Ring",
        "track_length_km": 4.318,
        "laps": 71,
        "race_distance_km": 306.452,
        "track_type": "Permanent",
        "overtaking_difficulty": "Easy",
        "turns": 10
    },

    "Emilia Romagna Grand Prix": {
        "country": "Italy",
        "circuit": "Autodromo Enzo e Dino Ferrari",
        "track_length_km": 4.909,
        "laps": 63,
        "race_distance_km": 309.049,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 19
    },

    "British Grand Prix": {
        "country": "United Kingdom",
        "circuit": "Silverstone Circuit",
        "track_length_km": 5.891,
        "laps": 52,
        "race_distance_km": 306.198,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 18
    },

    "Belgian Grand Prix": {
        "country": "Belgium",
        "circuit": "Spa-Francorchamps",
        "track_length_km": 7.004,
        "laps": 44,
        "race_distance_km": 308.052,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 19
    },

    "Hungarian Grand Prix": {
        "country": "Hungary",
        "circuit": "Hungaroring",
        "track_length_km": 4.381,
        "laps": 70,
        "race_distance_km": 306.630,
        "track_type": "Permanent",
        "overtaking_difficulty": "Very Hard",
        "turns": 14
    },

    "Dutch Grand Prix": {
        "country": "Netherlands",
        "circuit": "Circuit Zandvoort",
        "track_length_km": 4.259,
        "laps": 72,
        "race_distance_km": 306.648,
        "track_type": "Permanent",
        "overtaking_difficulty": "Hard",
        "turns": 14
    },

    "Italian Grand Prix": {
        "country": "Italy",
        "circuit": "Monza",
        "track_length_km": 5.793,
        "laps": 53,
        "race_distance_km": 306.720,
        "track_type": "Permanent",
        "overtaking_difficulty": "Easy",
        "turns": 11
    },

    "Spanish Grand Prix": {
        "country": "Spain",
        "circuit": "Madring",
        "track_length_km": 5.470,
        "laps": 56,
        "race_distance_km": 306.320,
        "track_type": "Street",
        "overtaking_difficulty": "Medium",
        "turns": 22
    },

    "Azerbaijan Grand Prix": {
        "country": "Azerbaijan",
        "circuit": "Baku City Circuit",
        "track_length_km": 6.003,
        "laps": 51,
        "race_distance_km": 306.049,
        "track_type": "Street",
        "overtaking_difficulty": "Medium",
        "turns": 20
    },

    "Singapore Grand Prix": {
        "country": "Singapore",
        "circuit": "Marina Bay Street Circuit",
        "track_length_km": 4.940,
        "laps": 62,
        "race_distance_km": 306.143,
        "track_type": "Street",
        "overtaking_difficulty": "Hard",
        "turns": 19
    },

    "United States Grand Prix": {
        "country": "United States",
        "circuit": "Circuit of the Americas",
        "track_length_km": 5.513,
        "laps": 56,
        "race_distance_km": 308.405,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 20
    },

    "Mexico City Grand Prix": {
        "country": "Mexico",
        "circuit": "Autodromo Hermanos Rodriguez",
        "track_length_km": 4.304,
        "laps": 71,
        "race_distance_km": 305.354,
        "track_type": "Permanent",
        "overtaking_difficulty": "Easy",
        "turns": 17
    },

    "São Paulo Grand Prix": {
        "country": "Brazil",
        "circuit": "Interlagos",
        "track_length_km": 4.309,
        "laps": 71,
        "race_distance_km": 305.879,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 15
    },

    "Las Vegas Grand Prix": {
        "country": "United States",
        "circuit": "Las Vegas Strip Circuit",
        "track_length_km": 6.201,
        "laps": 50,
        "race_distance_km": 309.958,
        "track_type": "Street",
        "overtaking_difficulty": "Easy",
        "turns": 17
    },

    "Qatar Grand Prix": {
        "country": "Qatar",
        "circuit": "Lusail International Circuit",
        "track_length_km": 5.419,
        "laps": 57,
        "race_distance_km": 308.611,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 16
    },

    "Abu Dhabi Grand Prix": {
        "country": "United Arab Emirates",
        "circuit": "Yas Marina Circuit",
        "track_length_km": 5.281,
        "laps": 58,
        "race_distance_km": 306.183,
        "track_type": "Permanent",
        "overtaking_difficulty": "Medium",
        "turns": 16
    }
}


# =====================================
# TRACK FILE
# =====================================

def update_track_metadata():

    os.makedirs(
        "data/golden/dashboard",
        exist_ok=True
    )

    if os.path.exists(TRACK_METADATA_PATH):

        existing = pd.read_csv(
            TRACK_METADATA_PATH
        )

        existing_races = set(
            existing["race"]
        )

    else:

        existing = pd.DataFrame()

        existing_races = set()

    rows = []

    for race, info in TRACK_METADATA.items():

        if race in existing_races:
            continue

        rows.append({

            "race": race,
            "country": info["country"],
            "circuit": info["circuit"],
            "track_length_km": info["track_length_km"],
            "laps": info["laps"],
            "race_distance_km": info["race_distance_km"],
            "track_type": info["track_type"],
            "overtaking_difficulty": info["overtaking_difficulty"],
            "turns": info["turns"]
        })

    if len(rows) == 0:

        print("✔ No new track metadata")

        return

    new_df = pd.DataFrame(rows)

    final_df = pd.concat(
        [existing, new_df],
        ignore_index=True
    )

    final_df.to_csv(
        TRACK_METADATA_PATH,
        index=False
    )

    print(
        f"✅ Added {len(rows)} track records"
    )

# =====================================
# WEATHER FILE
# =====================================

def update_weather_metadata():

    os.makedirs(
        "data/golden/dashboard",
        exist_ok=True
    )

    if os.path.exists(WEATHER_PATH):

        existing = pd.read_csv(
            WEATHER_PATH
        )

    else:

        existing = pd.DataFrame(columns=[

            "season",
            "round",
            "race",
            "weather_type",
            "temperature",
            "humidity",
            "wind_speed",
            "rain_probability"
        ])

    existing_keys = set(

        zip(
            existing["season"],
            existing["race"]
        )

    ) if len(existing) > 0 else set()

    rows = []

    golden_folder = "data/golden"

    for file in os.listdir(golden_folder):

        if not file.endswith("_R.csv"):
            continue

        race_df = pd.read_csv(
            os.path.join(
                golden_folder,
                file
            )
        )

        season = int(
            race_df["season"].iloc[0]
        )

        race = race_df["race"].iloc[0]

        key = (season, race)

        if key in existing_keys:
            continue

        rows.append({

            "season": season,
            "round": race_df["round"].iloc[0],
            "race": race,

            # placeholder values
            "weather_type": "Dry",
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "rain_probability": None
        })

    if len(rows) == 0:

        print("✔ No new weather rows")

        return

    new_df = pd.DataFrame(rows)

    final_df = pd.concat(
        [existing, new_df],
        ignore_index=True
    )

    final_df.to_csv(
        WEATHER_PATH,
        index=False
    )

    print(
        f"✅ Added {len(rows)} weather rows"
    )
