def get_previous_races(schedule, target_race):

    prev = []

    for r in schedule:

        # 🔥 HANDLE BOTH TYPES
        if isinstance(r, dict):
            race_name = r["race"]
        else:
            race_name = r

        if race_name == target_race:
            break

        prev.append(race_name)

    return prev