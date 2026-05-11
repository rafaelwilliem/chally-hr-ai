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
        job_title        = candidate_profile.get("job_title", "")
        job_skills       = candidate_profile.get("job_required_skills", [])
        experience_level = candidate_profile.get("job_experience_level", "")
        min_education    = candidate_profile.get("job_min_education", "")

        prompt = f"""You are Chally AI, a senior HR specialist. Score this candidate's fit for the job using the rubric below. Be honest, do not inflate scores. RESPOND IN ENGLISH ONLY.

JOB: {job_title} | Level: {experience_level} | Min Education: {min_education}
Required Skills: {", ".join(job_skills) if job_skills else "Not specified"}
Description: {job_description[:800]}

CANDIDATE: {candidate_name}
{json.dumps(candidate_profile, ensure_ascii=False)}

SCORING RUBRIC (100 pts total):
- skills_match (0-30): coverage of required skills, partial credit for adjacent skills
- work_experience (0-25): relevance of past roles, seniority match, years of experience
- education (0-15): meets min education requirement, field relevance
- achievements (0-15): awards, certs, leadership, org experience
- profile_quality (0-15): summary clarity, profile completeness

Rules: 70+ = strong candidate. Below 40 = poor fit. core_strength = one short phrase IN ENGLISH. confidence = 0.0-1.0.

Return ONLY valid JSON, no markdown:
{{"score_total":0,"score_breakdown":{{"skills_match":0,"work_experience":0,"education":0,"achievements":0,"profile_quality":0}},"reasoning":"2-3 sentence assessment in English","technical_reasoning":["point 1","point 2","point 3"],"core_strength":"phrase in English","confidence":0.0}}"""
        text = self._chat(prompt)
        payload = self._extract_json(text, default={}) or {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("score_total", 0)
        payload.setdefault("score_breakdown", {})
        payload.setdefault("reasoning", "No reasoning provided")
        payload.setdefault("technical_reasoning", [])
        payload.setdefault("core_strength", "N/A")
        payload.setdefault("confidence", 0.0)
        return payload

    def summarize_candidate(self, job_description: str, candidate_name: str, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        job_title = candidate_profile.get("job_title", "")

        prompt = f"""You are Chally AI, an HR specialist. Write a concise talent assessment for {candidate_name} applying for {job_title}. RESPOND IN ENGLISH ONLY.

Job: {job_description[:600]}
Candidate: {json.dumps(candidate_profile, ensure_ascii=False)}

Return ONLY valid JSON, no markdown:
{{"pros":["strength 1","strength 2","strength 3"],"cons":["gap 1","gap 2"],"short_summary":"2-3 sentence paragraph about overall fit in English","recommendation":"Recommended"}}

recommendation must be one of: "Highly Recommended", "Recommended", "Consider", "Not Recommended"
pros: 3-5 specific strengths for this role IN ENGLISH. cons: 2-4 honest gaps IN ENGLISH."""
        text = self._chat(prompt)
        payload = self._extract_json(text, default={}) or {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("pros", [])
        payload.setdefault("cons", [])
        payload.setdefault("short_summary", "No summary available.")
        payload.setdefault("recommendation", "Consider")
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
