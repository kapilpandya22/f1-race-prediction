from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV


def train_logistic(X, y, sample_weight=None):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    base_model = LogisticRegression(
        C=0.5,
        penalty="l2",
        solver="lbfgs",
        max_iter=3000,
        class_weight="balanced",      # ✅ cleaner
        random_state=42,        # ✅ stability
        n_jobs=-1
    )

    model = CalibratedClassifierCV(
        base_model,
        method="sigmoid",
        cv=3
    )

    model.fit(X_scaled, y)

    return model, scaler


def predict_logistic(model, scaler, X):

    X_scaled = scaler.transform(X)

    return model.predict_proba(X_scaled)[:, 1]