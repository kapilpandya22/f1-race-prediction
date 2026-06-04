import pandas as pd

def get_feature_importance(model, feature_cols):

    # ---------------------------
    # UNWRAP MODEL (if calibrated)
    # ---------------------------
    if hasattr(model, "calibrated_classifiers_"):
        base_model = model.calibrated_classifiers_[0].estimator
    else:
        base_model = model

    # ---------------------------
    # EXTRACT IMPORTANCE
    # ---------------------------
    if hasattr(base_model, "coef_"):
        coefs = base_model.coef_[0]
        type_ = "coef"

    elif hasattr(base_model, "feature_importances_"):
        coefs = base_model.feature_importances_
        type_ = "importance"

    else:
        raise ValueError("Model type not supported")

    # ---------------------------
    # FEATURE NAMES
    # ---------------------------
    feature_names = getattr(model, "feature_names_", feature_cols)

    if len(coefs) != len(feature_names):
        raise ValueError(
            f"Mismatch: {len(coefs)} vs {len(feature_names)} features"
        )

    df = pd.DataFrame({
        "feature": feature_names,
        "value": coefs,
        "type": type_
    })

    df["abs_value"] = df["value"].abs()
    df = df.sort_values("abs_value", ascending=False).reset_index(drop=True)

    return df