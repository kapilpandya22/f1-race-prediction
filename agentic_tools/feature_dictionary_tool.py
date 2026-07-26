import pandas as pd


class FeatureDictionaryTool:

    def __init__(self):

        self.df = pd.read_excel(
            "/Users/paridhishukla/Downloads/f1-ml-project 2/data/golden/Feature Interpretation.xlsx"
        )

        print(
            self.df.columns
        )

    def get_meaning(
        self,
        feature
    ):

        row = self.df[
            self.df["feature"] == feature
        ]

        if row.empty:
            return None

        return row.iloc[0][
            "meaning"
        ]