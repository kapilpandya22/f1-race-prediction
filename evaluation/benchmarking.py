import os
from models.train import run_logistic_model, run_rf_model, build_training_dataset
from evaluation.metrics import evaluate_model
from features.build_features import run_pipeline
import pandas as pd


def rolling_evaluation(season: int, schedule: list, target_race: str):

    all_metrics = []

    target_index = schedule.index(target_race)

    os.makedirs("outputs/predictions/logistic", exist_ok=True)
    os.makedirs("outputs/predictions/random_forest", exist_ok=True)

    # ✅ build once
    train_df = build_training_dataset(
        train_seasons=[2023, 2024, 2025],
        race_history_2026=[]
    )

    for i in range(0, target_index + 1):

        current_race = schedule[i]
        race_history = schedule[:i]

        print(f"\nEvaluating on: {current_race}")

        final_df = run_pipeline(
            target_race=current_race,
            season=season
        )

        if final_df.empty:
            print(f"⚠️ Skipping {current_race} (empty features)")
            continue

        # ---------------------------
        # LOGISTIC
        # ---------------------------
        log_results, _ = run_logistic_model(
            train_df=train_df,
            final_df=final_df,
            season=season,
            race_name=current_race,
            race_history=race_history,
            train_seasons=[2023, 2024, 2025]
        )

        # ---------------------------
        # RANDOM FOREST
        # ---------------------------
        rf_results, _ = run_rf_model(
            train_df=train_df,
            final_df=final_df,
            season=season,
            race_name=current_race,
            race_history=race_history,
            train_seasons=[2023, 2024, 2025]
        )

        # ---------------------------
        # SAVE PREDICTIONS
        # ---------------------------
        race_name_clean = current_race.replace(" ", "_")

        log_dir = f"outputs/predictions/logistic/{season}_{race_name_clean}"
        os.makedirs(log_dir, exist_ok=True)

        log_results.to_csv(
            f"{log_dir}/race_predictions_benchmark.csv",
            index=False
        )

        rf_dir = f"outputs/predictions/random_forest/{season}_{race_name_clean}"
        os.makedirs(rf_dir, exist_ok=True)

        rf_results.to_csv(
            f"{rf_dir}/race_predictions_benchmark.csv",
            index=False
        )

        # ---------------------------
        # DASHBOARD (optional)
        # ---------------------------
        if season == 2026:
            os.makedirs("output/eva", exist_ok=True)

            race_clean = current_race.replace(" ", "_")
            # logistic
            eva_log_dir = "outputs/eva/logistic"
            os.makedirs(eva_log_dir, exist_ok=True)

            log_results.to_csv(
                f"{eva_log_dir}/{season}_{race_clean}.csv",
                index=False
            )

            # RF
            eva_rf_dir = "outputs/eva/random_forest"
            os.makedirs(eva_rf_dir, exist_ok=True)

            rf_results.to_csv(
                f"{eva_rf_dir}/{season}_{race_clean}.csv",
                index=False
            )

        # ---------------------------
        # SKIP FUTURE (use ONE model)
        # ---------------------------
        if log_results["target_top3"].isna().all():
            print(f"⚠️ Skipping {current_race} (no target data)")
            continue

        # ---------------------------
        # METRICS - LOGISTIC
        # ---------------------------
        metrics_log = evaluate_model(log_results)
        metrics_log["race"] = current_race
        metrics_log["model"] = "logistic"

        # ---------------------------
        # METRICS - RF
        # ---------------------------
        metrics_rf = evaluate_model(rf_results)
        metrics_rf["race"] = current_race
        metrics_rf["model"] = "random_forest"

        # ---------------------------
        # PRINT
        # ---------------------------
        print(f"\n📊 Logistic Metrics for {current_race}:")
        for k, v in metrics_log.items():
            if isinstance(v, (int, float)):
                print(f"{k}: {v:.4f}")

        print(f"\n📊 RF Metrics for {current_race}:")
        for k, v in metrics_rf.items():
            if isinstance(v, (int, float)):
                print(f"{k}: {v:.4f}")

        # ---------------------------
        # STORE
        # ---------------------------
        all_metrics.append(metrics_log)
        all_metrics.append(metrics_rf)

    return pd.DataFrame(all_metrics)