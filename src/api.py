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


app = FastAPI(title="CHALLY HR AI API", version="1.0.0")
assistant: ChallyAssistantV2 | None = None


def get_assistant() -> ChallyAssistantV2:
    global assistant
    if assistant is None:
        assistant = ChallyAssistantV2()
    return assistant


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


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
