from driver_analytics_tool import DriverAnalyticsTool

tool = DriverAnalyticsTool()

print(tool.get_championship_leader())
print(tool.get_most_wins())
print(tool.get_most_podiums())
print(tool.get_most_reliable_driver())
print(tool.get_most_consistent_driver())
print(tool.get_average_finish("RUS"))
print(tool.get_reliability("RUS"))