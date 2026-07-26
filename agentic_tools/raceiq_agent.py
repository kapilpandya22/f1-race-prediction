# agentic_tools/raceiq_agent.py

from openai import OpenAI

from agentic_tools.prediction_tool import PredictionTool
from agentic_tools.driver_tool import DriverTool
from agentic_tools.benchmark_tool import BenchmarkTool
from agentic_tools.feature_importance_tool import FeatureImportanceTool
from agentic_tools.golden_dataset_tool import GoldenDatasetTool
from agentic_tools.intent_parser import IntentParser
from agentic_tools.driver_analytics_tool import DriverAnalyticsTool
from agentic_tools.mapping import (
    resolve_driver,
    resolve_race,
    resolve_team,
    get_driver_name
)
from agentic_tools.team_analytics_tool import TeamAnalyticsTool
from agentic_tools.analytics_rag import AnalyticsRAG

class RaceIQAgent:

    def __init__(self):

        self.client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )

        self.prediction_tool = PredictionTool()
        self.driver_tool = DriverTool()
        self.benchmark_tool = BenchmarkTool()
        self.feature_tool = FeatureImportanceTool()
        self.golden_tool = GoldenDatasetTool()
        self.intent_parser = IntentParser()
        self.driver_analytics_tool = (
        DriverAnalyticsTool() 
        )
        self.team_analytics_tool = TeamAnalyticsTool()
        self.analytics_rag = AnalyticsRAG()
        # Session memory
        self.sessions = {}

    def ask(
        self,
        question,
        session_id="default"
    ):

        # -------------------------
        # Session Memory
        # -------------------------

        if session_id not in self.sessions:

            self.sessions[
                session_id
            ] = []

        history = self.sessions[
            session_id
        ]

        history.append(
            {
                "role": "user",
                "content": question
            }
        )

        recent_history = history[-6:]

        history_text = "\n".join(
            [
                f"{m['role']}: {m['content']}"
                for m in recent_history
            ]
        )

        # -------------------------
        # Intent Parsing
        # -------------------------

        parsed = self.intent_parser.parse(
            f"""
Conversation:

{history_text}

Current Question:

{question}
"""
        )

        print("\nParsed Intent:")
        print(parsed)

        intent = parsed.get("intent")

        race = resolve_race(
            parsed.get("race")
        )

        driver = resolve_driver(
            parsed.get("driver")
        )
        
        team = resolve_team(
            parsed.get("team")
        )

        model = (
            parsed.get("model")
            or "logistic"
        )

        metric = (
            parsed.get("metric")
            or "auc"
        )

        context = ""

        # -------------------------
        # Prediction
        # -------------------------

        if intent == "prediction":

            if race is None:
                race = "Australian Grand Prix"

            predictions = (
                self.prediction_tool
                .get_top_predictions(
                    race_name=race,
                    model=model,
                    top_n=3
                )
            )

            context = f"""
Race:
{race}

Model:
{model}

Predicted Podium:

{predictions}
"""

        # -------------------------
        # Driver Explanation
        # -------------------------

        elif intent == "driver_explanation":

            if race is None:
                race = "Australian Grand Prix"

            if driver is None:

                answer = (
                    "Could not determine "
                    "which driver you mean."
                )

                history.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                return answer

            summary = (
                self.driver_tool
                .get_driver_summary(
                    race_name=race,
                    driver=driver,
                    model=model
                )
            )

            features = (
                self.feature_tool
                .get_top_features(
                    race,
                    model,
                    5
                )
            )

            feature_names = [
                f["feature"]
                for f in features
            ]

            context = f"""
Driver Prediction Data:

{summary}

Most Important Features:

{feature_names}
"""

        # -------------------------
        # Feature Importance
        # -------------------------

        elif intent == "feature_importance":

            if race is None:
                race = "Australian Grand Prix"

            features = (
                self.feature_tool
                .get_top_features(
                    race,
                    model,
                    10
                )
            )

            context = f"""
Race:
{race}

Model:
{model}

Top Features:

{features}
"""

        # -------------------------
        # Benchmark
        # -------------------------

        elif intent == "benchmark":

            benchmark = (
                self.benchmark_tool
                .get_metric_leader(
                    metric
                )
            )

            context = f"""
Metric:
{metric}

Benchmark Result:

{benchmark}
"""

        # -------------------------
        # Actual Results
        # -------------------------

        elif intent == "actual_results":

            if race is None:
                race = "Australian Grand Prix"

            podium = (
                self.golden_tool
                .get_podium(
                    race
                )
            )

            context = f"""
Race:
{race}

Actual Podium:

{podium}
"""
        elif intent == "driver_analytics":

            if metric == "leader":

                result = (
                self.driver_analytics_tool
                .get_championship_leader()
                )
                
                driver_name = get_driver_name(
                        result["driver"] )

                answer = (
                f"{driver_name} leads the "
                f"Drivers Championship with "
                f"{result['points']} points."
                )

                history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
                )

                return answer

            elif metric == "wins":

                context = str(
                    self.driver_analytics_tool
                    .get_most_wins()
                )

            elif metric == "podiums":

                context = str(
                    self.driver_analytics_tool
                    .get_most_podiums()
                )

            elif metric == "reliability":

                context = str(
                    self.driver_analytics_tool
                    .get_most_reliable_driver()
                )

            elif metric == "average_finish":

                context = str(
                    self.driver_analytics_tool
                    .get_average_finish(
                        driver
                    )
                ) 
            elif metric == "standings":

                standings = (
                    self.driver_analytics_tool
                    .get_driver_standings()
                )

                context = standings[:10]          
        # -------------------------
        # Unknown
        # -------------------------
        elif intent == "team_analytics":

            if metric == "leader":

                context = str(
                    self.team_analytics_tool
                    .get_constructor_leader()
                )

            elif metric == "wins":

                context = str(
                    self.team_analytics_tool
                    .get_most_wins_team()
                )

            elif metric == "podiums":

                context = str(
                    self.team_analytics_tool
                    .get_most_podiums_team()
                )

            elif metric == "reliability":

                context = str(
                    self.team_analytics_tool
                    .get_most_reliable_team()
                )

            elif metric == "points":

                context = str(
                    self.team_analytics_tool
                    .get_team_points(
                        team
                    )
                )
        elif intent == "analytics_query":

            context = (
                self.analytics_rag
                .get_general_context(
                    driver=driver,
                    team=team,
                    race=race
                )
            )      
        else:

            answer = (
                "I could not understand "
                "the question. Kya bol rha budbak"
            )

            history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            return answer

        # -------------------------
        # Final LLM Prompt
        # -------------------------
        print("\nCONTEXT:")
        print(context)
        prompt = f"""
You are RaceIQ, an F1 analytics assistant.

Use ONLY the supplied data.

If information is not present in the data,
say:

'The requested information is not available.'

Do NOT use external Formula 1 knowledge.
Do NOT use knowledge from previous seasons.
Do NOT invent facts.

Answer ONLY using the provided context.

Question:
{question}

Context:
{context}

Rules:
- Do not invent facts.
- Be concise.
- Mention driver names when possible.
- Use bullet points when appropriate.
"""

        response = (
            self.client.chat.completions.create(
                model="qwen2.5-3b-instruct.gguf",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer