import fastf1

session = fastf1.get_session(2026, "Canadian Grand Prix", "R")
session.load()

print(session.event)
print(session.event["EventName"])
print(session.event["RoundNumber"])