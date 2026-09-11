
import os
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# --------------------------------------------------
# APP
# --------------------------------------------------

app = FastAPI(title="LifeFix AI")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# GEMINI
# --------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add your Gemini API key."
    )

client = genai.Client(api_key=API_KEY)


# --------------------------------------------------
# DAILY REQUEST LIMIT
# --------------------------------------------------

DAILY_LIMIT = 50

request_count = 0
request_date = date.today()


def check_daily_limit():
    global request_count
    global request_date

    today = date.today()

    # Reset counter when a new day starts
    if today != request_date:
        request_count = 0
        request_date = today

    if request_count >= DAILY_LIMIT:
        return False

    return True


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ProblemRequest(BaseModel):
    text: str


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "LifeFix AI is running",
        "daily_limit": DAILY_LIMIT,
        "requests_used_today": request_count
    }


# --------------------------------------------------
# SOLVE PROBLEM
# --------------------------------------------------

@app.post("/solve")
def solve_problem(request: ProblemRequest):

    global request_count

    # Check empty problem
    if not request.text.strip():
        return {
            "solution": "Please tell me your problem first."
        }

    # Check 50 requests/day limit
    if not check_daily_limit():
        return {
            "solution": (
                "Daily request limit reached. "
                "LifeFix AI allows 50 requests per day. "
                "Please try again tomorrow."
            ),
            "limit_reached": True
        }

    prompt = f"""
You are LifeFix AI, a helpful everyday life problem-solving assistant.

The user will tell you a problem.

Give a practical and easy-to-understand solution.

Do not make the answer unnecessarily long.
Give clear steps when useful.
Be supportive and realistic.

User's problem:
{request.text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        request_count += 1

        solution = response.text

        return {
            "solution": solution,
            "limit": DAILY_LIMIT,
            "requests_used_today": request_count
        }

    except Exception as e:

        print("Gemini Error:", e)

        return {
            "solution": (
                "Sorry, LifeFix AI could not generate a solution right now. "
                "Please try again."
            ),
            "error": str(e)
        }
