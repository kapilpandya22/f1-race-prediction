from agentic_tools.comparison_tool import (
    ComparisonTool
)

tool = ComparisonTool()

print(
    tool.compare_drivers(
        "RUS",
        "ANT"
    )
)

print(
    tool.compare_teams(
        "Mercedes",
        "Ferrari"
    )
)