DRIVER_MAP = {
    "VER": "Max Verstappen",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "LEC": "Charles Leclerc",
    "HAM": "Lewis Hamilton",
    "RUS": "George Russell",
    "ANT": "Kimi Antonelli",
    "HAD": "Isack Hadjar",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "GAS": "Pierre Gasly",
    "OCO": "Esteban Ocon",
    "ALB": "Alexander Albon",
    "SAI": "Carlos Sainz",
    "TSU": "Yuki Tsunoda",
    "HUL": "Nico Hulkenberg",
    "BEA": "Oliver Bearman",
    "BOR": "Gabriel Bortoleto",
    "DOO": "Jack Doohan",
    "LAW": "Liam Lawson",
    "COL": "Franco Colapinto"
}

RACE_MAP = {
    "Australian Grand Prix": "Melbourne",
    "Chinese Grand Prix": "Shanghai",
    "Japanese Grand Prix": "Suzuka",
    "Bahrain Grand Prix": "Sakhir",
    "Saudi Arabian Grand Prix": "Jeddah",
    "Miami Grand Prix": "Miami",
    "Emilia Romagna Grand Prix": "Imola",
    "Monaco Grand Prix": "Monte Carlo",
    "Spanish Grand Prix": "Barcelona",
    "Canadian Grand Prix": "Montreal",
    "Austrian Grand Prix": "Spielberg",
    "British Grand Prix": "Silverstone",
    "Belgian Grand Prix": "Spa-Francorchamps",
    "Hungarian Grand Prix": "Budapest",
    "Dutch Grand Prix": "Zandvoort",
    "Italian Grand Prix": "Monza",
    "Azerbaijan Grand Prix": "Baku",
    "Singapore Grand Prix": "Singapore",
    "United States Grand Prix": "Austin",
    "Mexico City Grand Prix": "Mexico City",
    "São Paulo Grand Prix": "Interlagos",
    "Las Vegas Grand Prix": "Las Vegas",
    "Qatar Grand Prix": "Lusail",
    "Abu Dhabi Grand Prix": "Yas Marina"
}

AVAILABLE_MODELS = [
    "logistic",
    "random_forest",
    "xgboost"
]


DRIVER_NAME_TO_CODE = {
    v.lower(): k
    for k, v in DRIVER_MAP.items()
}

RACE_ALIASES = {
    "australia": "Australian Grand Prix",
    "australian": "Australian Grand Prix",
    "melbourne": "Australian Grand Prix",

    "china": "Chinese Grand Prix",
    "chinese": "Chinese Grand Prix",
    "shanghai": "Chinese Grand Prix",

    "japan": "Japanese Grand Prix",
    "japanese": "Japanese Grand Prix",
    "suzuka": "Japanese Grand Prix",

    "canada": "Canadian Grand Prix",
    "canadian": "Canadian Grand Prix",
    "montreal": "Canadian Grand Prix",

    "miami": "Miami Grand Prix"
}
def resolve_driver(driver_name):

    if not driver_name:
        return None

    driver_name = (
        driver_name
        .strip()
        .lower()
    )

    # exact full name
    if driver_name in DRIVER_NAME_TO_CODE:
        return DRIVER_NAME_TO_CODE[
            driver_name
        ]

    # code directly
    upper = driver_name.upper()

    if upper in DRIVER_MAP:
        return upper

    # partial surname match
    for code, full_name in DRIVER_MAP.items():

        if (
            driver_name
            in full_name.lower()
        ):
            return code

    return None


def resolve_race(race):

    if not race:
        return None

    return RACE_ALIASES.get(
        race.lower()
    )
def get_driver_name(driver_code):

    return DRIVER_MAP.get(
        driver_code,
        driver_code
    )


def get_race_name(alias):

    if not alias:
        return None

    return RACE_ALIASES.get(
        alias.lower(),
        alias
    )

TEAM_ALIASES = {
    "mercedes": "Mercedes",
    "ferrari": "Ferrari",
    "mclaren": "McLaren",
    "red bull": "Red Bull",
    "redbull": "Red Bull",
    "aston martin": "Aston Martin",
    "alpine": "Alpine",
    "haas": "Haas",
    "williams": "Williams",
    "sauber": "Sauber",
    "racing bulls": "Racing Bulls"
}


def resolve_team(team):

    if not team:
        return None

    return TEAM_ALIASES.get(
        team.lower()
    )