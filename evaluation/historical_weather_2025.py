"""
Historical weather features for the 2025 temporal evaluation.

IMPORTANT:
    This file is evaluation-only.

It does NOT modify:
    features/weather.py
    the 2026 prediction pipeline
    the frontend

Weather source:
    Open-Meteo Previous Model Runs API

Forecast lead time:
    Approximately 24 hours before the valid weather time
    (_previous_day1)

The same weather-feature definitions used by the project are
reproduced here:
    - rain_probability
    - wet_track_flag
    - temperature
    - humidity
    - wind_speed
    - temperature_vs_baseline
    - humidity_vs_baseline
    - wind_speed_vs_baseline
    - rain_probability_vs_baseline
"""

import os
import json
import requests
import pandas as pd

from features.weather import (
    TRACK_INFO,
    TRACK_WEATHER_BASELINES,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

CACHE_DIR = "outputs/evaluation_2025/weather"

os.makedirs(CACHE_DIR, exist_ok=True)


# =============================================================================
# 2025 RACE DATES
# =============================================================================
#
# These are the 2025 race dates used by the temporal evaluation.
#
# The calendar.py file intentionally contains only race names for 2025,
# so the evaluation keeps its own date mapping rather than modifying the
# project's main calendar.
#
# =============================================================================

RACE_DATES_2025 = {

    "Australian Grand Prix":
        "2025-03-16",

    "Chinese Grand Prix":
        "2025-03-23",

    "Japanese Grand Prix":
        "2025-04-06",

    "Bahrain Grand Prix":
        "2025-04-13",

    "Saudi Arabian Grand Prix":
        "2025-04-20",

    "Miami Grand Prix":
        "2025-05-04",

    "Emilia Romagna Grand Prix":
        "2025-05-18",

    "Monaco Grand Prix":
        "2025-05-25",

    "Spanish Grand Prix":
        "2025-06-01",

    "Canadian Grand Prix":
        "2025-06-15",

    "Austrian Grand Prix":
        "2025-06-29",

    "British Grand Prix":
        "2025-07-06",

    "Belgian Grand Prix":
        "2025-07-27",

    "Hungarian Grand Prix":
        "2025-08-03",

    "Dutch Grand Prix":
        "2025-08-31",

    "Italian Grand Prix":
        "2025-09-07",

    "Azerbaijan Grand Prix":
        "2025-09-21",

    "Singapore Grand Prix":
        "2025-10-05",

    "United States Grand Prix":
        "2025-10-19",

    "Mexico City Grand Prix":
        "2025-10-26",

    "São Paulo Grand Prix":
        "2025-11-09",

    "Las Vegas Grand Prix":
        "2025-11-22",

    "Qatar Grand Prix":
        "2025-11-30",

    "Abu Dhabi Grand Prix":
        "2025-12-07",
}


# =============================================================================
# HELPERS
# =============================================================================

def _cache_path(race_name: str) -> str:

    race_clean = (
        race_name
        .replace(" ", "_")
        .replace("/", "_")
    )

    return os.path.join(
        CACHE_DIR,
        f"2025_{race_clean}_weather.json",
    )


def _validate_race(race_name: str):

    if race_name not in RACE_DATES_2025:

        raise ValueError(
            f"No 2025 race date configured for: "
            f"{race_name}"
        )

    if race_name not in TRACK_INFO:

        raise ValueError(
            f"No TRACK_INFO configured for: "
            f"{race_name}"
        )

    if race_name not in TRACK_WEATHER_BASELINES:

        raise ValueError(
            f"No weather baseline configured for: "
            f"{race_name}"
        )


# =============================================================================
# FETCH HISTORICAL FORECAST
# =============================================================================

def fetch_historical_forecast_2025(
    race_name: str,
    timeout: int = 120,
):
    """
    Retrieve archived forecast values for the 2025 race.

    The Previous Runs API exposes variables such as:

        temperature_2m

    which represent the forecast approximately 24 hours before
    the valid time.

    We request:
        - precipitation probability
        - temperature
        - relative humidity
        - wind speed

    for the complete race date.
    """

    _validate_race(race_name)

    cache_path = _cache_path(race_name)

    # -------------------------------------------------------------------------
    # CACHE
    # -------------------------------------------------------------------------

    if os.path.exists(cache_path):

        print(
            f"📦 Loading historical weather cache: "
            f"{cache_path}"
        )

        with open(
            cache_path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    # -------------------------------------------------------------------------
    # TRACK INFORMATION
    # -------------------------------------------------------------------------

    track_info = TRACK_INFO[race_name]

    lat, lon = track_info["coords"]

    race_date = RACE_DATES_2025[race_name]

    # -------------------------------------------------------------------------
    # PREVIOUS RUNS API
    # -------------------------------------------------------------------------

    url = (
        "https://previous-runs-api.open-meteo.com/v1/forecast"
    )

    params = {

        "latitude": lat,

        "longitude": lon,

        "start_date": race_date,

        "end_date": race_date,

        "hourly": (
            "precipitation_probability",
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m"
        ),

        "timezone": "auto",
    }

    print(
        f"\n🌦️ Fetching historical forecast:"
        f"\n   Race: {race_name}"
        f"\n   Date: {race_date}"
        f"\n   Lead time: approximately 24 hours"
    )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=timeout,
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        raise RuntimeError(
            f"Historical weather API failed for "
            f"{race_name}: {e}"
        )

    # -------------------------------------------------------------------------
    # VALIDATE RESPONSE
    # -------------------------------------------------------------------------

    if "hourly" not in data:

        raise RuntimeError(
            f"Historical weather response does not "
            f"contain hourly data for {race_name}."
        )

    hourly = data["hourly"]

    required = [
        "time",
        "precipitation_probability",
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
    ]

    for column in required:

        if column not in hourly:

            raise RuntimeError(
                f"Missing '{column}' in historical "
                f"weather response for {race_name}."
            )

    # -------------------------------------------------------------------------
    # SAVE RAW RESPONSE
    # -------------------------------------------------------------------------

    with open(
        cache_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
        )

    print(
        f"💾 Saved historical weather cache → "
        f"{cache_path}"
    )

    return data


# =============================================================================
# BUILD WEATHER FEATURES
# =============================================================================

def build_historical_weather_features_2025(
    race_name: str,
):
    """
    Reproduce the project's weather feature calculations using
    historical 24-hour-ahead forecast information.
    """

    _validate_race(race_name)

    track_info = TRACK_INFO[race_name]

    race_hour = track_info["race_hour_local"]

    data = fetch_historical_forecast_2025(
        race_name
    )

    hourly = data["hourly"]

    times = hourly["time"]

    rain_values = hourly[
        "precipitation_probability"
    ]

    temp_values = hourly[
        "temperature_2m"
    ]

    humidity_values = hourly[
        "relative_humidity_2m"
    ]

    wind_values = hourly[
        "wind_speed_10m"
    ]

    # -------------------------------------------------------------------------
    # CONVERT TO DATAFRAME
    # -------------------------------------------------------------------------

    weather_df = pd.DataFrame({

        "time": times,

        "rain_probability_raw": rain_values,

        "temperature": temp_values,

        "humidity": humidity_values,

        "wind_speed": wind_values,
    })

    # -------------------------------------------------------------------------
    # FIND RACE HOUR
    # -------------------------------------------------------------------------

    race_indices = []

    for i, timestamp in enumerate(
        weather_df["time"]
    ):

        try:

            hour = int(
                timestamp
                .split("T")[1]
                .split(":")[0]
            )

        except Exception:

            continue

        if hour == race_hour:

            race_indices.append(i)

    if not race_indices:

        raise RuntimeError(
            f"Race hour {race_hour}:00 was not "
            f"found for {race_name}."
        )

    race_idx = race_indices[0]

    # -------------------------------------------------------------------------
    # SAME 5-HOUR WINDOW AS PRODUCTION WEATHER CODE
    # -------------------------------------------------------------------------
    #
    # Production implementation:
    #
    #     race hour - 2
    #     race hour - 1
    #     race hour
    #     race hour + 1
    #     race hour + 2
    #
    # -------------------------------------------------------------------------

    start_idx = max(
        0,
        race_idx - 2,
    )

    end_idx = min(
        len(weather_df),
        race_idx + 3,
    )

    window = weather_df.iloc[
        start_idx:end_idx
    ].copy()

    if window.empty:

        raise RuntimeError(
            f"Weather window is empty for "
            f"{race_name}."
        )

    # -------------------------------------------------------------------------
    # VALIDATE WEATHER VALUES
    # -------------------------------------------------------------------------

    weather_columns = [
        "rain_probability_raw",
        "temperature",
        "humidity",
        "wind_speed",
    ]

    for column in weather_columns:

        if window[column].isna().any():

            raise RuntimeError(
                f"Missing historical weather values "
                f"in '{column}' for {race_name}."
            )

    # -------------------------------------------------------------------------
    # SAME CALCULATIONS AS EXISTING WEATHER PIPELINE
    # -------------------------------------------------------------------------

    rain_probability = (
        window[
            "rain_probability_raw"
        ].max()
        / 100.0
    )

    wet_track_flag = (
        1
        if window[
            "rain_probability_raw"
        ].max() >= 60
        else 0
    )

    avg_temp = (
        window["temperature"]
        .mean()
    )

    avg_humidity = (
        window["humidity"]
        .mean()
    )

    avg_wind = (
        window["wind_speed"]
        .mean()
    )

    # -------------------------------------------------------------------------
    # TRACK BASELINE
    # -------------------------------------------------------------------------

    baseline = (
        TRACK_WEATHER_BASELINES[
            race_name
        ]
    )

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

    # -------------------------------------------------------------------------
    # FINAL FEATURE DICTIONARY
    # -------------------------------------------------------------------------

    weather_features = {

        "rain_probability":
            float(rain_probability),

        "wet_track_flag":
            int(wet_track_flag),

        "temperature":
            float(avg_temp),

        "humidity":
            float(avg_humidity),

        "wind_speed":
            float(avg_wind),

        "temperature_vs_baseline":
            float(temperature_vs_baseline),

        "humidity_vs_baseline":
            float(humidity_vs_baseline),

        "wind_speed_vs_baseline":
            float(wind_speed_vs_baseline),

        "rain_probability_vs_baseline":
            float(
                rain_probability_vs_baseline
            ),
    }

    # -------------------------------------------------------------------------
    # FINAL VALIDATION
    # -------------------------------------------------------------------------

    for name, value in weather_features.items():

        if value is None:

            raise RuntimeError(
                f"Historical weather feature "
                f"'{name}' is None for {race_name}."
            )

        if pd.isna(value):

            raise RuntimeError(
                f"Historical weather feature "
                f"'{name}' is NaN for {race_name}."
            )

    # -------------------------------------------------------------------------
    # DEBUG
    # -------------------------------------------------------------------------

    print(
        f"\n🌦️ HISTORICAL WEATHER SUMMARY | "
        f"{race_name}"
    )

    print(
        f"Forecast lead time: ~24 hours"
    )

    print(
        f"Race date: "
        f"{RACE_DATES_2025[race_name]}"
    )

    print(
        f"Race hour: "
        f"{race_hour}:00 local"
    )

    print(
        f"Window: "
        f"{window['time'].iloc[0]} "
        f"→ "
        f"{window['time'].iloc[-1]}"
    )

    print(
        f"Rain Probability: "
        f"{rain_probability:.2f}"
    )

    print(
        f"Wet Track Flag: "
        f"{wet_track_flag}"
    )

    print(
        f"Temperature: "
        f"{avg_temp:.1f} C "
        f"(vs baseline: "
        f"{temperature_vs_baseline:+.1f} C)"
    )

    print(
        f"Humidity: "
        f"{avg_humidity:.1f}% "
        f"(vs baseline: "
        f"{humidity_vs_baseline:+.1f}%)"
    )

    print(
        f"Wind Speed: "
        f"{avg_wind:.1f} km/h "
        f"(vs baseline: "
        f"{wind_speed_vs_baseline:+.1f} km/h)"
    )

    print(
        f"Rain Probability vs Baseline: "
        f"{rain_probability_vs_baseline:+.2f}"
    )

    return weather_features


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def get_historical_weather_2025(
    race_name: str,
):
    """
    Public function used by temporal_2025.py.
    """

    return build_historical_weather_features_2025(
        race_name
    )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":

    test_race = "Spanish Grand Prix"

    print(
        "\nTesting historical weather for:"
        f" {test_race}"
    )

    result = (
        get_historical_weather_2025(
            test_race
        )
    )

    print("\nResult:")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

