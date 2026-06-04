import pandas as pd


def compute_driver_explanations(results_with_features, importance_df, feature_cols):

    coef_dict = dict(zip(importance_df["feature"], importance_df["value"]))

    explanations = []

    for _, row in results_with_features.iterrows():

        driver = row["driver"]
        contribs = {}

        for f in feature_cols:
            val = row[f]

            if pd.isna(val):
                val = 0

            coef = coef_dict.get(f, 0)

            contribs[f"{f}_contrib"] = round(val * coef, 4)

        # top features
        top_features = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        top_features_str = ", ".join([f"{k} ({v:.2f})" for k, v in top_features])

        explanations.append({
            "driver": driver,
            **contribs,
            "top_features": top_features_str
        })

    explanations_df = pd.DataFrame(explanations)

    final_df = results_with_features.merge(
        explanations_df,
        on="driver",
        how="left",
        suffixes=("", "_dup")
    )

    return final_df