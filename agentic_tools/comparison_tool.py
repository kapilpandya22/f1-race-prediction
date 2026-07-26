from agentic_tools.driver_analytics_tool import (
    DriverAnalyticsTool
)

from agentic_tools.team_analytics_tool import (
    TeamAnalyticsTool
)


class ComparisonTool:

    def __init__(self):

        self.driver_tool = (
            DriverAnalyticsTool()
        )

        self.team_tool = (
            TeamAnalyticsTool()
        )

    # -------------------------
    # Driver Comparison
    # -------------------------

    def compare_drivers(
        self,
        driver1,
        driver2
    ):

        return {

            driver1: {

                "points":
                self.driver_tool
                .get_driver_points(
                    driver1
                )["points"],

                "wins":
                self.driver_tool
                .get_driver_wins(
                    driver1
                )["wins"],

                "podiums":
                self.driver_tool
                .get_driver_podiums(
                    driver1
                )["podiums"],

                "reliability":
                self.driver_tool
                .get_reliability(
                    driver1
                )["reliability"],

                "average_finish":
                self.driver_tool
                .get_average_finish(
                    driver1
                )["average_finish"]
            },

            driver2: {

                "points":
                self.driver_tool
                .get_driver_points(
                    driver2
                )["points"],

                "wins":
                self.driver_tool
                .get_driver_wins(
                    driver2
                )["wins"],

                "podiums":
                self.driver_tool
                .get_driver_podiums(
                    driver2
                )["podiums"],

                "reliability":
                self.driver_tool
                .get_reliability(
                    driver2
                )["reliability"],

                "average_finish":
                self.driver_tool
                .get_average_finish(
                    driver2
                )["average_finish"]
            }
        }

    # -------------------------
    # Team Comparison
    # -------------------------

    def compare_teams(
        self,
        team1,
        team2
    ):

        return {

            team1: {

                "points":
                self.team_tool
                .get_team_points(
                    team1
                )["points"],

                "wins":
                self.team_tool
                .get_team_wins(
                    team1
                )["wins"],

                "podiums":
                self.team_tool
                .get_team_podiums(
                    team1
                )["podiums"],

                "reliability":
                self.team_tool
                .get_team_reliability(
                    team1
                )["reliability"],

                "average_finish":
                self.team_tool
                .get_team_average_finish(
                    team1
                )["average_finish"]
            },

            team2: {

                "points":
                self.team_tool
                .get_team_points(
                    team2
                )["points"],

                "wins":
                self.team_tool
                .get_team_wins(
                    team2
                )["wins"],

                "podiums":
                self.team_tool
                .get_team_podiums(
                    team2
                )["podiums"],

                "reliability":
                self.team_tool
                .get_team_reliability(
                    team2
                )["reliability"],

                "average_finish":
                self.team_tool
                .get_team_average_finish(
                    team2
                )["average_finish"]
            }
        }