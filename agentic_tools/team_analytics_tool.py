import pandas as pd
from pathlib import Path


class TeamAnalyticsTool:

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        / "/Users/paridhishukla/Downloads/f1-ml-project 2/data/golden"
    )

    def load_season_data(
        self,
        season=2026
    ):

        files = list(
            self.BASE_DIR.glob(
                f"{season}_*_R.csv"
            )
        )

        if not files:
            raise FileNotFoundError(
                f"No race files found for {season}"
            )

        dfs = [
            pd.read_csv(f)
            for f in files
        ]

        return pd.concat(
            dfs,
            ignore_index=True
        )

    # -------------------------
    # Constructors Championship
    # -------------------------

    def get_constructor_standings(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        standings = (
            df.groupby("team")
            ["points"]
            .sum()
            .reset_index()
            .sort_values(
                "points",
                ascending=False
            )
        )

        standings["rank"] = (
            range(
                1,
                len(standings) + 1
            )
        )

        return standings.to_dict(
            "records"
        )

    def get_constructor_leader(
        self,
        season=2026
    ):

        standings = (
            self.get_constructor_standings(
                season
            )
        )

        return standings[0]

    # -------------------------
    # Team Points
    # -------------------------

    def get_team_points(
        self,
        team,
        season=2026
    ):

        standings = (
            self.get_constructor_standings(
                season
            )
        )

        for row in standings:

            if row["team"] == team:

                return {
                    "team": team,
                    "points": float(
                        row["points"]
                    )
                }

        return None

    # -------------------------
    # Wins
    # -------------------------

    def get_team_wins(
        self,
        team,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        wins = (
            df[
                (df["team"] == team)
                &
                (df["winner"] == 1)
            ]
            .shape[0]
        )

        return {
            "team": team,
            "wins": int(wins)
        }

    def get_most_wins_team(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        wins = (
            df.groupby("team")
            ["winner"]
            .sum()
            .reset_index()
            .sort_values(
                "winner",
                ascending=False
            )
        )

        return wins.iloc[0].to_dict()

    # -------------------------
    # Podiums
    # -------------------------

    def get_team_podiums(
        self,
        team,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        podiums = (
            df[
                (df["team"] == team)
                &
                (df["podium"] == 1)
            ]
            .shape[0]
        )

        return {
            "team": team,
            "podiums": int(
                podiums
            )
        }

    def get_most_podiums_team(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        podiums = (
            df.groupby("team")
            ["podium"]
            .sum()
            .reset_index()
            .sort_values(
                "podium",
                ascending=False
            )
        )

        return podiums.iloc[0].to_dict()

    # -------------------------
    # Average Finish
    # -------------------------

    def get_team_average_finish(
        self,
        team,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            (df["team"] == team)
            &
            (df["position"].notna())
        ]

        avg_finish = (
            rows["position"]
            .mean()
        )

        return {
            "team": team,
            "average_finish":
                float(
                    round(
                        avg_finish,
                        2
                    )
                )
        }

    # -------------------------
    # Reliability
    # -------------------------

    def get_team_reliability(
        self,
        team,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            df["team"] == team
        ]

        finished = (
            rows["finished_race"]
            .sum()
        )

        dnf = (
            rows["dnf_flag"]
            .sum()
        )

        total = (
            finished + dnf
        )

        reliability = (
            finished / total
            if total > 0
            else 0
        )

        return {
            "team": team,
            "finished": int(
                finished
            ),
            "dnf": int(
                dnf
            ),
            "reliability":
                float(
                    round(
                        reliability * 100,
                        1
                    )
                )
        }

    def get_most_reliable_team(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        teams = (
            df["team"]
            .unique()
        )

        results = []

        for team in teams:

            results.append(
                self.get_team_reliability(
                    team,
                    season
                )
            )

        results.sort(
            key=lambda x:
            x["reliability"],
            reverse=True
        )

        return results[0]