from pathlib import Path
from path_resolver import get_file_path

path = get_file_path(
    race_name="Australian Grand Prix",
    model="logistic",
    file_type="predictions"
)

print("Path:", path)
print("Exists:", Path(path).exists())