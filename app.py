from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


app = FastAPI(title="LifeFix AI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


class Problem(BaseModel):
    text: str


@app.get("/")
def home():
    return {
        "message": "Welcome to LifeFix AI 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "LifeFix AI is running"
    }


@app.post("/solve")
def solve_problem(problem: Problem):

    prompt = f"""
You are LifeFix AI, a helpful everyday life problem-solving assistant.

Give practical, clear and actionable advice.
Break complicated problems into simple steps.
Be supportive and concise.

Problem:
{problem.text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return {
        "problem": problem.text,
        "solution": response.text
    }