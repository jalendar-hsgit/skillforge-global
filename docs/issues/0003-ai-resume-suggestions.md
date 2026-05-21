# ISSUE 0003 — AI Resume Suggestions Endpoint

Priority: High

Goal:
Provide an endpoint to generate AI-powered bullet points or phrasing suggestions for resume sections (work experience, summary, achievements) using the project's LLM provider abstraction.

Endpoint:
- `POST /api/v1x/resumes/{resume_id}/suggestions`
  - Body: {"section": "work_experience"|"summary"|"achievement", "context": "current text or bullet points"}
  - Returns: {"suggestions": ["...", "..."]}

Implementation notes:
- Use `app/services/llm_provider.py` abstraction.
- Rate limit requests per user.
- Store suggestion history optionally for analytics.
- Return multiple suggestions (3) and allow temperature param.

Acceptance Criteria:
- Generates useful suggestions within reasonable latency (3-5s)
- Respect rate limits and authentication
- Frontend can display suggestions and insert them into editor
