from datetime import datetime

def get_race_lists(schedule):

    today = datetime.today().date()

    prediction_races = []
    metrics_races = []

    for r in schedule:
        quali = datetime.strptime(r["quali_date"], "%Y-%m-%d").date()
        race = datetime.strptime(r["race_date"], "%Y-%m-%d").date()

        if today >= quali:
            prediction_races.append(r["race"])

        if today >= race:
            metrics_races.append(r["race"])

    return prediction_races, metrics_races