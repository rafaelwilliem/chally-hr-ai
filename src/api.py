import time
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .assistant_v2 import ChallyAssistantV2


class BaseAiRequest(BaseModel):
    request_id: str | None = None
    model_version: str | None = None
    payload: Dict[str, Any]


class JobsRecommendRequest(BaseModel):
    request_id: str | None = None
    model_version: str | None = None
    payload: Dict[str, Any]


def ok(request_id: str, data: Any, started_at: float) -> Dict[str, Any]:
    latency_ms = int((time.time() - started_at) * 1000)
    return {
        "status": "ok",
        "request_id": request_id,
        "data": data,
        "latency_ms": latency_ms,
    }


def err(request_id: str, code: str, message: str, retryable: bool = False) -> Dict[str, Any]:
    return {
        "status": "error",
        "request_id": request_id,
        "code": code,
        "message": message,
        "retryable": retryable,
    }


import os
import subprocess

def get_git_version() -> str:
    """Read the most recent git tag or fallback to 'dev'."""
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return tag.lstrip("v")  # remove 'v' prefix if present
    except Exception:
        return "1.0.0"

__version__ = get_git_version()

app = FastAPI(title="CHALLY HR AI API", version=__version__)
assistant: ChallyAssistantV2 | None = None


def get_assistant() -> ChallyAssistantV2:
    global assistant
    if assistant is None:
        assistant = ChallyAssistantV2()
    return assistant


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "ok", "service": "CHALLY HR AI", "version": "1.0.0"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/ping-ai")
def ping_ai() -> Dict[str, Any]:
    """Quick test: sends a minimal prompt to Groq and returns latency."""
    import time
    started = time.time()
    try:
        assistant = get_assistant()
        result = assistant._chat("Reply with just the word: OK")
        latency = round((time.time() - started) * 1000)
        return {"status": "ok", "groq_response": result.strip(), "latency_ms": latency}
    except Exception as e:
        return {"status": "error", "message": str(e), "latency_ms": round((time.time() - started) * 1000)}


@app.post("/ai/cv/rate")
def cv_rate(req: BaseAiRequest) -> Dict[str, Any]:
    """Rate candidate fit (HR Feature)."""
    started_at = time.time()
    request_id = req.request_id or str(uuid.uuid4())
    try:
        payload = req.payload
        data = get_assistant().rate_candidate(
            job_description=payload.get("job_description", ""),
            candidate_name=payload.get("candidate_name", "Candidate"),
            candidate_profile=payload.get("candidate_profile", {}),
        )
        return ok(request_id, data, started_at)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=err(request_id, "AI_RATE_FAILED", str(exc), True))


@app.post("/ai/candidate/summary")
def candidate_summary(req: BaseAiRequest) -> Dict[str, Any]:
    """Summarize candidate with pros, cons, and recommendation (HR Feature)."""
    started_at = time.time()
    request_id = req.request_id or str(uuid.uuid4())
    try:
        payload = req.payload
        data = get_assistant().summarize_candidate(
            job_description=payload.get("job_description", ""),
            candidate_name=payload.get("candidate_name", "Candidate"),
            candidate_profile=payload.get("candidate_profile", {}),
        )
        return ok(request_id, data, started_at)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=err(request_id, "AI_SUMMARY_FAILED", str(exc), True))


@app.post("/ai/jobs/recommend")
def jobs_recommend(req: JobsRecommendRequest) -> Dict[str, Any]:
    """Recommend jobs for user (User Feature)."""
    started_at = time.time()
    request_id = req.request_id or str(uuid.uuid4())
    try:
        payload = req.payload
        recommendations: List[Dict[str, Any]] = get_assistant().recommend_jobs_for_user(
            user_profile=payload.get("user_profile", {}),
            jobs=payload.get("jobs", []),
        )
        return ok(request_id, recommendations, started_at)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=err(request_id, "AI_JOBS_RECOMMEND_FAILED", str(exc), True))
