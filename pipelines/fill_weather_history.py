import requests
import pandas as pd
from datetime import datetime

WEATHER_PATH = "data/golden/dashboard/weather.csv"


TRACK_COORDS = {

    "Australian Grand Prix": (-37.8497, 144.9680),
    "Chinese Grand Prix": (31.3389, 121.2197),
    "Japanese Grand Prix": (34.8431, 136.5410),
    "Miami Grand Prix": (25.9581, -80.2389),
    "Canadian Grand Prix": (45.5006, -73.5228),
    "Monaco Grand Prix": (43.7347, 7.4206),
    "Spanish Grand Prix": (41.5700, 2.2611),
    "Austrian Grand Prix": (47.2197, 14.7647),
    "British Grand Prix": (52.0786, -1.0169),
    "Belgian Grand Prix": (50.4372, 5.9714),
    "Hungarian Grand Prix": (47.5789, 19.2486),
    "Dutch Grand Prix": (52.3888, 4.5409),
    "Italian Grand Prix": (45.6156, 9.2811),
    "Spanish Grand Prix (Madrid)": (40.3723, -3.6197),
    "Azerbaijan Grand Prix": (40.3725, 49.8533),
    "Singapore Grand Prix": (1.2914, 103.8640),
    "United States Grand Prix": (30.1328, -97.6411),
    "Mexican Grand Prix": (19.4042, -99.0907),
    "Brazilian Grand Prix": (-23.7036, -46.6997),
    "Las Vegas Grand Prix": (36.1147, -115.1728),
    "Qatar Grand Prix": (25.4894, 51.4542),
    "Abu Dhabi Grand Prix": (24.4672, 54.6031)
}


RACE_DATES = {

    "Australian Grand Prix": "2026-03-08",
    "Chinese Grand Prix": "2026-03-15",
    "Japanese Grand Prix": "2026-03-29",
    "Miami Grand Prix": "2026-05-03",
    "Canadian Grand Prix": "2026-05-24",
    "Monaco Grand Prix": "2026-06-07",
    "Spanish Grand Prix": "2026-06-14",
    "Austrian Grand Prix": "2026-06-28",
    "British Grand Prix": "2026-07-05",
    "Belgian Grand Prix": "2026-07-19",
    "Hungarian Grand Prix": "2026-07-26",
    "Dutch Grand Prix": "2026-08-23",
    "Italian Grand Prix": "2026-09-06",
    "Spanish Grand Prix (Madrid)": "2026-09-13",
    "Azerbaijan Grand Prix": "2026-09-26",
    "Singapore Grand Prix": "2026-10-11",
    "United States Grand Prix": "2026-10-25",
    "Mexican Grand Prix": "2026-11-01",
    "Brazilian Grand Prix": "2026-11-08",
    "Las Vegas Grand Prix": "2026-11-21",
    "Qatar Grand Prix": "2026-11-29",
    "Abu Dhabi Grand Prix": "2026-12-06"
}


def classify_weather(rain_probability):

    if rain_probability >= 0.60:
        return "Wet"

    if rain_probability >= 0.20:
        return "Mixed"

    return "Dry"


def fetch_weather(race):

    lat, lon = TRACK_COORDS[race]

    date = RACE_DATES[race]

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
    )

    params = {

        "latitude": lat,
        "longitude": lon,

        "start_date": date,
        "end_date": date,

        "daily":
        "temperature_2m_mean,"
        "relative_humidity_2m_mean,"
        "wind_speed_10m_mean,"
        "precipitation_hours",

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    temperature = float(
        daily["temperature_2m_mean"][0]
    )

    humidity = float(
        daily["relative_humidity_2m_mean"][0]
    )

    wind_speed = float(
        daily["wind_speed_10m_mean"][0]
    )

    precip_hours = float(
        daily["precipitation_hours"][0]
    )

    rain_probability = min(
        precip_hours / 10,
        1.0
    )

    weather_type = classify_weather(
        rain_probability
    )

    return {

        "weather_type": weather_type,

        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,

        "rain_probability":
            rain_probability
    }


def fill_weather_history():

    df = pd.read_csv(
        WEATHER_PATH
    )

    for idx, row in df.iterrows():

        if pd.notna(
            row["temperature"]
        ):
            continue

        race = row["race"]

        if race not in TRACK_COORDS:
            continue

        try:

            weather = fetch_weather(
                race
            )

            df.loc[
                idx,
                "weather_type"
            ] = weather[
                "weather_type"
            ]

            df.loc[
                idx,
                "temperature"
            ] = weather[
                "temperature"
            ]

            df.loc[
                idx,
                "humidity"
            ] = weather[
                "humidity"
            ]

            df.loc[
                idx,
                "wind_speed"
            ] = weather[
                "wind_speed"
            ]

            df.loc[
                idx,
                "rain_probability"
            ] = weather[
                "rain_probability"
            ]

            print(
                f"✅ Filled weather: "
                f"{race}"
            )

        except Exception as e:

            print(
                f"❌ Weather failed: "
                f"{race} | {e}"
            )

    df.to_csv(
        WEATHER_PATH,
        index=False
    )

    print(
        "\n✅ weather.csv updated"
    )


if __name__ == "__main__":

    fill_weather_history()