import pandas as pd
from pathlib import Path


class DriverAnalyticsTool:

    BASE_DIR = Path("/Users/paridhishukla/Downloads/f1-ml-project 2/data/golden")

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
    # Championship
    # -------------------------

    def get_driver_standings(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        standings = (
            df.groupby("driver")
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

    def get_championship_leader(
        self,
        season=2026
    ):

        standings = (
            self.get_driver_standings(
                season
            )
        )

        return standings[0]

    def get_driver_points(
        self,
        driver,
        season=2026
    ):

        standings = (
            self.get_driver_standings(
                season
            )
        )

        for row in standings:

            if row["driver"] == driver:

                return {
                    "driver": driver,
                    "points": row["points"]
                }

        return None

    # -------------------------
    # Wins
    # -------------------------

    def get_driver_wins(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        wins = (
            df[
                (df["driver"] == driver)
                &
                (df["winner"] == 1)
            ]
            .shape[0]
        )

        return {
            "driver": driver,
            "wins": int(wins)
        }

    def get_most_wins(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        wins = (
            df.groupby("driver")
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

    def get_driver_podiums(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        podiums = (
            df[
                (df["driver"] == driver)
                &
                (df["podium"] == 1)
            ]
            .shape[0]
        )

        return {
            "driver": driver,
            "podiums": int(podiums)
        }

    def get_most_podiums(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        podiums = (
            df.groupby("driver")
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

    def get_average_finish(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            (df["driver"] == driver)
            &
            (df["position"].notna())
        ]

        avg_finish = (
            rows["position"]
            .mean()
        )

        return {
            "driver": driver,
            "average_finish": float(
                round(
                    avg_finish,
                    2
                )
            )
        }

    # -------------------------
    # Positions Gained
    # -------------------------

    def get_positions_gained(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            df["driver"] == driver
        ]

        gained = (
            rows["positions_gained"]
            .sum()
        )

        return {
            "driver": driver,
            "positions_gained":
                int(gained)
        }

    def get_most_positions_gained(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        gained = (
            df.groupby("driver")
            ["positions_gained"]
            .sum()
            .reset_index()
            .sort_values(
                "positions_gained",
                ascending=False
            )
        )

        return gained.iloc[0].to_dict()

    # -------------------------
    # Reliability
    # -------------------------

    def get_reliability(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            df["driver"] == driver
        ]

        finished = (
            rows["finished_race"]
            .sum()
        )

        dnf = (
            rows["dnf_flag"]
            .sum()
        )

        total = finished + dnf

        reliability = (
            finished / total
            if total > 0
            else 0
        )

        return {
            "driver": driver,
            "finished": int(finished),
            "dnf": int(dnf),
            "reliability": float(
                round(
                    reliability * 100,
                    1
                ) )
        }

    def get_most_reliable_driver(
        self,
        season=2026,
        min_races=3
    ):

        df = self.load_season_data(
            season
        )

        results = []

        for driver in (
            df["driver"]
            .unique()
        ):

            stats = (
                self.get_reliability(
                    driver,
                    season
                )
            )

            total = (
                stats["finished"]
                +
                stats["dnf"]
            )

            if total >= min_races:

                results.append(
                    stats
                )

        results.sort(
            key=lambda x:
            x["reliability"],
            reverse=True
        )

        return results[0]

    # -------------------------
    # Consistency
    # -------------------------

    def get_consistency(
        self,
        driver,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        rows = df[
            (df["driver"] == driver)
            &
            (df["position"].notna())
        ]

        std_dev = (
            rows["position"]
            .std()
        )

        return {
            "driver": driver,
            "finish_position_std":
                float(
                    round(std_dev),
                    2
                )
        }

    def get_most_consistent_driver(
        self,
        season=2026
    ):

        df = self.load_season_data(
            season
        )

        drivers = (
            df["driver"]
            .unique()
        )

        results = []

        for driver in drivers:

            stats = (
                self.get_consistency(
                    driver,
                    season
                )
            )

            results.append(
                stats
            )

        results.sort(
            key=lambda x:
            x["finish_position_std"]
        )

        return results[0]