import pandas as pd

from agentic_tools.path_resolver import get_file_path


class FeatureImportanceTool:

    def get_top_features(
        self,
        race_name,
        model="logistic",
        top_n=10
    ):

        path = get_file_path(
            race_name=race_name,
            model=model,
            file_type="feature_importance"
        )

        df = pd.read_csv(path)

        return (
            df.sort_values(
                "abs_importance",
                ascending=False
            )
            .head(top_n)
            [["feature", "abs_importance"]]
            .to_dict("records")
        )