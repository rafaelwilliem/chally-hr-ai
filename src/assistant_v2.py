import os
import json
import re
from typing import List, Dict, Any
from google import genai

try:
    from . import config
except ImportError:
    import config

class ChallyAssistantV2:
    """HR Intelligence Assistant (v2) focusing on Candidate Scoring and Job Recommendation."""

    def __init__(self) -> None:
        """Initializes the generative model."""
        self.client = config.get_client()
        self.model_name = config.MODEL_NAME

    def _extract_json(self, text: str, default: Any = None) -> Any:
        """Extract and parse JSON object/array from model output safely."""
        normalized = text.strip()
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            pass

        object_match = re.search(r'\{.*\}', normalized, re.DOTALL)
        if object_match:
            try:
                return json.loads(object_match.group(0))
            except json.JSONDecodeError:
                pass

        array_match = re.search(r'\[.*\]', normalized, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group(0))
            except json.JSONDecodeError:
                pass

        return default

    def rate_candidate(
        self,
        job_description: str,
        candidate_name: str,
        candidate_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Rate candidate fit against job description (HR feature).
        
        Evaluates based on experience, skills, and summary.
        Provides reasoning for the match.
        """
        prompt = f"""
        You are Chally AI, an HR Intelligence Specialist.
        Evaluate candidate fit based on:
        1. Work Experience (Pengalaman Kerja)
        2. Skills (Keahlian)
        3. Brief Self-Summary (Deskripsi Singkat Data Diri)

        [JOB DESCRIPTION]
        {job_description}

        [CANDIDATE NAME]
        {candidate_name}

        [CANDIDATE PROFILE JSON]
        {json.dumps(candidate_profile, ensure_ascii=False)}

        TASK:
        - Give total fit score 0-100.
        - Provide 'Technical Reasoning' (Why is this candidate a match for this position?).
        - Provide core_strength.

        STRICT RULES:
        - ALL reasoning, summary, and descriptions MUST be in English.

        OUTPUT JSON:
        {{
          "score_total": 0,
          "reasoning": "string (Why this candidate fits this position)",
          "technical_reasoning": ["point 1", "point 2", "point 3"],
          "core_strength": "string",
          "confidence": 0.0
        }}
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        payload = self._extract_json(response.text, default={}) or {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("score_total", 0)
        payload.setdefault("reasoning", "No reasoning provided")
        payload.setdefault("technical_reasoning", [])
        payload.setdefault("core_strength", "N/A")
        payload.setdefault("confidence", 0.0)
        return payload

    def recommend_jobs_for_user(self, user_profile: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend top jobs for a user profile (User feature).
        
        Uses the same evaluation logic as HR to ensure consistency.
        """
        prompt = f"""
        You are Chally AI recommendation engine.
        Match candidate profile against a list of jobs using HR-standard scoring logic.

        [USER PROFILE]
        {json.dumps(user_profile, ensure_ascii=False)}

        [JOB LIST]
        {json.dumps(jobs, ensure_ascii=False)}

        TASK:
        - Evaluate the user profile against each job.
        - Return a match score and reasoning for each.

        STRICT RULES:
        - ALL reasoning and descriptions MUST be in English.

        OUTPUT JSON ARRAY:
        [
          {{
            "job_id": 1,
            "match_score": 0,
            "reasoning": "Why this job fits the user profile"
          }}
        ]
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        payload = self._extract_json(response.text, default=[]) or []
        if not isinstance(payload, list):
            payload = []
        normalized = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "job_id": item.get("job_id"),
                "match_score": int(item.get("match_score", 0)),
                "reasoning": item.get("reasoning", "No reasoning provided"),
            })
        
        # Sort by match score descending
        normalized = sorted(normalized, key=lambda x: x['match_score'], reverse=True)
        return normalized
