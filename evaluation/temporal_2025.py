"""
2025 Temporal Evaluation Study
==============================

Professor's evaluation design:

EARLY
    Training: 2023 + 2024
    Testing:  2025 Races 1-8

MID
    Training: 2023 + 2024 + 2025 Races 1-8
    Testing:  2025 Races 9-16

LATE
    Training: 2023 + 2024 + 2025 Races 1-16
    Testing:  2025 Races 17-24


Models:
    - Logistic Regression
    - Random Forest
    - XGBoost
    - Qualifying-position baseline


Metrics:
    - Accuracy
    - F1
    - AUC
    - Log Loss
    - Brier Score
    - MRR
    - Top-3 Accuracy
    - Top-3 Precision
    - Top-3 Recall


IMPORTANT
---------
This file is an evaluation-only module.

It does NOT modify:
    features/weather.py
    models/train.py
    evaluation/metrics.py
    benchmark.py
    the 2026 prediction pipeline
    the frontend


Results:
    outputs/evaluation_2025/
"""

import os
import numpy as np
import pandas as pd

from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    log_loss,
    brier_score_loss,
)

from data.calendar import F1_2025_SCHEDULE

from features.build_features import run_pipeline

from models.train import (
    build_training_dataset,
    prepare_training_data,
    prepare_features,
    train_logistic,
    predict_logistic,
    train_rf,
    predict_rf,
    train_xgb,
    predict_xgb,
)

from features.feature_list import FEATURE_COLS as feature_cols

from evaluation.metrics import evaluate_model

from evaluation.historical_weather_2025 import (
    get_historical_weather_2025,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

RESULTS_DIR = "outputs/evaluation_2025"

os.makedirs(
    RESULTS_DIR,
    exist_ok=True,
)

MODEL_NAMES = [
    "logistic",
    "random_forest",
    "xgboost",
]

METRIC_COLUMNS = [
    "accuracy",
    "f1",
    "auc",
    "log_loss",
    "brier",
    "mrr",
    "top3_accuracy",
    "top3_precision",
    "top3_recall",
]


WEATHER_COLUMNS = [
    "rain_probability",
    "wet_track_flag",
    "temperature",
    "humidity",
    "wind_speed",
    "temperature_vs_baseline",
    "humidity_vs_baseline",
    "wind_speed_vs_baseline",
    "rain_probability_vs_baseline",
]


# =============================================================================
# PHASE DEFINITIONS
# =============================================================================

def get_evaluation_phases():

    races = list(F1_2025_SCHEDULE)

    if len(races) < 24:

        raise ValueError(
            f"Expected 24 races in F1_2025_SCHEDULE, "
            f"but found {len(races)}."
        )

    races = races[:24]

    return {

        "early": {
            "training_2025": [],
            "test": races[:8],
        },

        "mid": {
            "training_2025": races[:8],
            "test": races[8:16],
        },

        "late": {
            "training_2025": races[:16],
            "test": races[16:24],
        },
    }


# =============================================================================
# APPLY HISTORICAL 2025 WEATHER
# =============================================================================

def apply_historical_weather_2025(
    race_df,
    race_name,
):
    """
    Replace the production weather values in a 2025 evaluation
    dataframe with the archived historical forecast values.

    This is intentionally performed only inside the evaluation.

    The production weather.py remains unchanged.
    """

    race_df = race_df.copy()

    print(
        "\n🌦️ Applying historical 2025 weather "
        f"for {race_name}"
    )

    historical_weather = (
        get_historical_weather_2025(
            race_name
        )
    )

    for column in WEATHER_COLUMNS:

        if column not in historical_weather:

            raise ValueError(
                f"Historical weather result is missing "
                f"'{column}' for {race_name}."
            )

        race_df[column] = (
            historical_weather[column]
        )

    # -----------------------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------------------

    for column in WEATHER_COLUMNS:

        if race_df[column].isna().any():

            raise ValueError(
                f"Historical weather column "
                f"'{column}' contains NaN values "
                f"for {race_name}."
            )

    print(
        "✅ Historical weather applied successfully."
    )

    return race_df


def recalculate_weather_interactions_2025(race_df):
    """
    Recalculate interaction features that depend on the weather.

    The production pipeline calculates ``rain_x_quali`` using the
    production weather source. During the 2025 temporal evaluation we
    replace that weather with the historical ~24-hour forecast, so the
    weather-dependent interaction must also be recalculated.

    This function is evaluation-only and does not modify the production
    feature pipeline.
    """

    race_df = race_df.copy()

    required = [
        "qualifying_position",
        "rain_probability",
    ]

    missing = [
        column
        for column in required
        if column not in race_df.columns
    ]

    if missing:
        raise ValueError(
            "Cannot recalculate weather interaction features. "
            f"Missing columns: {missing}"
        )

    qualifying_position = pd.to_numeric(
        race_df["qualifying_position"],
        errors="coerce",
    )

    rain_probability = pd.to_numeric(
        race_df["rain_probability"],
        errors="coerce",
    )

    grid_size = qualifying_position.dropna().max()

    if pd.isna(grid_size) or grid_size == 0:
        grid_size = 20

    quali_norm = qualifying_position / grid_size

    race_df["rain_x_quali"] = (
        rain_probability * quali_norm
    )

    race_df["rain_x_quali"] = (
        race_df["rain_x_quali"].fillna(0)
    )

    print(
        "✅ Recalculated rain_x_quali using historical 2025 weather."
    )

    return race_df


# =============================================================================
# PHASE DATASET WEATHER REPLACEMENT
# =============================================================================

def apply_historical_weather_to_2025_dataset(
    df,
):
    """
    Apply historical weather to every 2025 race contained
    in a dataframe.

    Used for 2025 training races that become part of the
    temporal training set.
    """

    df = df.copy()

    if df.empty:
        return df

    if "race" not in df.columns:

        raise ValueError(
            "Cannot apply historical weather because "
            "'race' column is missing."
        )

    processed = []

    for race_name in df["race"].unique():

        race_df = df[
            df["race"] == race_name
        ].copy()

        race_df = (
            apply_historical_weather_2025(
                race_df,
                race_name,
            )
        )

        # Keep weather-dependent interactions consistent with the
        # historical 2025 weather values.
        race_df = recalculate_weather_interactions_2025(
            race_df
        )

        processed.append(
            race_df
        )

    if not processed:

        return df

    return pd.concat(
        processed,
        ignore_index=True,
    )


# =============================================================================
# BUILD BASE TRAINING DATA
# =============================================================================

def build_base_training_data():

    print("\n" + "=" * 80)
    print(
        "BUILDING BASE TRAINING DATA: 2023 + 2024"
    )
    print("=" * 80)

    train_df = build_training_dataset(
        train_seasons=[2023, 2024],
        race_history_2026=[],
    )

    train_df = train_df.copy()

    print(
        f"\n2023 + 2024 training records: "
        f"{len(train_df)}"
    )

    print(
        "Training race names:",
        train_df["race"].nunique(),
    )

    print(
        "Training seasons:",
        sorted(
            train_df["season"].unique()
        ),
    )

    return train_df


# =============================================================================
# BUILD ONE HISTORICAL 2025 RACE
# =============================================================================

def build_2025_race_dataset(
    race,
):

    print("\n" + "-" * 80)
    print(
        f"BUILDING 2025 DATA: {race}"
    )
    print("-" * 80)

    # -----------------------------------------------------------------
    # EXISTING FEATURE PIPELINE
    # -----------------------------------------------------------------

    final_df = run_pipeline(
        target_race=race,
        season=2025,
    )

    if final_df.empty:

        print(
            f"WARNING: Empty feature dataframe "
            f"for {race}"
        )

        return pd.DataFrame()

    # -----------------------------------------------------------------
    # BUILD HISTORICAL TARGET
    # -----------------------------------------------------------------

    final_df = prepare_training_data(
        final_df,
        season=2025,
        race_name=race,
    )

    final_df["season"] = 2025
    final_df["race"] = race

    # -----------------------------------------------------------------
    # IMPORTANT:
    # REPLACE THE 2026 WEATHER VALUES
    # WITH HISTORICAL 2025 FORECAST VALUES
    # -----------------------------------------------------------------

    final_df = apply_historical_weather_2025(
        final_df,
        race,
    )

    # IMPORTANT:
    # rain_x_quali was originally calculated by the production
    # pipeline before the historical weather replacement.
    # Recalculate it so it uses the historical 2025 forecast.
    # -----------------------------------------------------------------

    final_df = recalculate_weather_interactions_2025(
        final_df
    )

    # -----------------------------------------------------------------
    # TARGET VALIDATION
    # -----------------------------------------------------------------

    missing_targets = (
        final_df["target_top3"]
        .isna()
        .sum()
    )

    print(
        f"Driver records: "
        f"{len(final_df)}"
    )

    print(
        f"Missing targets before handling: "
        f"{missing_targets}"
    )

    # -----------------------------------------------------------------
    # HANDLE DRIVERS ABSENT FROM THE RACE RESULT
    # -----------------------------------------------------------------
    #
    # A driver can appear in qualifying/practice features but not in
    # the race-result file because they did not participate in the race.
    #
    # Example:
    # 2025 Spanish GP:
    # STR appears in qualifying but did not start the race.
    #
    # Such a driver cannot have finished in the Top 3, so for the
    # Top-3 classification target we assign target_top3 = 0.
    #
    # This is different from a genuinely corrupted or missing result
    # for a driver who actually participated in the race.
    # -----------------------------------------------------------------

    if missing_targets > 0:

        missing_drivers = final_df.loc[
            final_df["target_top3"].isna(),
            "driver",
        ].tolist()

        print(
            f"\nWARNING: Drivers with missing race targets: "
            f"{missing_drivers}"
        )

        # Check the corresponding race-result file.
        from data.load_target import load_single_race_result

        race_results = load_single_race_result(
            season=2025,
            race_name=race,
        )

        race_result_drivers = set(
            race_results["driver"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # Normalize feature driver codes for matching.
        final_driver_codes = (
            final_df["driver"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # Drivers missing from the race result are treated as
        # non-participants and therefore non-Top-3.
        absent_from_race = [
            driver
            for driver in missing_drivers
            if driver.strip().upper()
            not in race_result_drivers
        ]

        if absent_from_race:

            print(
                f"⚠️ Drivers present in qualifying/features but "
                f"absent from race results: {absent_from_race}"
            )

            for driver in absent_from_race:

                mask = (
                    final_driver_codes
                    == driver.strip().upper()
                )

                final_df.loc[
                    mask,
                    "target_top3"
                ] = 0

                print(
                    f"   → {driver}: "
                    f"target_top3 = 0 "
                    f"(did not participate)"
                )

        # Re-check after handling legitimate non-participants.
        remaining_missing = (
            final_df["target_top3"]
            .isna()
            .sum()
        )

        if remaining_missing > 0:

            remaining_drivers = final_df.loc[
                final_df["target_top3"].isna(),
                "driver",
            ].tolist()

            raise ValueError(
                f"2025 {race} still has "
                f"{remaining_missing} missing target values "
                f"after handling non-participants. "
                f"Remaining drivers: {remaining_drivers}. "
                f"This indicates a genuine race-result/driver "
                f"matching problem."
            )

    # -----------------------------------------------------------------
    # FINAL TARGET VALIDATION
    # -----------------------------------------------------------------

    final_df["target_top3"] = (
        final_df["target_top3"]
        .astype(int)
    )

    print(
        f"Missing targets after handling: "
        f"{final_df['target_top3'].isna().sum()}"
    )

    print(
        f"Top-3 drivers: "
        f"{final_df.loc[final_df['target_top3'] == 1, 'driver'].tolist()}"
    )

    print(
        f"Non-Top-3 drivers: "
        f"{final_df.loc[final_df['target_top3'] == 0, 'driver'].tolist()}"
    )

    return final_df

# =============================================================================
# BUILD ALL 2025 DATA
# =============================================================================

def build_all_2025_data(
    races,
):

    all_data = []

    for race in races:

        df = build_2025_race_dataset(
            race
        )

        if df.empty:
            continue

        all_data.append(
            df
        )

    if not all_data:

        raise ValueError(
            "No 2025 race data could be constructed."
        )

    result = pd.concat(
        all_data,
        ignore_index=True,
    )

    print("\n" + "=" * 80)
    print(
        "2025 DATASET CONSTRUCTION COMPLETE"
    )
    print("=" * 80)

    print(
        f"Total 2025 driver-race records: "
        f"{len(result)}"
    )

    print(
        f"Total 2025 races: "
        f"{result['race'].nunique()}"
    )

    return result


# =============================================================================
# MODEL DATA PREPARATION
# =============================================================================

def prepare_model_data(
    train_df,
    test_df,
):

    train_df = train_df.copy()
    test_df = test_df.copy()

    # -----------------------------------------------------------------
    # DRIVER NORMALISATION
    # -----------------------------------------------------------------

    if "driver" in train_df.columns:

        train_df["driver"] = (
            train_df["driver"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    if "driver" in test_df.columns:

        test_df["driver"] = (
            test_df["driver"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    # -----------------------------------------------------------------
    # REMOVE TRAINING ROWS WITHOUT TARGETS
    # -----------------------------------------------------------------

    train_df = train_df.dropna(
        subset=["target_top3"]
    ).copy()

    if train_df.empty:

        raise ValueError(
            "Training dataframe contains "
            "no target rows."
        )

    # -----------------------------------------------------------------
    # SAMPLE WEIGHTS
    # -----------------------------------------------------------------

    train_df["sample_weight"] = (
        train_df["season"].map(
            {
                2023: 1.0,
                2024: 1.3,
                2025: 1.7,
                2026: 2.0,
            }
        )
    )

    if train_df[
        "sample_weight"
    ].isna().any():

        missing_seasons = sorted(
            train_df.loc[
                train_df["sample_weight"].isna(),
                "season",
            ].unique()
        )

        raise ValueError(
            f"Missing sample weights for seasons: "
            f"{missing_seasons}"
        )

    weights = train_df[
        "sample_weight"
    ]

    # -----------------------------------------------------------------
    # FEATURE EXISTENCE
    # -----------------------------------------------------------------

    missing_train = (
        set(feature_cols)
        - set(train_df.columns)
    )

    missing_test = (
        set(feature_cols)
        - set(test_df.columns)
    )

    if missing_train:

        raise ValueError(
            f"Missing features in TRAIN: "
            f"{missing_train}"
        )

    if missing_test:

        raise ValueError(
            f"Missing features in TEST: "
            f"{missing_test}"
        )

    # -----------------------------------------------------------------
    # PREPARE FEATURES
    # -----------------------------------------------------------------

    X_train, X_test = prepare_features(
        train_df,
        test_df,
        feature_cols,
    )

    y_train = (
        train_df["target_top3"]
        .astype(int)
    )

    return (
        X_train,
        X_test,
        y_train,
        weights,
    )


# =============================================================================
# LOGISTIC REGRESSION
# =============================================================================

def predict_logistic_evaluation(
    train_df,
    test_df,
):

    (
        X_train,
        X_test,
        y_train,
        weights,
    ) = prepare_model_data(
        train_df,
        test_df,
    )

    model, scaler = train_logistic(
        X_train,
        y_train,
        sample_weight=weights,
    )

    model.feature_names_ = (
        X_train.columns.tolist()
    )

    probabilities = predict_logistic(
        model,
        scaler,
        X_test,
    )

    result = test_df.copy()

    result["pred_rank_score"] = (
        probabilities
    )

    result["pred_top3_prob"] = (
        probabilities.clip(
            0.01,
            0.99,
        )
    )

    result = result.sort_values(
        "pred_rank_score",
        ascending=False,
    ).reset_index(
        drop=True
    )

    result["rank"] = (
        result.index + 1
    )

    return result


# =============================================================================
# RANDOM FOREST
# =============================================================================

def predict_rf_evaluation(
    train_df,
    test_df,
):

    (
        X_train,
        X_test,
        y_train,
        weights,
    ) = prepare_model_data(
        train_df,
        test_df,
    )

    model = train_rf(
        X_train,
        y_train,
        sample_weight=weights,
    )

    model.feature_names_ = (
        X_train.columns.tolist()
    )

    probabilities = predict_rf(
        model,
        X_test,
    )

    result = test_df.copy()

    result["pred_rank_score"] = (
        probabilities
    )

    result["pred_top3_prob"] = (
        probabilities.clip(
            0.01,
            0.99,
        )
    )

    result = result.sort_values(
        "pred_rank_score",
        ascending=False,
    ).reset_index(
        drop=True
    )

    result["rank"] = (
        result.index + 1
    )

    return result


# =============================================================================
# XGBOOST
# =============================================================================

def predict_xgb_evaluation(
    train_df,
    test_df,
):

    (
        X_train,
        X_test,
        y_train,
        weights,
    ) = prepare_model_data(
        train_df,
        test_df,
    )

    model = train_xgb(
        X_train,
        y_train,
        sample_weight=weights,
    )

    model.feature_names_ = (
        X_train.columns.tolist()
    )

    probabilities = predict_xgb(
        model,
        X_test,
    )

    result = test_df.copy()

    result["pred_rank_score"] = (
        probabilities
    )

    result["pred_top3_prob"] = (
        probabilities.clip(
            0.01,
            0.99,
        )
    )

    result = result.sort_values(
        "pred_rank_score",
        ascending=False,
    ).reset_index(
        drop=True
    )

    result["rank"] = (
        result.index + 1
    )

    return result


# =============================================================================
# MODEL DISPATCH
# =============================================================================

def run_model(
    model_name,
    train_df,
    test_df,
):

    if model_name == "logistic":

        return predict_logistic_evaluation(
            train_df,
            test_df,
        )

    if model_name == "random_forest":

        return predict_rf_evaluation(
            train_df,
            test_df,
        )

    if model_name == "xgboost":

        return predict_xgb_evaluation(
            train_df,
            test_df,
        )

    raise ValueError(
        f"Unknown model: {model_name}"
    )


# =============================================================================
# QUALIFYING BASELINE
# =============================================================================

def build_qualifying_baseline(
    race_df,
):

    result = race_df.copy()

    if (
        "qualifying_position"
        not in result.columns
    ):

        raise ValueError(
            "qualifying_position is not available "
            "for the qualifying baseline."
        )

    result["qualifying_position"] = (
        pd.to_numeric(
            result[
                "qualifying_position"
            ],
            errors="coerce",
        )
    )

    if result[
        "qualifying_position"
    ].isna().all():

        raise ValueError(
            "All qualifying_position values "
            "are missing."
        )

    # Lower qualifying position =
    # better predicted race position.
    result["pred_rank_score"] = (
        -result["qualifying_position"]
    )

    # Small probabilities prevent infinite
    # Log Loss / Brier values.
    result["pred_top3_prob"] = np.where(
        result[
            "qualifying_position"
        ] <= 3,
        0.99,
        0.01,
    )

    result = result.sort_values(
        "pred_rank_score",
        ascending=False,
    ).reset_index(
        drop=True
    )

    result["rank"] = (
        result.index + 1
    )

    return result


# =============================================================================
# QUALIFYING BASELINE METRICS
# =============================================================================

def evaluate_qualifying_baseline(
    race_df,
):

    df = build_qualifying_baseline(
        race_df
    )

    df = df.dropna(
        subset=["target_top3"]
    ).copy()

    y_true = (
        df["target_top3"]
        .astype(int)
    )

    y_prob = (
        df["pred_top3_prob"]
    )

    ranked = df.sort_values(
        "pred_rank_score",
        ascending=False,
    )

    predicted_top3 = set(
        ranked.head(3)["driver"]
    )

    actual_top3 = set(
        df[
            df["target_top3"] == 1
        ]["driver"]
    )

    hits = len(
        predicted_top3
        & actual_top3
    )

    # -----------------------------------------------------------------
    # CLASSIFICATION PREDICTION
    # -----------------------------------------------------------------

    y_pred = np.zeros(
        len(df),
        dtype=int,
    )

    top3_indices = (
        ranked.head(3).index
    )

    index_positions = (
        df.index.get_indexer(
            top3_indices
        )
    )

    y_pred[
        index_positions
    ] = 1

    # -----------------------------------------------------------------
    # METRICS
    # -----------------------------------------------------------------

    accuracy = float(
        np.mean(
            y_true.values
            == y_pred
        )
    )

    f1 = float(
        f1_score(
            y_true,
            y_pred,
            average="binary",
            zero_division=0,
        )
    )

    if y_true.nunique() < 2:

        auc = None
        loss = None

    else:

        auc = float(
            roc_auc_score(
                y_true,
                y_prob,
            )
        )

        loss = float(
            log_loss(
                y_true,
                y_prob,
            )
        )

    brier = float(
        brier_score_loss(
            y_true,
            y_prob,
        )
    )

    # -----------------------------------------------------------------
    # MRR
    # -----------------------------------------------------------------

    reciprocal_ranks = []

    for rank, row in enumerate(
        ranked.itertuples(),
        start=1,
    ):

        if row.target_top3 == 1:

            reciprocal_ranks.append(
                1 / rank
            )

    if reciprocal_ranks:

        mrr = float(
            np.mean(
                reciprocal_ranks
            )
        )

    else:

        mrr = 0.0

    # -----------------------------------------------------------------
    # TOP-3 METRICS
    # -----------------------------------------------------------------

    top3_accuracy = (
        hits / 3
    )

    top3_precision = (
        hits / 3
    )

    if len(actual_top3) == 0:

        top3_recall = 0.0

    else:

        top3_recall = (
            hits
            / len(actual_top3)
        )

    return {

        "accuracy": accuracy,

        "f1": f1,

        "auc": auc,

        "log_loss": loss,

        "brier": brier,

        "mrr": mrr,

        "top3_accuracy":
            float(top3_accuracy),

        "top3_precision":
            float(top3_precision),

        "top3_recall":
            float(top3_recall),
    }


# =============================================================================
# EVALUATE ONE RACE
# =============================================================================

def evaluate_one_race(
    race,
    phase,
    train_df,
    race_df,
):

    print("\n" + "#" * 80)

    print(
        f"PHASE: {phase.upper()} | "
        f"RACE: {race}"
    )

    print("#" * 80)

    results = []

    # -----------------------------------------------------------------
    # SAFETY CHECKS
    # -----------------------------------------------------------------

    if race_df.empty:

        raise ValueError(
            f"No test data available "
            f"for {race}."
        )

    if race_df[
        "target_top3"
    ].isna().any():

        missing = race_df[
            "target_top3"
        ].isna().sum()

        raise ValueError(
            f"{race} has {missing} "
            f"missing target_top3 values."
        )

    print(
        f"Training records: "
        f"{len(train_df)}"
    )

    print(
        f"Test records: "
        f"{len(race_df)}"
    )

    print(
        "Actual Top-3 drivers:",
        list(
            race_df.loc[
                race_df[
                    "target_top3"
                ] == 1,
                "driver",
            ]
        ),
    )

    # -----------------------------------------------------------------
    # MODELS
    # -----------------------------------------------------------------

    for model_name in MODEL_NAMES:

        print(
            f"\nRunning {model_name}..."
        )

        predictions = run_model(
            model_name,
            train_df,
            race_df,
        )

        metrics = evaluate_model(
            predictions
        )

        metrics["season"] = 2025
        metrics["race"] = race
        metrics["phase"] = phase
        metrics["model"] = model_name

        results.append(
            metrics
        )

        print(
            f"{model_name}: "
            f"F1={metrics['f1']:.4f}, "
            f"AUC="
            f"{metrics['auc'] if metrics['auc'] is not None else 'NA'}, "
            f"MRR={metrics['mrr']:.4f}, "
            f"Top3="
            f"{metrics['top3_accuracy']:.4f}"
        )

    # -----------------------------------------------------------------
    # QUALIFYING BASELINE
    # -----------------------------------------------------------------

    print(
        "\nRunning qualifying baseline..."
    )

    baseline_metrics = (
        evaluate_qualifying_baseline(
            race_df
        )
    )

    baseline_metrics["season"] = 2025
    baseline_metrics["race"] = race
    baseline_metrics["phase"] = phase
    baseline_metrics["model"] = (
        "qualifying_baseline"
    )

    results.append(
        baseline_metrics
    )

    print(
        f"qualifying_baseline: "
        f"F1={baseline_metrics['f1']:.4f}, "
        f"AUC="
        f"{baseline_metrics['auc'] if baseline_metrics['auc'] is not None else 'NA'}, "
        f"MRR={baseline_metrics['mrr']:.4f}, "
        f"Top3="
        f"{baseline_metrics['top3_accuracy']:.4f}"
    )

    return results


# =============================================================================
# RUN ONE PHASE
# =============================================================================

def run_phase(
    phase,
    train_df,
    test_races,
    all_2025_data,
):

    phase_results = []

    print("\n")
    print("=" * 80)

    print(
        f"{phase.upper()} PHASE"
    )

    print("=" * 80)

    print(
        "\nTraining records:",
        len(train_df)
    )

    print(
        "Training seasons:",
        sorted(
            train_df[
                "season"
            ].unique()
        ),
    )

    print(
        "Training race names:",
        train_df[
            "race"
        ].nunique(),
    )

    print(
        "\nTest races:"
    )

    for race in test_races:

        print(
            f"  - {race}"
        )

    for race in test_races:

        race_df = all_2025_data[
            all_2025_data[
                "race"
            ] == race
        ].copy()

        race_results = (
            evaluate_one_race(
                race=race,
                phase=phase,
                train_df=train_df,
                race_df=race_df,
            )
        )

        phase_results.extend(
            race_results
        )

    return pd.DataFrame(
        phase_results
    )


# =============================================================================
# PHASE SUMMARY
# =============================================================================

def create_phase_summary(
    race_results,
):

    if race_results.empty:

        return pd.DataFrame()

    summary = (
        race_results
        .groupby(
            [
                "phase",
                "model",
            ],
            as_index=False,
        )[
            METRIC_COLUMNS
        ]
        .mean(
            numeric_only=True
        )
    )

    return summary


# =============================================================================
# DATA COUNT TABLE
# =============================================================================

def create_data_count_table(
    early_train,
    mid_train,
    late_train,
    early_test,
    mid_test,
    late_test,
):

    def count_season_races(df):

        if df.empty:

            return 0

        return (
            df[
                [
                    "season",
                    "race",
                ]
            ]
            .drop_duplicates()
            .shape[0]
        )

    return pd.DataFrame(
        [

            {
                "phase":
                    "early",

                "training_data":
                    "2023 + 2024",

                "training_season_races":
                    count_season_races(
                        early_train
                    ),

                "training_records":
                    len(early_train),

                "test_races":
                    early_test[
                        "race"
                    ].nunique(),

                "test_records":
                    len(early_test),
            },

            {
                "phase":
                    "mid",

                "training_data":
                    "2023 + 2024 + "
                    "2025 R1-R8",

                "training_season_races":
                    count_season_races(
                        mid_train
                    ),

                "training_records":
                    len(mid_train),

                "test_races":
                    mid_test[
                        "race"
                    ].nunique(),

                "test_records":
                    len(mid_test),
            },

            {
                "phase":
                    "late",

                "training_data":
                    "2023 + 2024 + "
                    "2025 R1-R16",

                "training_season_races":
                    count_season_races(
                        late_train
                    ),

                "training_records":
                    len(late_train),

                "test_races":
                    late_test[
                        "race"
                    ].nunique(),

                "test_records":
                    len(late_test),
            },
        ]
    )


# =============================================================================
# SAVE PROGRESSION TABLES
# =============================================================================

def save_progression_tables(
    summary,
):

    for metric in METRIC_COLUMNS:

        progression = (
            summary.pivot(
                index="model",
                columns="phase",
                values=metric,
            )
        )

        progression = (
            progression.reindex(
                columns=[
                    "early",
                    "mid",
                    "late",
                ]
            )
        )

        output_path = os.path.join(
            RESULTS_DIR,
            f"2025_{metric}_progression.csv",
        )

        progression.to_csv(
            output_path
        )


# =============================================================================
# MAIN EVALUATION
# =============================================================================

def run_temporal_2025_evaluation():

    print("\n")
    print("=" * 80)

    print(
        "2025 TEMPORAL EVALUATION STUDY"
    )

    print("=" * 80)

    # -----------------------------------------------------------------
    # PHASES
    # -----------------------------------------------------------------

    phases = (
        get_evaluation_phases()
    )

    early_races = phases[
        "early"
    ]["test"]

    mid_races = phases[
        "mid"
    ]["test"]

    late_races = phases[
        "late"
    ]["test"]

    all_races = (
        early_races
        + mid_races
        + late_races
    )

    print(
        f"\n2025 races used: "
        f"{len(all_races)}"
    )

    # -----------------------------------------------------------------
    # RACE LISTS
    # -----------------------------------------------------------------

    print(
        "\nEARLY:"
    )

    for race in early_races:

        print(
            f"  {race}"
        )

    print(
        "\nMID:"
    )

    for race in mid_races:

        print(
            f"  {race}"
        )

    print(
        "\nLATE:"
    )

    for race in late_races:

        print(
            f"  {race}"
        )

    # -----------------------------------------------------------------
    # BASE TRAINING: 2023 + 2024
    # -----------------------------------------------------------------

    base_training = (
        build_base_training_data()
    )

    # -----------------------------------------------------------------
    # BUILD ALL 2025 DATA
    # -----------------------------------------------------------------

    all_2025_data = (
        build_all_2025_data(
            all_races
        )
    )

    # -----------------------------------------------------------------
    # EARLY
    # -----------------------------------------------------------------

    early_train = (
        base_training.copy()
    )

    early_test = all_2025_data[
        all_2025_data[
            "race"
        ].isin(
            early_races
        )
    ].copy()

    # -----------------------------------------------------------------
    # MID
    #
    # 2023 + 2024 + 2025 R1-R8
    # -----------------------------------------------------------------

    early_2025_training = (
        all_2025_data[
            all_2025_data[
                "race"
            ].isin(
                early_races
            )
        ].copy()
    )

    mid_train = pd.concat(
        [
            base_training,
            early_2025_training,
        ],
        ignore_index=True,
    )

    mid_test = all_2025_data[
        all_2025_data[
            "race"
        ].isin(
            mid_races
        )
    ].copy()

    # -----------------------------------------------------------------
    # LATE
    #
    # 2023 + 2024 + 2025 R1-R16
    # -----------------------------------------------------------------

    early_mid_2025_training = (
        all_2025_data[
            all_2025_data[
                "race"
            ].isin(
                early_races
                + mid_races
            )
        ].copy()
    )

    late_train = pd.concat(
        [
            base_training,
            early_mid_2025_training,
        ],
        ignore_index=True,
    )

    late_test = all_2025_data[
        all_2025_data[
            "race"
        ].isin(
            late_races
        )
    ].copy()

    # -----------------------------------------------------------------
    # PRINT SPLITS
    # -----------------------------------------------------------------

    print("\n")
    print("=" * 80)
    print(
        "TEMPORAL DATA SPLITS"
    )
    print("=" * 80)

    print(
        "\nEARLY"
    )

    print(
        "Training:",
        len(early_train),
        "records",
    )

    print(
        "Testing:",
        len(early_test),
        "records",
    )

    print(
        "\nMID"
    )

    print(
        "Training:",
        len(mid_train),
        "records",
    )

    print(
        "Testing:",
        len(mid_test),
        "records",
    )

    print(
        "\nLATE"
    )

    print(
        "Training:",
        len(late_train),
        "records",
    )

    print(
        "Testing:",
        len(late_test),
        "records",
    )

    # -----------------------------------------------------------------
    # RUN EARLY
    # -----------------------------------------------------------------

    early_results = run_phase(
        phase="early",
        train_df=early_train,
        test_races=early_races,
        all_2025_data=all_2025_data,
    )

    # -----------------------------------------------------------------
    # RUN MID
    # -----------------------------------------------------------------

    mid_results = run_phase(
        phase="mid",
        train_df=mid_train,
        test_races=mid_races,
        all_2025_data=all_2025_data,
    )

    # -----------------------------------------------------------------
    # RUN LATE
    # -----------------------------------------------------------------

    late_results = run_phase(
        phase="late",
        train_df=late_train,
        test_races=late_races,
        all_2025_data=all_2025_data,
    )

    # -----------------------------------------------------------------
    # COMBINE
    # -----------------------------------------------------------------

    race_results = pd.concat(
        [
            early_results,
            mid_results,
            late_results,
        ],
        ignore_index=True,
    )

    # -----------------------------------------------------------------
    # SAVE RACE-LEVEL RESULTS
    # -----------------------------------------------------------------

    race_results_path = os.path.join(
        RESULTS_DIR,
        "temporal_2025_race_results.csv",
    )

    race_results.to_csv(
        race_results_path,
        index=False,
    )

    # -----------------------------------------------------------------
    # PHASE SUMMARY
    # -----------------------------------------------------------------

    phase_summary = (
        create_phase_summary(
            race_results
        )
    )

    phase_summary_path = os.path.join(
        RESULTS_DIR,
        "temporal_2025_phase_summary.csv",
    )

    phase_summary.to_csv(
        phase_summary_path,
        index=False,
    )

    # -----------------------------------------------------------------
    # DATA COUNTS
    # -----------------------------------------------------------------

    data_counts = (
        create_data_count_table(
            early_train=early_train,
            mid_train=mid_train,
            late_train=late_train,
            early_test=early_test,
            mid_test=mid_test,
            late_test=late_test,
        )
    )

    data_counts_path = os.path.join(
        RESULTS_DIR,
        "2025_evaluation_data_counts.csv",
    )

    data_counts.to_csv(
        data_counts_path,
        index=False,
    )

    # -----------------------------------------------------------------
    # PROGRESSION TABLES
    # -----------------------------------------------------------------

    save_progression_tables(
        phase_summary
    )

    # -----------------------------------------------------------------
    # FINAL OUTPUT
    # -----------------------------------------------------------------

    print("\n")
    print("=" * 80)

    print(
        "2025 TEMPORAL EVALUATION COMPLETE"
    )

    print("=" * 80)

    print(
        "\nRace-level results:"
    )

    print(
        race_results_path
    )

    print(
        "\nPhase summary:"
    )

    print(
        phase_summary_path
    )

    print(
        "\nData counts:"
    )

    print(
        data_counts_path
    )

    print(
        "\nResults directory:"
    )

    print(
        RESULTS_DIR
    )

    print("\n")
    print("=" * 80)

    print(
        "PHASE SUMMARY"
    )

    print("=" * 80)

    print(
        phase_summary.to_string(
            index=False
        )
    )

    return (
        race_results,
        phase_summary,
        data_counts,
    )


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    run_temporal_2025_evaluation()