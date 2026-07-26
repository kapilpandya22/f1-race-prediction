from intent_parser import IntentParser

parser = IntentParser()

questions = [
    "Who is predicted to win Australia?",
    "Why is George Russell ranked first?",
    "Which model has best AUC?",
    "Who won Australia?"
]

for q in questions:

    print("\nQUESTION:")
    print(q)

    print("\nPARSED:")
    print(parser.parse(q))