from data.calendar import F1_2026_SCHEDULE
from pipelines.date_logic import get_race_lists
import pandas as pd

pred, met = get_race_lists(F1_2026_SCHEDULE)

# ---------------------------
# DEBUG PRINTS (ADD THIS)
# ---------------------------
print("\n=== PREDICTION RACES ===")
print(pred)

print("\n=== METRICS RACES ===")
print(met)

# ---------------------------
# DATAFRAME (for Power BI)
# ---------------------------
df_pred = pd.DataFrame({
    "race": pred,
    "type": "prediction"
})

df_met = pd.DataFrame({
    "race": met,
    "type": "metrics"
})

final = pd.concat([df_pred, df_met], ignore_index=True)

