from analytics_rag import AnalyticsRAG

rag = AnalyticsRAG()

print(
    rag.get_driver_context(
        "ANT"
    )
)

print(
    rag.compare_drivers_context(
        "ANT",
        "RUS"
    )
)