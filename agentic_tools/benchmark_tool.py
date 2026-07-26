import pandas as pd
from pathlib import Path


class BenchmarkTool:

    BASE_DIR = (
        Path(__file__).resolve().parent.parent
        / "outputs"
        / "analysis"
    )

    def get_model_summary(
        self,
        model
    ):

        path = (
            self.BASE_DIR
            / model
            / "mean_metrics.csv"
        )
        
        df = pd.read_csv(path)

        return {
            row["metric"]: row["value"]
            for _, row in df.iterrows()
        }
        

    def compare_models(
        self,
        models=None
    ):

        if models is None:
            models = [
                "logistic",
                "random_forest",
                "xgboost"
            ]

        results = {}

        for model in models:

            results[model] = (
                self.get_model_summary(model)
            )

        return results

    def get_best_model(
        self,
        metric="f1"
    ):

        comparison = self.compare_models()

        scores = {}

        for model, metrics in comparison.items():

            score = metrics.get(metric)

            if score is not None:
                scores[model] = score

        best_score = max(scores.values())

        winners = [
            model
            for model, score in scores.items()
            if score == best_score
        ]

        return {
            "metric": metric,
            "best_models": winners,
            "score": best_score
        }
    def get_metric_leader(
        self,
        metric
    ):

        comparison = self.compare_models()

        LOWER_IS_BETTER = [
            "log_loss",
            "brier"
        ]

        best_model = None

        if metric in LOWER_IS_BETTER:
            best_score = float("inf")
        else:
            best_score = float("-inf")

        for model, metrics in comparison.items():

            score = metrics.get(metric)

            if score is None:
                continue

            if metric in LOWER_IS_BETTER:

                if score < best_score:
                    best_score = score
                    best_model = model

            else:

                if score > best_score:
                    best_score = score
                    best_model = model

        return {
            "metric": metric,
            "best_model": best_model,
            "score": best_score
        }

    def get_leaderboard(
        self,
        metric="f1"
    ):

        comparison = self.compare_models()

        leaderboard = []

        for model, metrics in comparison.items():

            leaderboard.append(
                {
                    "model": model,
                    "score": metrics.get(metric)
                }
            )

        leaderboard.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return leaderboard