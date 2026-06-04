import os
import json
import pandas as pd

BASE_PATH = "outputs/analysis"


def load_all_metrics():
    all_metrics = []

    for model_name in os.listdir(BASE_PATH):

        model_path = os.path.join(BASE_PATH, model_name)

        if not os.path.isdir(model_path):
            continue

        # iterate over races
        for race_folder in os.listdir(model_path):

            race_path = os.path.join(model_path, race_folder)
            metrics_path = os.path.join(race_path, "metrics.json")

            if os.path.exists(metrics_path):

                with open(metrics_path, "r") as f:
                    data = json.load(f)

                    # ✅ attach model name
                    data["model"] = model_name

                    if data.get("accuracy") is not None:
                        all_metrics.append(data)

    return pd.DataFrame(all_metrics)

def main():
    df = load_all_metrics()

    if df.empty:
        print("⚠️ No valid metrics found")
        return

    print("\n=== ALL RESULTS ===")
    print(df)

    # ---------------------------
    # SAVE PER MODEL
    # ---------------------------
    for model_name in df["model"].unique():

        model_df = df[df["model"] == model_name]

        model_dir = os.path.join(BASE_PATH, model_name)
        os.makedirs(model_dir, exist_ok=True)

        # full results
        model_df.to_csv(
            os.path.join(model_dir, "all_results.csv"),
            index=False
        )

        # mean metrics
        mean_df = model_df.mean(numeric_only=True)
        mean_df = mean_df.to_frame(name="value").reset_index()
        mean_df.columns = ["metric", "value"]

        mean_df.to_csv(
            os.path.join(model_dir, "mean_metrics.csv"),
            index=False
        )

        print(f"\n✅ Saved analysis for {model_name}")

    print("\n🎯 All analysis saved in outputs/analysis/")

if __name__ == "__main__":
    main()