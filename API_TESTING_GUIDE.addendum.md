# Addendum: Quiz AI Generation (v1)

New endpoints added on Nov 3, 2025 to support dynamic AI-style quizzes and improved UX.

## Generate AI Quiz
POST http://localhost:8001/api/v1/quizzes/generate
Content-Type: application/json

{
  "topic": "python ai",
  "difficulty": "medium", // easy | medium | hard
  "num_questions": 6,
  "options_per_question": 4,
  "time_limit_minutes": 10
}

Response (QuizEnvelope with answerIndex embedded):
- id: string (starts with "ai-")
- title: string
- questions: [{ id, type: "mcq", text, options[], answerIndex, explanation? }]

## Submit AI Quiz
POST http://localhost:8001/api/v1/quizzes/submit-ai
Content-Type: application/json
Authorization: Bearer <token> (optional)

{
  "path": "python-ai",
  "questions": [/* same shape returned by generate */],
  "answers": [ { "id": "ai-python-ai-1", "answerIndex": 2 }, ... ]
}

Response: { score, total, results: [{ id, correct, correctIndex, explanation }] }

## Frontend proxies
- POST /api/quizzes/generate → backend /api/v1/quizzes/generate
- POST /api/quizzes/submit-ai → backend /api/v1/quizzes/submit-ai
- GET  /api/quizzes/status → backend /api/v1/quizzes/status

## UI behavior
- On /quiz/[slug], if a static quiz isn’t found, the page auto-generates an AI quiz for the slug topic and enables real-time feedback, a countdown timer, and progress bar.
- Submissions for AI quizzes use /api/quizzes/submit-ai; static quizzes continue to use /api/v1/quizzes/submit.
