# CHALLY HR AI API Contract (Simplified)

All endpoints use JSON and return a common envelope.

## Common Request Envelope

```json
{
  "request_id": "optional-client-request-id",
  "payload": {}
}
```

## Common Success Envelope

```json
{
  "status": "ok",
  "request_id": "uuid-or-forwarded-id",
  "data": {},
  "latency_ms": 123
}
```

## Endpoints

### `POST /ai/cv/rate` (HR Feature)
Rate candidate fit against a job based on work experience, skills, and summary.

`payload`:
- `job_description` (string)
- `candidate_name` (string)
- `candidate_profile` (object)

`data`:
- `score_total` (0-100)
- `reasoning` (string) - Why the candidate fits this position.
- `technical_reasoning` (string[]) - Key matching points.
- `core_strength` (string)

### `POST /ai/jobs/recommend` (User Feature)
Recommend top jobs for a user profile using HR-standard scoring logic.

`payload`:
- `user_profile` (object)
- `jobs` (array of objects with `id` and description)

`data`:
- array of:
  - `job_id` (number)
  - `match_score` (0-100)
  - `reasoning` (string)
