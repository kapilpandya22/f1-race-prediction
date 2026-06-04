import os
import json
from features.build_features import run_pipeline as build_features
from explainability.feature_importance import get_feature_importance
from models.train import build_training_dataset
from models.train import run_logistic_model, run_rf_model, run_xgb_model
from pipelines.race_logic import get_previous_races
from data.calendar import (
    F1_2023_SCHEDULE,
    F1_2024_SCHEDULE,
    F1_2025_SCHEDULE,
    F1_2026_SCHEDULE
)
from data.load_data import enable_cache

enable_cache()

MODEL_REGISTRY = {
    "logistic": run_logistic_model,
    "random_forest": run_rf_model,
    "xgboost": run_xgb_model
}


def run_prediction_pipeline(target_race):

    train_seasons = [2023, 2024, 2025]
    predict_season = 2026

    # ---------------------------
    # HISTORY
    # ---------------------------
    race_history_2026 = get_previous_races(F1_2026_SCHEDULE, target_race)

    print("\n=== PREDICTION MODE ===")
    print("Target:", target_race)
    print("2026 History:", race_history_2026)
    


    # ---------------------------
    # BUILD FEATURES (TEST ONLY)
    # ---------------------------
    final_df = build_features(target_race=target_race, season=predict_season)
    if final_df.empty:
        raise ValueError(f"No features generated for {target_race}")

    print("\n=== RELIABILITY CHECK (ALL DRIVERS) ===")
    print(final_df[["driver", "reliability"]].sort_values("reliability"))

    print("\n=== FEATURE SHAPE ===")
    print(final_df.shape)

    final_df["driver"] = final_df["driver"].str.upper().str.strip()


    # ---------------------------
    # TRAIN DATA
    # ---------------------------
    train_df = build_training_dataset(train_seasons, race_history_2026)

    # ---------------------------
    # MODEL LOOP
    # ---------------------------
    for model_name, model_fn in MODEL_REGISTRY.items():

        print(f"\n🚀 Running model: {model_name}")

        results, model = model_fn(
            train_df=train_df,
            final_df=final_df,
            season=predict_season,
            race_name=target_race,
            race_history=race_history_2026,
            train_seasons=train_seasons
        )

        # ---------------------------
        # SAVE OUTPUT 
        # ---------------------------
        race_name_clean = target_race.replace(" ", "_")
        prediction_folder = (
            f"outputs/predictions/{model_name}/"
            f"{predict_season}_{race_name_clean}"
        )

        analysis_folder = (
            f"outputs/analysis/{model_name}/"
            f"{predict_season}_{race_name_clean}"
        )

        os.makedirs(prediction_folder, exist_ok=True)
        os.makedirs(analysis_folder, exist_ok=True)

        results["season"] = predict_season
        results["race"] = target_race
        results["driver"] = results["driver"].str.upper().str.strip()
        results.to_csv(
            f"{prediction_folder}/predictions.csv",
            index=False
        )
        print("\n=== PREDICTIONS ===")
        print(results[["driver", "pred_top3_prob", "rank"]].sort_values("rank"))
        
        
        # ---------------------------
        # MERGE FEATURES
        # ---------------------------        
        feature_names = model.feature_names_

        missing = set(feature_names) - set(final_df.columns)
        if missing:
            raise ValueError(f"Missing features in final_df: {missing}")

        feature_subset = final_df[["driver"] + feature_names].copy()

        results_with_features = results.merge(
            feature_subset,
            on="driver",
            how="left",
            suffixes=("", "_new")
        )

        for col in feature_names:
            if f"{col}_new" in results_with_features.columns:
                results_with_features[col] = results_with_features[f"{col}_new"]
                results_with_features.drop(columns=[f"{col}_new"], inplace=True)

        results_with_features = results_with_features[
            ["driver", "pred_top3_prob", "rank", "season", "race"] + feature_names
        ]

        results_with_features.to_csv(
            f"{prediction_folder}/predictions_with_features.csv",
            index=False
        )
        
        
        # ---------------------------
        # FEATURE IMPORTANCE
        # ---------------------------       
        importance_df = get_feature_importance(model, feature_names)
        importance_df["abs_importance"] = importance_df["value"].abs()
        importance_df = importance_df.sort_values(by="abs_importance", ascending=False)

        importance_df.to_csv(
            f"{prediction_folder}/feature_importance.csv",
            index=False
        )
        # 🔥 PRINT FULL TABLE (no truncation)
        print("\n=== FEATURE IMPORTANCE ===")
        print(importance_df.to_string(index=False))
        
        # ---------------------------
        # EMPTY METRICS FILE
        # ---------------------------
        metrics = {
            "accuracy": None,
            "f1": None,
            "auc": None,
            "log_loss": None,
            "brier": None,
            "mrr": None,
            "top3_accuracy": None,
            "top3_recall": None,
            "top3_precision": None,
            "race": target_race,
            "season": predict_season,
            "has_ground_truth": False,
        }

        with open(f"{analysis_folder}/metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)

                
        
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise ValueError("❌ Please provide race name")

    race = sys.argv[1]
    print(f"\n🚀 Running prediction for: {race}\n")

    run_prediction_pipeline(race)        