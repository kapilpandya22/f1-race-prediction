import requests
import pandas as pd
import json
import os
import time

TRACK_INFO = {

    "Australian Grand Prix": {
        "coords": (-37.8497, 144.9680),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Chinese Grand Prix": {
        "coords": (31.3389, 121.2197),
        "race_hour_local": 15,
        "quali_hour_local": 15,
        "sprint_hour_local": 11
    },

    "Japanese Grand Prix": {
        "coords": (34.8431, 136.5410),
        "race_hour_local": 14,
        "quali_hour_local": 15
    },

    "Bahrain Grand Prix": {
        "coords": (26.0325, 50.5106),
        "race_hour_local": 18,
        "quali_hour_local": 19
    },

    "Saudi Arabian Grand Prix": {
        "coords": (21.6319, 39.1044),
        "race_hour_local": 20,
        "quali_hour_local": 20
    },

    "Miami Grand Prix": {
        "coords": (25.9581, -80.2389),
        "race_hour_local": 16,
        "quali_hour_local": 16,
        "sprint_hour_local": 12
    },

    "Canadian Grand Prix": {
        "coords": (45.5006, -73.5228),
        "race_hour_local": 16,
        "quali_hour_local": 16,
        "sprint_hour_local": 12
    },

    "Monaco Grand Prix": {
        "coords": (43.7347, 7.4206),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Spanish Grand Prix": {
        "coords": (41.5700, 2.2611),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Austrian Grand Prix": {
        "coords": (47.2197, 14.7647),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "British Grand Prix": {
        "coords": (52.0786, -1.0169),
        "race_hour_local": 15,
        "quali_hour_local": 16,
        "sprint_hour_local": 12
    },

    "Belgian Grand Prix": {
        "coords": (50.4372, 5.9714),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Hungarian Grand Prix": {
        "coords": (47.5789, 19.2486),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Dutch Grand Prix": {
        "coords": (52.3888, 4.5409),
        "race_hour_local": 15,
        "quali_hour_local": 16,
        "sprint_hour_local": 12
    },

    "Italian Grand Prix": {
        "coords": (45.6156, 9.2811),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Spanish Grand Prix (Madrid)": {
        "coords": (40.3723, -3.6197),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Azerbaijan Grand Prix": {
        "coords": (40.3725, 49.8533),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Singapore Grand Prix": {
        "coords": (1.2914, 103.8640),
        "race_hour_local": 20,
        "quali_hour_local": 21,
        "sprint_hour_local": 17
    },

    "United States Grand Prix": {
        "coords": (30.1328, -97.6411),
        "race_hour_local": 15,
        "quali_hour_local": 16
    },

    "Mexico City Grand Prix": {
        "coords": (19.4042, -99.0907),
        "race_hour_local": 14,
        "quali_hour_local": 15
    },

    "Brazilian Grand Prix": {
        "coords": (-23.7036, -46.6997),
        "race_hour_local": 14,
        "quali_hour_local": 15
    },

    "Las Vegas Grand Prix": {
        "coords": (36.1147, -115.1728),
        "race_hour_local": 20,
        "quali_hour_local": 20
    },

    "Qatar Grand Prix": {
        "coords": (25.4894, 51.4542),
        "race_hour_local": 19,
        "quali_hour_local": 21
    },

    "Abu Dhabi Grand Prix": {
        "coords": (24.4672, 54.6031),
        "race_hour_local": 17,
        "quali_hour_local": 18
    },
    "Emilia Romagna Grand Prix": {
        "coords": (44.3439, 11.7167),
        "race_hour_local": 15,
        "quali_hour_local": 16
    }
}

TRACK_WEATHER_BASELINES = {

    "Australian Grand Prix": {
        "temperature": 22,
        "humidity": 60,
        "wind_speed": 18,
        "rain_probability": 0.25
    },

    "Chinese Grand Prix": {
        "temperature": 24,
        "humidity": 68,
        "wind_speed": 14,
        "rain_probability": 0.30
    },

    "Japanese Grand Prix": {
        "temperature": 18,
        "humidity": 65,
        "wind_speed": 16,
        "rain_probability": 0.35
    },

    "Bahrain Grand Prix": {
        "temperature": 30,
        "humidity": 45,
        "wind_speed": 16,
        "rain_probability": 0.05
    },

    "Saudi Arabian Grand Prix": {
        "temperature": 31,
        "humidity": 58,
        "wind_speed": 14,
        "rain_probability": 0.03
    },

    "Miami Grand Prix": {
        "temperature": 31,
        "humidity": 70,
        "wind_speed": 20,
        "rain_probability": 0.35
    },

    "Canadian Grand Prix": {
        "temperature": 23,
        "humidity": 62,
        "wind_speed": 17,
        "rain_probability": 0.40
    },

    "Monaco Grand Prix": {
        "temperature": 24,
        "humidity": 63,
        "wind_speed": 11,
        "rain_probability": 0.20
    },

    "Spanish Grand Prix": {
        "temperature": 27,
        "humidity": 55,
        "wind_speed": 15,
        "rain_probability": 0.15
    },

    "Austrian Grand Prix": {
        "temperature": 23,
        "humidity": 60,
        "wind_speed": 14,
        "rain_probability": 0.35
    },

    "British Grand Prix": {
        "temperature": 19,
        "humidity": 72,
        "wind_speed": 22,
        "rain_probability": 0.40
    },

    "Belgian Grand Prix": {
        "temperature": 20,
        "humidity": 78,
        "wind_speed": 18,
        "rain_probability": 0.55
    },

    "Hungarian Grand Prix": {
        "temperature": 29,
        "humidity": 52,
        "wind_speed": 12,
        "rain_probability": 0.20
    },

    "Dutch Grand Prix": {
        "temperature": 21,
        "humidity": 75,
        "wind_speed": 24,
        "rain_probability": 0.40
    },

    "Italian Grand Prix": {
        "temperature": 28,
        "humidity": 58,
        "wind_speed": 13,
        "rain_probability": 0.18
    },

    "Spanish Grand Prix (Madrid)": {
        "temperature": 31,
        "humidity": 40,
        "wind_speed": 11,
        "rain_probability": 0.10
    },

    "Azerbaijan Grand Prix": {
        "temperature": 27,
        "humidity": 50,
        "wind_speed": 28,
        "rain_probability": 0.12
    },

    "Singapore Grand Prix": {
        "temperature": 30,
        "humidity": 82,
        "wind_speed": 10,
        "rain_probability": 0.55
    },

    "United States Grand Prix": {
        "temperature": 29,
        "humidity": 58,
        "wind_speed": 16,
        "rain_probability": 0.25
    },

    "Mexico City Grand Prix": {
        "temperature": 22,
        "humidity": 48,
        "wind_speed": 14,
        "rain_probability": 0.18
    },

    "Brazilian Grand Prix": {
        "temperature": 26,
        "humidity": 72,
        "wind_speed": 15,
        "rain_probability": 0.45
    },

    "Las Vegas Grand Prix": {
        "temperature": 14,
        "humidity": 28,
        "wind_speed": 12,
        "rain_probability": 0.03
    },

    "Qatar Grand Prix": {
        "temperature": 32,
        "humidity": 60,
        "wind_speed": 17,
        "rain_probability": 0.02
    },

    "Abu Dhabi Grand Prix": {
        "temperature": 29,
        "humidity": 55,
        "wind_speed": 14,
        "rain_probability": 0.02
    },

    "Emilia Romagna Grand Prix": {
        "temperature": 23,
        "humidity": 65,
        "wind_speed": 13,
        "rain_probability": 0.28
    }
}

def fetch_weather_forecast(race_name):

    # ---------------------------
    # VALIDATE TRACK
    # ---------------------------
    if race_name not in TRACK_INFO:

        raise RuntimeError(
            f"Missing TRACK_INFO for {race_name}"
        )

    # ---------------------------
    # TRACK METADATA
    # ---------------------------
    track_info = TRACK_INFO[race_name]

    if "coords" not in track_info:

        raise RuntimeError(
            f"Missing coords for {race_name}"
        )

    if "race_hour_local" not in track_info:

        raise RuntimeError(
            f"Missing race hour for {race_name}"
        )

    lat, lon = track_info["coords"]

    race_hour = track_info["race_hour_local"]
    
    weather_dir = "outputs/predictions/weather"

    os.makedirs(weather_dir, exist_ok=True)
    
    race_clean = (
        race_name
        .replace(" ", "_")
        .replace("/", "_")
    )

    weather_path = (
        f"{weather_dir}/"
        f"2026_{race_clean}_weather.json"
    )

    # ---------------------------
    # LOAD CACHED WEATHER
    # ---------------------------
    CACHE_HOURS = 3

    if os.path.exists(weather_path):

        cache_age = (
            time.time()
            - os.path.getmtime(weather_path)
        )

        if cache_age < CACHE_HOURS * 3600:

            print(
                f"📦 Loading cached weather: "
                f"{weather_path}"
            )

            with open(weather_path, "r") as f:

                return json.load(f)

        else:

            print(
                f"♻️ Weather cache expired "
                f"for {race_name}"
            )
            
    # ---------------------------
    # API CONFIG
    # ---------------------------
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": (
            "precipitation_probability,"
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "forecast_days": 1,
        "timezone": "auto"
    }

    # ---------------------------
    # API REQUEST
    # ---------------------------
    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"Weather API failed for "
            f"{race_name}: {e}"
        )
    
    # ---------------------------
    # VALIDATE RESPONSE
    # ---------------------------
    if "hourly" not in data:

        raise RuntimeError(
            f"Missing hourly weather data "
            f"for {race_name}"
        )

    hourly = data["hourly"]

    if "time" not in hourly:

        raise RuntimeError(
            f"Missing hourly timestamps "
            f"for {race_name}"
        )

    required_cols = [
        "precipitation_probability",
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m"
    ]

    for col in required_cols:

        if col not in hourly:

            raise RuntimeError(
                f"Missing {col} "
                f"for {race_name}"
            )

    times = hourly["time"]

    # ---------------------------
    # FIND RACE HOUR
    # ---------------------------
    race_idx = None

    for i, t in enumerate(times):

        hour = int(
            t.split("T")[1].split(":")[0]
        )

        if hour == race_hour:
            race_idx = i
            break

    if race_idx is None:

        raise RuntimeError(
            f"Race hour {race_hour} "
            f"not found in weather data "
            f"for {race_name}"
        )

    # ---------------------------
    # WEATHER WINDOW
    # ---------------------------
    window = range(
        max(0, race_idx - 2),
        min(len(times), race_idx + 3)
    )

    rain_probs = [
        hourly[
            "precipitation_probability"
        ][i]
        for i in window
    ]

    temps = [
        hourly["temperature_2m"][i]
        for i in window
    ]

    humidity = [
        hourly["relative_humidity_2m"][i]
        for i in window
    ]

    wind = [
        hourly["wind_speed_10m"][i]
        for i in window
    ]
    
    # ---------------------------
    # VALIDATE WEATHER ARRAYS
    # ---------------------------
    required_weather = {
        "rain_probs": rain_probs,
        "temps": temps,
        "humidity": humidity,
        "wind": wind
    }

    for name, values in required_weather.items():

        if len(values) == 0:

            raise RuntimeError(
                f"Empty weather array: {name} "
                f"for {race_name}"
            )

        if any(v is None for v in values):

            raise RuntimeError(
                f"Missing values in {name} "
                f"for {race_name}"
            )
            
        
    if len(rain_probs) == 0:

        raise RuntimeError(
            f"No rain probabilities "
            f"for {race_name}"
        )
        
    avg_temp = (
        sum(temps) / len(temps)
    )

    avg_humidity = (
        sum(humidity) / len(humidity)
    )

    avg_wind = (
        sum(wind) / len(wind)
    )
    # ---------------------------
    # FEATURES
    # ---------------------------
    rain_probability = (max(rain_probs) / 100)

    wet_track_flag = 1 if max(rain_probs) >= 60 else 0
    
    # ---------------------------
    # WEATHER ANOMALIES
    # ---------------------------
    if race_name not in TRACK_WEATHER_BASELINES:

        raise RuntimeError(
            f"Missing weather baseline for {race_name}"
        )

    baseline = TRACK_WEATHER_BASELINES[race_name]

    temperature_vs_baseline = (
        avg_temp
        - baseline["temperature"]
    )

    humidity_vs_baseline = (
        avg_humidity
        - baseline["humidity"]
    )

    wind_speed_vs_baseline = (
        avg_wind
        - baseline["wind_speed"]
    )

    rain_probability_vs_baseline = (
        rain_probability
        - baseline["rain_probability"]
    )

    # ---------------------------
    # DEBUG LOG
    # ---------------------------
    print(
        f"\n🌧️ WEATHER SUMMARY | {race_name}\n"

        f"Rain Probability: {rain_probability:.2f}\n"
        f"Wet Track Flag: {wet_track_flag}\n"

        f"Temperature: {avg_temp:.1f}C "
        f"(vs baseline: {temperature_vs_baseline:+.1f}C)\n"

        f"Humidity: {avg_humidity:.1f}% "
        f"(vs baseline: {humidity_vs_baseline:+.1f}%)\n"

        f"Wind Speed: {avg_wind:.1f} km/h "
        f"(vs baseline: {wind_speed_vs_baseline:+.1f} km/h)\n"

        f"Rain Probability vs Baseline: "
        f"{rain_probability_vs_baseline:+.2f}\n"
    )

    # ---------------------------
    # VALIDATE FINAL FEATURES
    # ---------------------------
    final_features = {

        "rain_probability": rain_probability,
        "temperature": avg_temp,
        "humidity": avg_humidity,
        "wind_speed": avg_wind,

        "temperature_vs_baseline": temperature_vs_baseline,
        "humidity_vs_baseline": humidity_vs_baseline,
        "wind_speed_vs_baseline": wind_speed_vs_baseline,
        "rain_probability_vs_baseline": rain_probability_vs_baseline
    }

    for name, value in final_features.items():

        if value is None:

            raise RuntimeError(
                f"{name} is None "
                f"for {race_name}"
            )

        if pd.isna(value):

            raise RuntimeError(
                f"{name} is NaN "
                f"for {race_name}"
            )

    weather_data = {

        "rain_probability": rain_probability,
        "wet_track_flag": wet_track_flag,
 
        "temperature": avg_temp,
        "humidity": avg_humidity,
        "wind_speed": avg_wind,

        "temperature_vs_baseline": temperature_vs_baseline,
        "humidity_vs_baseline": humidity_vs_baseline,
        "wind_speed_vs_baseline": wind_speed_vs_baseline,
        "rain_probability_vs_baseline": rain_probability_vs_baseline
    }

    # ---------------------------
    # SAVE WEATHER CACHE
    # ---------------------------
    with open(weather_path, "w") as f:

        json.dump(
            weather_data,
            f,
            indent=4
        )

    print(
        f"💾 Saved weather cache → "
        f"{weather_path}"
    )

    return weather_data



def build_weather_features(
    race_name: str,
    drivers: list
):

    weather = fetch_weather_forecast(race_name)

    df = pd.DataFrame({

        "driver": drivers,

        "rain_probability": [
            weather["rain_probability"]
        ] * len(drivers),

        "wet_track_flag": [
            weather["wet_track_flag"]
        ] * len(drivers),

        "temperature": [
            weather["temperature"]
        ] * len(drivers),

        "humidity": [
            weather["humidity"]
        ] * len(drivers),

        "wind_speed": [
            weather["wind_speed"]
        ] * len(drivers),
        
        "temperature_vs_baseline": [
            weather["temperature_vs_baseline"]
        ] * len(drivers),

        "humidity_vs_baseline": [
            weather["humidity_vs_baseline"]
        ] * len(drivers),

        "wind_speed_vs_baseline": [
            weather["wind_speed_vs_baseline"]
        ] * len(drivers),

        "rain_probability_vs_baseline": [
            weather["rain_probability_vs_baseline"]
        ] * len(drivers)
    })

    return df