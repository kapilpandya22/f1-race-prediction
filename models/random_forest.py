from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV


def train_rf(X, y, sample_weight=None):

    base_model = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight=None,   # ✅ avoid double weighting
        random_state=42,
        n_jobs=-1
    )

    # ✅ Wrap with calibration (same as logistic style)
    model = CalibratedClassifierCV(
        base_model,
        method="sigmoid",   # Platt scaling
        cv=3
    )

    # ✅ IMPORTANT: pass sample weights
    model.fit(X, y, sample_weight=sample_weight)

    return model


def predict_rf(model, X):
    return model.predict_proba(X)[:, 1]