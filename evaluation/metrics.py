from sklearn.metrics import accuracy_score, f1_score, log_loss, brier_score_loss
import numpy as np
from sklearn.metrics import roc_auc_score

def compute_accuracy(y_true, y_pred):

    return accuracy_score(y_true, y_pred)


def compute_f1(y_true, y_pred):

    return f1_score(y_true, y_pred, average="binary", zero_division=0)


def compute_log_loss(y_true, y_prob):

    y_true = np.array(y_true)

    # Prevent crash if only one class present
    if np.unique(y_true).shape[0] == 1:
        return None

    return log_loss(y_true, y_prob)


def compute_brier(y_true, y_prob):

    return brier_score_loss(y_true, y_prob)


def compute_mrr(df):

    df = df.sort_values(by="pred_rank_score", ascending=False).reset_index(drop=True)

    reciprocal_ranks = []

    for i, row in enumerate(df.itertuples(), start=1):
        if row.target_top3 == 1:
            reciprocal_ranks.append(1 / i)

    if len(reciprocal_ranks) == 0:
        return 0

    return np.mean(reciprocal_ranks)

def compute_top3_accuracy(df):

    # Top 3 predicted
    top3_pred = df.sort_values("pred_top3_prob", ascending=False).head(min(3, len(df)))

    # Actual top 3
    actual_top3 = df[df["target_top3"] == 1]

    hits = len(set(top3_pred["driver"]) & set(actual_top3["driver"]))

    return hits / min(3, len(df))


def compute_auc(y_true, y_prob):

    y_true = np.array(y_true)

    if len(y_true) == 0:
        return None

    if np.unique(y_true).shape[0] < 2:
        return None

    return roc_auc_score(y_true, y_prob)


def compute_top3_recall(df):

    actual_top3 = df[df["target_top3"] == 1]
    top3_pred = df.sort_values("pred_top3_prob", ascending=False).head(min(3, len(df)))

    hits = len(set(top3_pred["driver"]) & set(actual_top3["driver"]))

    if len(actual_top3) == 0:
        return 0

    return hits / len(actual_top3)

def compute_top3_precision(df):

    # sort by model ranking
    df_sorted = df.sort_values(by="pred_rank_score", ascending=False)

    # predicted top 3
    pred_top3 = set(df_sorted.head(3)["driver"])

    # actual top 3
    actual_top3 = set(df[df["target_top3"] == 1]["driver"])

    correct = len(pred_top3 & actual_top3)

    return correct / min(3, len(df))


def evaluate_model(df):
    
    df = df.copy() 
    missing = df["target_top3"].isna().sum()
    if missing > 0:
        print(f"⚠️ Dropping {missing} rows with missing targets")
    # ✅ REMOVE rows without target
    df = df.dropna(subset=["target_top3"])
    df["pred_rank_score"] = df["pred_top3_prob"]
    
    y_true = df["target_top3"].astype(int)
    y_prob = df["pred_top3_prob"]

    df_sorted = df.sort_values("pred_top3_prob", ascending=False)
    df["y_pred_top3"] = 0
    df.loc[df_sorted.head(3).index, "y_pred_top3"] = 1

    y_pred = df["y_pred_top3"]

    results = {
        "accuracy": compute_accuracy(y_true, y_pred),
        "f1": compute_f1(y_true, y_pred),
        "auc": compute_auc(y_true, y_prob),
        "log_loss": compute_log_loss(y_true, y_prob),
        "brier": compute_brier(y_true, y_prob),
        "mrr": compute_mrr(df),
        "top3_accuracy": compute_top3_accuracy(df),
        "top3_recall": compute_top3_recall(df),
        "top3_precision": compute_top3_precision(df)
    }

    return results