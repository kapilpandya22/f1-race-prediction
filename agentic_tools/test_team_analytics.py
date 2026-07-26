from team_analytics_tool import (
    TeamAnalyticsTool
)

tool = TeamAnalyticsTool()

print(
    tool.get_constructor_leader()
)

print(
    tool.get_most_wins_team()
)

print(
    tool.get_most_podiums_team()
)

print(
    tool.get_most_reliable_team()
)

print(
    tool.get_team_points(
        "Mercedes"
    )
)

print(
    tool.get_team_reliability(
        "Mercedes"
    )
)