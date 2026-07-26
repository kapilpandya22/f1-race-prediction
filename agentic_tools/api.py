from fastapi import FastAPI
from pydantic import BaseModel

from agentic_tools.raceiq_agent import RaceIQAgent

app = FastAPI()

agent = RaceIQAgent()


@app.get("/")
def root():

    return {
        "status": "RaceIQ API running"
    }


class QuestionRequest(BaseModel):

    session_id: str
    question: str


@app.post("/ask")
def ask_question(req: QuestionRequest):

    answer = agent.ask(
        req.question,
        req.session_id
    )

    return {
        "answer": answer
    }