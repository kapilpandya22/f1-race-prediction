# agentic_tools/analytics_rag.py

import pandas as pd
from pathlib import Path


class AnalyticsRAG:

    def __init__(self):

        base = (
            Path(__file__)
            .resolve()
            .parent
            .parent
            / "/Users/paridhishukla/Downloads/f1-ml-project 2/data/golden"
            / "dashboard"
        )

        self.driver_race_stats = pd.read_csv(
            base / "driver_race_stats.csv"
        )

        self.driver_season_stats = pd.read_csv(
            base / "driver_season_stats.csv"
        )

        self.driver_standings = pd.read_csv(
            base / "driver_standings.csv"
        )

        self.team_season_stats = pd.read_csv(
            base / "team_season_stats.csv"
        )

        self.constructor_standings = pd.read_csv(
            base / "constructor_standings.csv"
        )

    # ---------------------------------
    # Driver Context
    # ---------------------------------

    def get_driver_context(
        self,
        driver
    ):

        season_stats = (
            self.driver_season_stats[
                self.driver_season_stats["driver"] == driver
            ]
        )

        race_history = (
            self.driver_race_stats[
                self.driver_race_stats["driver"] == driver
            ]
            .sort_values("round")
        )

        standing = (
            self.driver_standings[
                self.driver_standings["driver"] == driver
            ]
        )

        return f"""
DRIVER STANDINGS:

{standing.to_dict('records')}

DRIVER SEASON STATS:

{season_stats.to_dict('records')}

DRIVER RACE HISTORY:

{race_history.to_dict('records')}
"""

    # ---------------------------------
    # Team Context
    # ---------------------------------

    def get_team_context(
        self,
        team
    ):

        stats = (
            self.team_season_stats[
                self.team_season_stats["team"] == team
            ]
        )

        standing = (
            self.constructor_standings[
                self.constructor_standings["team"] == team
            ]
        )

        return f"""
CONSTRUCTOR STANDINGS:

{standing.to_dict('records')}

TEAM SEASON STATS:

{stats.to_dict('records')}
"""

    # ---------------------------------
    # Race Context
    # ---------------------------------

    def get_race_context(
        self,
        race
    ):

        race_results = (
            self.driver_race_stats[
                self.driver_race_stats["race"] == race
            ]
            .sort_values("position")
        )

        return f"""
RACE RESULTS:

{race_results.to_dict('records')}
"""

    # ---------------------------------
    # Driver Comparison
    # ---------------------------------

    def compare_drivers_context(
        self,
        driver1,
        driver2
    ):

        d1 = (
            self.driver_season_stats[
                self.driver_season_stats["driver"] == driver1
            ]
        )

        d2 = (
            self.driver_season_stats[
                self.driver_season_stats["driver"] == driver2
            ]
        )

        return f"""
DRIVER 1:

{d1.to_dict('records')}

DRIVER 2:

{d2.to_dict('records')}
"""

    # ---------------------------------
    # Team Comparison
    # ---------------------------------

    def compare_teams_context(
        self,
        team1,
        team2
    ):

        t1 = (
            self.team_season_stats[
                self.team_season_stats["team"] == team1
            ]
        )

        t2 = (
            self.team_season_stats[
                self.team_season_stats["team"] == team2
            ]
        )

        return f"""
TEAM 1:

{t1.to_dict('records')}

TEAM 2:

{t2.to_dict('records')}
"""

    # ---------------------------------
    # Championship Context
    # ---------------------------------

    def get_standings_context(
        self
    ):

        return f"""
DRIVER STANDINGS:

{self.driver_standings.to_dict('records')}

CONSTRUCTOR STANDINGS:

{self.constructor_standings.to_dict('records')}
"""

    # ---------------------------------
    # Generic Analytics Retrieval
    # ---------------------------------

    def get_general_context(
        self,
        driver=None,
        team=None,
        race=None
    ):

        context = ""

        if driver:

            context += (
                self.get_driver_context(
                    driver
                )
            )

        if team:

            context += (
                self.get_team_context(
                    team
                )
            )

        if race:

            context += (
                self.get_race_context(
                    race
                )
            )

        context += (
            self.get_standings_context()
        )

        return context