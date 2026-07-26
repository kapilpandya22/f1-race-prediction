from agentic_tools.raceiq_agent import RaceIQAgent


agent = RaceIQAgent()

while True:

    question = input(
        "\nAsk RaceIQ: "
    )

    if question.lower() == "exit":
        break

    answer = agent.ask(
        question
    )

    print("\nRaceIQ:")
    print(answer)