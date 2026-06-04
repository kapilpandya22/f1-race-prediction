import os
import json
import pandas as pd

from data.load_target import build_target
from evaluation.metrics import evaluate_model
from data.load_data import fetch_and_store_race
from explainability.driver_explanations import compute_driver_explanations
from outputs.analysis.aggregate_results import main as run_aggregate


def run_metrics_pipeline(target_race):

    predict_season = 2026
    models = ["logistic", "random_forest", "xgboost"]

    # ---------------------------
    # LOAD GROUND TRUTH (ONCE)
    # ---------------------------
    race_clean = target_race.replace(" ", "_")
    r_path = f"data/golden/{predict_season}_{race_clean}_R.csv"

    if not os.path.exists(r_path):
        print(f"📥 Fetching race results for {target_race}")
        fetch_and_store_race(predict_season, target_race)

        if not os.path.exists(r_path):
            raise RuntimeError(f"❌ Golden race data still missing for {target_race}")

    target_df = build_target(predict_season, target_race)

    if target_df.empty:
        raise RuntimeError(f"⏳ Race not completed yet → no ground truth for {target_race}")

    # normalize ONCE
    target_df["driver"] = target_df["driver"].str.upper().str.strip()

    # ---------------------------
    # MODEL LOOP
    # ---------------------------
    for model_name in models:

        print(f"\n📊 Running metrics for {model_name} — {target_race}")

        prediction_folder = (
            f"outputs/predictions/{model_name}/{predict_season}_{race_clean}"
        )

        analysis_folder = (
            f"outputs/analysis/{model_name}/{predict_season}_{race_clean}"
        )

        os.makedirs(analysis_folder, exist_ok=True)
        preds_path = f"{prediction_folder}/predictions_with_features.csv"

        if not os.path.exists(preds_path):
            raise RuntimeError(
                f"❌ Missing predictions for {target_race} ({model_name})\n"
                f"Run prediction pipeline first."
            )

        # ✅ load predictions here
        df = pd.read_csv(preds_path)

        # normalize
        df["driver"] = df["driver"].str.upper().str.strip()

        # ✅ merge here (CORRECT PLACE)
        df = df.merge(target_df, on="driver", how="left", validate="one_to_one")

        # strict check
        if "target_top3" not in df.columns or df["target_top3"].isna().all():
            raise RuntimeError("❌ Target merge failed — invalid evaluation data")

        # ---------------------------
        # METRICS
        # ---------------------------
        metrics = evaluate_model(df)

        print("\n=== METRICS ===")
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                print(f"{k}: {v:.4f}")
            else:
                print(f"{k}: {v}")

        metrics["race"] = target_race
        metrics["season"] = predict_season
        metrics["has_ground_truth"] = True
        metrics["model"] = model_name

        with open(f"{analysis_folder}/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)

        # ---------------------------
        # DRIVER EXPLANATIONS
        # ---------------------------
        importance_path = f"{prediction_folder}/feature_importance.csv"

        if not os.path.exists(importance_path):
            raise RuntimeError(
                f"❌ Missing feature importance for {model_name} — run prediction first"
            )

        importance_df = pd.read_csv(importance_path)
        feature_cols = importance_df["feature"].tolist()

        explain_df = compute_driver_explanations(df, importance_df, feature_cols)

        explain_df.to_csv(
            f"{analysis_folder}/driver_explanations.csv",
            index=False
        )

        print(f"✅ {model_name} done")

    # ---------------------------
    # GLOBAL ANALYSIS
    # ---------------------------
    print("\n📊 Updating global analysis...")
    run_aggregate()
        
        
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise ValueError("❌ Please provide race name")

    race = sys.argv[1]
    print(f"\n📊 Running metrics for: {race}\n")

    run_metrics_pipeline(race)        