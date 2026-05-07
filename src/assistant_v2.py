import json
import re
from typing import List, Dict, Any

try:
    from . import config
except ImportError:
    import config


class ChallyAssistantV2:
    def __init__(self) -> None:
        self.client = config.get_client()
        self.model_name = config.MODEL_NAME

    def _chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    def _extract_json(self, text: str, default: Any = None) -> Any:
        normalized = text.strip()
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            pass
        for pattern in [r'\{.*\}', r'\[.*\]']:
            match = re.search(pattern, normalized, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return default

    def rate_candidate(self, job_description: str, candidate_name: str, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""You are Chally AI, an HR Intelligence Specialist.
Evaluate candidate fit based on work experience, skills, and summary.

[JOB DESCRIPTION]
{job_description}

[CANDIDATE NAME]
{candidate_name}

[CANDIDATE PROFILE JSON]
{json.dumps(candidate_profile, ensure_ascii=False)}

Return ONLY a JSON object (no markdown, no explanation):
{{
  "score_total": 0,
  "reasoning": "Why this candidate fits",
  "technical_reasoning": ["point 1", "point 2", "point 3"],
  "core_strength": "string",
  "confidence": 0.0
}}"""
        text = self._chat(prompt)
        payload = self._extract_json(text, default={}) or {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("score_total", 0)
        payload.setdefault("reasoning", "No reasoning provided")
        payload.setdefault("technical_reasoning", [])
        payload.setdefault("core_strength", "N/A")
        payload.setdefault("confidence", 0.0)
        return payload

    def recommend_jobs_for_user(self, user_profile: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompt = f"""You are Chally AI recommendation engine.
Match candidate profile against jobs and return match scores.

[USER PROFILE]
{json.dumps(user_profile, ensure_ascii=False)}

[JOB LIST]
{json.dumps(jobs, ensure_ascii=False)}

Return ONLY a JSON array (no markdown, no explanation):
[
  {{"job_id": 1, "match_score": 0, "reasoning": "Why this job fits"}}
]"""
        text = self._chat(prompt)
        payload = self._extract_json(text, default=[]) or []
        if not isinstance(payload, list):
            payload = []
        normalized = [
            {
                "job_id": item.get("job_id"),
                "match_score": int(item.get("match_score", 0)),
                "reasoning": item.get("reasoning", "No reasoning provided"),
            }
            for item in payload if isinstance(item, dict)
        ]
        return sorted(normalized, key=lambda x: x["match_score"], reverse=True)
