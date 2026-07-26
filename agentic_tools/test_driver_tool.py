# test_driver_tool.py

from driver_tool import DriverTool

tool = DriverTool()

summary = tool.get_driver_summary(
    race_name="Australian Grand Prix",
    driver="RUS",
    model="logistic"
)

print(summary)