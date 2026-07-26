import json
from openai import OpenAI


class IntentParser:

    def __init__(self):

        self.client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )

    def parse(self, question):

        prompt = f"""
You are an intent classifier for an F1 prediction assistant.

Supported intents:

1. prediction
   Example:
   "Who is predicted to win Australia?"

2. driver_explanation
   use this intent whenever the user asks WHY a driver
received a prediction, ranking, probability, or position.

Examples:

"Why is George Russell ranked first?"

"Why was Hamilton predicted to finish on the podium?"

"Why is Antonelli ranked ahead of Norris?"

"Explain Hamilton's prediction."

"Explain Russell's prediction for Australia."

"Explain George Russell's podium probability."

Questions beginning with:

Why was...
Why is...
Explain...

should usually return:

intent = driver_explanation

3. benchmark
   Example:
   "Which model has best AUC?"

4. actual_results
   Example:
   "Who won Australia?"
   "What was the podium in Australia?"

5. feature_importance
   Examples:
   "What are the most important features for Australia?"
   "Which factors influence the prediction most?"
   "Show feature importance for the logistic model."

6. analytics_query

Examples:
"How has Antonelli performed this season?"
"Summarize George Russell's season."
"Describe Ferrari's season."
"Tell me about Norris's recent form."
"How has McLaren performed so far?"
"Show Antonelli's recent races."
For open-ended analytical questions, use:
intent = analytics_query 
 
7. driver_analytics
For driver_analytics questions, return one of:

leader
wins
podiums
reliability
average_finish
points
consistency
positions_gained
standings
Examples:

"Who is leading the Drivers Championship?"
metric = leader

"Who has the most wins?"
metric = wins

"Who has the most podiums?"
metric = podiums

"Who is the most reliable driver?"
metric = reliability

"What is George Russell's average finishing position?"
metric = average_finish
"Show Drivers Championship standings" metric = standings
"Current standings" metric = standings
"Top drivers" metric = standings


Return ONLY valid JSON.

8. team_analytics.
Examples:
"Which team leads the Constructors Championship?"
"How many points has Ferrari scored?"
"Which team has the most wins?"
"Which team has the most podiums?"
"Which team is the most reliable?"
9. Comparison
Examples:
"Compare Russell and Antonelli"
"Compare Hamilton and Leclerc"
"Compare Ferrari and Mercedes"
"Which Mercedes driver has performed better?"

Schema:

{{
    "intent": "",
    "race": "",
    "driver": "",
    "driver2": "",
    "team": "",
    "team2": "",
    "model": "",
    "metric": ""
}}



Question:
{question}
"""

        response = self.client.chat.completions.create(
            model="qwen2.5-3b-instruct.gguf",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except:
            return {
                "intent": "unknown",
                "race": None,
                "driver": None,
                "model": None
            }