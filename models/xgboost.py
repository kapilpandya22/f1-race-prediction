from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV


def train_xgb(X, y, sample_weight=None):

    # 1. Base model
    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        reg_alpha=0.1,
        random_state=42,
        eval_metric="logloss"   # 🔥 IMPORTANT
    )

    # 2. Calibration wrapper
    model = CalibratedClassifierCV(
        estimator=xgb_model,
        method="sigmoid",   # or "sigmoid" (faster)
        cv=3
    )

    # 3. Fit
    model.fit(X, y)

    return model


def predict_xgb(model, X):
    return model.predict_proba(X)[:, 1]