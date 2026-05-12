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
            temperature=0.5,
            max_tokens=2048,
            timeout=30,
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
        job_skills_raw   = candidate_profile.get("job_required_skills", [])
        job_skills       = job_skills_raw if isinstance(job_skills_raw, list) else []
        experience_level = candidate_profile.get("job_experience_level", "")
        min_education    = candidate_profile.get("job_min_education", "")

        # Build a clean, readable candidate profile for the prompt
        candidate_parts = []

        # Skills
        skills_raw = candidate_profile.get("skills", [])
        if isinstance(skills_raw, str):
            skills_raw = [s.strip() for s in skills_raw.split(",") if s.strip()]
        if skills_raw:
            candidate_parts.append(f"SKILLS: {', '.join(skills_raw)}")
        else:
            candidate_parts.append("SKILLS: Not listed")

        # Education
        edu = candidate_profile.get("education", {})
        if isinstance(edu, dict) and edu:
            edu_parts = []
            for k in ["level", "major", "university", "graduation_year"]:
                v = edu.get(k, "")
                if v:
                    edu_parts.append(f"{k.title()}: {v}")
            if edu_parts:
                candidate_parts.append("EDUCATION: " + " | ".join(edu_parts))

        # Work experience
        experiences = candidate_profile.get("work_experiences", [])
        if experiences and isinstance(experiences, list):
            exp_lines = []
            for exp in experiences[:5]:  # max 5 entries
                years = f"{exp.get('year_start', '')}-{exp.get('year_end', 'now')}"
                title = exp.get("title", "")
                company = exp.get("company_name", "")
                desc = exp.get("description", "")[:200]
                exp_lines.append(f"  - [{years}] {title} at {company}: {desc}")
            if exp_lines:
                candidate_parts.append("WORK EXPERIENCE:\n" + "\n".join(exp_lines))

        # Achievements
        achievements = candidate_profile.get("achievements", [])
        if achievements and isinstance(achievements, list):
            ach_lines = []
            for ach in achievements[:5]:
                title = ach.get("title", "")
                level = ach.get("level", "")
                typ = ach.get("type", "")
                ach_lines.append(f"  - {title} ({level} {typ})")
            if ach_lines:
                candidate_parts.append("ACHIEVEMENTS:\n" + "\n".join(ach_lines))

        # Org experience
        orgs = candidate_profile.get("organizational_experiences", [])
        if orgs and isinstance(orgs, list):
            org_lines = []
            for org in orgs[:3]:
                org_lines.append(f"  - {org.get('position', '')} at {org.get('organization', org.get('organization_name', ''))}")
            if org_lines:
                candidate_parts.append("ORGANIZATIONS:\n" + "\n".join(org_lines))

        # Summary
        summary = candidate_profile.get("summary", "")
        if summary:
            candidate_parts.append(f"SUMMARY: {summary}")

        candidate_text = "\n".join(candidate_parts) or "(No profile data provided)"

        prompt = f"""You are Chally AI, a senior HR specialist evaluating candidates for job openings. Score honestly — do NOT inflate scores.

JOB: {job_title}
Level: {experience_level or 'Not specified'}
Min Education: {min_education or 'Not specified'}
Required Skills: {", ".join(job_skills) if job_skills else "Not specified"}
Job Description: {job_description[:500]}

CANDIDATE: {candidate_name}
{candidate_text}

SCORING RUBRIC (100 pts total):
- skills_match (0-30): coverage of required skills. Partial credit for adjacent/related skills. 0 if no overlap.
- work_experience (0-25): relevance and seniority of past roles to the job. Years of relevant experience matter.
- education (0-15): meets education requirement. Field relevance bonus.
- achievements (0-15): awards, certifications, leadership, organizational roles relevant to job.
- profile_quality (0-15): clarity and completeness of the profile.

Rules:
- A candidate with matching skills AND relevant experience should score 60-80
- A strong candidate with excellent experience should score 70-90
- Only score 90+ for outstanding, highly relevant candidates
- Score 20 or below only for completely wrong candidates (wrong field entirely)
- confidence is your certainty: 0.7-0.95 for well-described profiles, 0.4-0.6 for thin profiles
- core_strength: one short phrase in English describing the candidate's strongest asset
- Return ONLY valid JSON, no markdown, no explanation:

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
