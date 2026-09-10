"""
PromptCraft v2 - Niche-driven Role/Context/Task/Format prompt tool
Calls Google Gemini API and returns the response.

Setup:
1. Get a free Gemini API key: https://aistudio.google.com/apikey
2. Create a set-gemini-key.env file next to this script with:
       GEMINI_API_KEY=your_key_here
3. Run:  uvicorn app:app --reload
4. Open: http://127.0.0.1:8000
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv("set-gemini-key.env")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in a set-gemini-key.env file before running.")

print("GEMINI_API_KEY loaded for this session.")

client = genai.Client(api_key=API_KEY)

app = FastAPI(title="PromptCraft")


# ---------------------------------------------------------------------------
# Niche configuration — add a new niche by adding one entry here.
# Nothing else in the backend needs to change.
# ---------------------------------------------------------------------------
NICHES = {
    "sql": {
        "label": "SQL Query / Schema Assistant",
        "default_role": "Senior database architect reviewing SQL Server schemas and queries",
        "tasks": [
            "Review this schema for normalization issues",
            "Optimize this query",
            "Suggest indexes",
            "Explain this execution plan",
        ],
        "context_placeholder": "Paste your CREATE TABLE statement(s) or SQL query here...",
        "default_format": "Bulleted list, technical tone, include the corrected T-SQL where relevant",
        "system_instructions": (
            "You are a senior SQL Server database architect. Use correct T-SQL syntax. "
            "Be specific about index names, data types, and normal forms where relevant. "
            "If you suggest a rewrite, show the full corrected SQL in a code block."
        ),
    },
    "etl": {
        "label": "ETL Error Translator",
        "default_role": "Senior data engineer debugging Azure Data Factory / SSIS pipeline errors",
        "tasks": [
            "Explain this error in plain English",
            "Suggest a likely root cause",
            "Suggest a fix",
        ],
        "context_placeholder": "Paste the error message or stack trace here...",
        "default_format": "Plain English explanation first, then a short bulleted fix list",
        "system_instructions": (
            "You are a senior data engineer experienced with Azure Data Factory, SSIS, and T-SQL "
            "stored procedures. Translate cryptic pipeline errors into plain English, then give "
            "concrete, actionable next steps."
        ),
    },
    "arch_doc": {
        "label": "Architecture Doc Generator",
        "default_role": "Solutions architect writing a formal architecture decision record",
        "tasks": [
            "Turn these notes into an Architecture Decision Record (ADR)",
            "Turn these notes into a stakeholder-ready summary",
            "Turn these notes into a technical design document",
        ],
        "context_placeholder": "Paste your rough technical notes here...",
        "default_format": "Formal document structure with headings, professional tone",
        "system_instructions": (
            "You are a solutions architect producing enterprise-grade documentation. "
            "Structure output with clear headings. Be precise and avoid vague language."
        ),
    },
    "resume": {
        "label": "Resume Repositioning",
        "default_role": "Career coach repositioning a technical resume for a target role",
        "tasks": [
            "Rewrite this bullet point for a new target role",
            "Suggest which existing experience best supports this target role",
            "Draft a professional summary for this target role",
        ],
        "context_placeholder": "Paste the resume section and your target role here...",
        "default_format": "Concise, resume-ready bullet points",
        "system_instructions": (
            "You are an experienced technical career coach. Reposition real experience "
            "truthfully for a new target role — never invent experience that wasn't described."
        ),
    },
    "cloud_cost": {
        "label": "Cloud Cost Report Narrator",
        "default_role": "Cloud architect producing an executive cost report",
        "tasks": [
            "Summarize this cost data for executives",
            "Identify optimization opportunities",
            "Explain the cost trend in plain English",
        ],
        "context_placeholder": "Paste your billing data or cost summary here...",
        "default_format": "Executive summary, plain English, one key recommendation highlighted",
        "system_instructions": (
            "You are a cloud architect experienced with GCP and Azure cost governance. "
            "Translate raw billing data into an executive-readable narrative with a clear "
            "recommendation."
        ),
    },
}


class PromptRequest(BaseModel):
    niche: str
    role: str
    context: str
    task: str
    format_tone: str


def build_prompt(niche_config: dict, data: PromptRequest) -> str:
    """Assemble the four inputs plus niche system instructions into one prompt."""
    return f"""{niche_config['system_instructions']}

You are acting in the following role: {data.role}

Context:
{data.context}

Task:
{data.task}

Desired format / tone:
{data.format_tone}

Now complete the task above, following the role, context, and format/tone exactly."""


@app.get("/niches")
def get_niches():
    """Return the niche config so the frontend can build its dropdowns."""
    return NICHES


@app.post("/generate")
def generate(req: PromptRequest):
    if req.niche not in NICHES:
        raise HTTPException(status_code=400, detail="Unknown niche.")
    if not req.role.strip() or not req.task.strip():
        raise HTTPException(status_code=400, detail="Role and Task are required.")

    niche_config = NICHES[req.niche]
    prompt = build_prompt(niche_config, req)

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {e}")

    return {"result": response.text}


# Serve the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
