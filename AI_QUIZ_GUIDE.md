# AI Quiz Generation - Advanced Features

**Added:** November 3, 2025

## Overview
Enhanced quiz system with real LLM-backed generation, streaming, adaptive difficulty, and persistent templates.

## Features

### 1. LLM Provider Integration
Multi-provider support with automatic fallback to deterministic generation if LLM fails.

**Supported Providers:**
- **OpenAI** (gpt-4o-mini, gpt-4, gpt-3.5-turbo)
- **Anthropic** (claude-3-5-sonnet, claude-3-opus, claude-3-haiku)
- **Azure OpenAI** (your deployed models)
- **Ollama** (local/self-hosted llama3, mistral, etc.)

**Configuration:**
```bash
# Set in backend/.env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**API Endpoint:**
```http
POST /api/v1/quizzes/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "topic": "python async programming",
  "difficulty": "medium",
  "num_questions": 5,
  "options_per_question": 4,
  "save": true,  // Save to user's library
  "session_id": 123  // Optional: for adaptive difficulty
}
```

**Response:**
```json
{
  "id": "ai-python-async-1730678400",
  "title": "Python Async Programming — Medium Quiz",
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "text": "What is the primary benefit of async/await?",
      "options": ["...", "...", "...", "..."],
      "answerIndex": 2,
      "explanation": "Async/await allows..."
    }
  ],
  "saved_id": 42  // If save=true
}
```

### 2. Streaming Generation (SSE)
Questions appear in real-time as the LLM generates them.

**Backend Endpoint:**
```http
GET /api/v1/quizzes/generate-stream?topic=react&difficulty=hard&num_questions=6
Authorization: Bearer <token>
Accept: text/event-stream
```

**Frontend API Route:**
```http
GET /api/quizzes/generate-stream?topic=react&difficulty=hard&num_questions=6
```

**SSE Event Format:**
```javascript
// Metadata event
data: {"type":"metadata","id":"ai-react-123","title":"React — Hard Quiz"}

// Question events
data: {"type":"question","data":{"id":"q1","type":"mcq",...}}
data: {"type":"question","data":{"id":"q2","type":"mcq",...}}

// Completion
data: {"type":"complete","total":6}
```

**Frontend Usage:**
```typescript
import { useQuizStream } from '@/lib/quizStream'

const { startStream, stopStream } = useQuizStream()

startStream(
  { topic: 'react', difficulty: 'hard', num_questions: 6 },
  {
    onMetadata: (meta) => console.log('Quiz:', meta.title),
    onQuestion: (q, idx) => console.log(`Q${idx+1}:`, q.text),
    onComplete: (total) => console.log('Done:', total),
    onError: (err) => console.error(err)
  }
)
```

**Demo Page:**
`/quiz/stream?topic=react&difficulty=medium`

### 3. Adaptive Difficulty
Adjusts question difficulty based on user performance.

**How It Works:**
1. User starts quiz session via `POST /api/v1/quizzes/session/start`
2. Each question submission includes performance metrics (time, correctness)
3. Next question difficulty adjusted based on:
   - Recent correctness rate (target: 65% for optimal learning)
   - Response time (fast correct → increase difficulty)
   - Streak (3+ correct → harder, 3+ wrong → easier)

**Algorithm:**
- **80%+ correct + 3-streak** → Increase difficulty
- **100% correct + fast (<15s avg)** → Jump up
- **<40% correct or 3-incorrect-streak** → Decrease difficulty
- **Below target (65%)** → Slight decrease

**Start Session:**
```http
POST /api/v1/quizzes/session/start?quiz_id=42
Authorization: Bearer <token>

Response: {"session_id": 123, "started_at": "2025-11-03T..."}
```

**Generate with Adaptive Context:**
```http
POST /api/v1/quizzes/generate?session_id=123
{
  "topic": "algorithms",
  "difficulty": "medium",
  "num_questions": 1
}
```

LLM prompt will include:
> "Adaptive context: User answered 4/6 correctly in previous questions. Adjust difficulty accordingly."

### 4. Persistent Quiz Templates
Save AI-generated quizzes for review and retakes.

**Save Quiz (during generation):**
```http
POST /api/v1/quizzes/generate
{
  "topic": "machine learning",
  "difficulty": "hard",
  "num_questions": 10,
  "save": true  // ← Save to library
}
```

**List Saved Quizzes:**
```http
GET /api/v1/quizzes/saved?topic=machine&difficulty=hard&limit=20
Authorization: Bearer <token>

Response:
[
  {
    "id": 42,
    "topic": "machine learning",
    "difficulty": "hard",
    "title": "Machine Learning — Hard Quiz",
    "num_questions": 10,
    "times_taken": 3,
    "best_score": 8,
    "best_score_total": 10,
    "is_favorite": true,
    "created_at": "2025-11-03T10:30:00Z",
    "last_taken_at": "2025-11-03T12:15:00Z"
  }
]
```

**Retrieve Saved Quiz:**
```http
GET /api/v1/quizzes/saved/42
Authorization: Bearer <token>

Response: QuizEnvelope with full questions
```

**Toggle Favorite:**
```http
POST /api/v1/quizzes/saved/42/favorite
Authorization: Bearer <token>

Response: {"is_favorite": true}
```

**Archive (Soft Delete):**
```http
DELETE /api/v1/quizzes/saved/42
Authorization: Bearer <token>

Response: {"archived": true}
```

## Database Schema

### `generated_quizzes`
```sql
CREATE TABLE generated_quizzes (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  topic VARCHAR(255) NOT NULL,
  difficulty VARCHAR(50) NOT NULL,
  title VARCHAR(500) NOT NULL,
  questions JSON NOT NULL,
  provider VARCHAR(50),  -- openai, anthropic, ollama
  model VARCHAR(100),    -- gpt-4o-mini, claude-3-5-sonnet
  adaptive_context JSON,
  times_taken INTEGER DEFAULT 0,
  best_score INTEGER,
  best_score_total INTEGER,
  last_taken_at TIMESTAMP,
  is_favorite BOOLEAN DEFAULT FALSE,
  is_archived BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);
```

### `quiz_sessions`
```sql
CREATE TABLE quiz_sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  quiz_id INTEGER,  -- FK to generated_quizzes (NULL for static)
  quiz_path VARCHAR(255),  -- For static quizzes
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  duration_seconds INTEGER,
  score INTEGER NOT NULL DEFAULT 0,
  total_questions INTEGER NOT NULL,
  passed BOOLEAN NOT NULL DEFAULT FALSE,
  answers JSON,  -- [{question_id, user_answer, correct, time_ms}]
  difficulty_progression JSON,  -- Track difficulty changes
  avg_response_time_ms INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install openai==1.54.0 anthropic==0.39.0 httpx-sse==0.4.0
```

### 2. Configure Provider
```bash
# backend/.env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run Migrations
```bash
cd backend
alembic revision --autogenerate -m "Add quiz templates and sessions"
alembic upgrade head
```

### 4. Test Generation
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoint
curl -X POST http://localhost:8001/api/v1/quizzes/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "topic": "fastapi",
    "difficulty": "medium",
    "num_questions": 3,
    "save": true
  }'
```

## Frontend Integration

### Static Quiz with AI Fallback
`/quiz/[slug]` automatically falls back to AI generation if static quiz not found.

### Streaming Quiz Demo
`/quiz/stream?topic=react&difficulty=hard` shows live generation.

### Interactive Quiz
`/quiz/interactive-[slug]` includes timer, feedback, achievements.

## Performance & Costs

### Generation Speed
- **OpenAI gpt-4o-mini**: ~2-4s for 5 questions
- **Anthropic claude-3-5-sonnet**: ~3-5s for 5 questions
- **Ollama (local)**: ~10-20s for 5 questions (depends on hardware)

### API Costs (per 5-question quiz)
- **OpenAI gpt-4o-mini**: ~$0.002 ($0.15/M input, $0.60/M output)
- **Anthropic claude-3-5-sonnet**: ~$0.015 ($3/M input, $15/M output)
- **Ollama**: Free (local compute)

### Caching Strategy
1. Save generated quizzes to DB (free retakes)
2. Use deterministic fallback when LLM unavailable
3. Batch generation for popular topics during off-peak

## Error Handling

### LLM Failures
- Automatic fallback to deterministic generator
- Retry logic with exponential backoff
- User-friendly error messages

### Streaming Errors
- Connection loss → fallback to non-streaming
- Malformed JSON → skip question, continue
- Timeout → return partial results

## Security

### API Keys
- Store in `.env` (never commit)
- Rotate regularly
- Use least-privilege keys

### Rate Limiting
```python
# Add to main.py
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
@router.post("/generate")
async def generate_quiz_ai(...):
    ...
```

### Content Filtering
- Validate topic input (no profanity, no PII)
- Sanitize LLM outputs before storing
- Review flagged quizzes

## Future Enhancements

1. **Multi-modal Questions**: Images, code snippets, diagrams
2. **Voice Quizzes**: Audio questions via TTS
3. **Collaborative Quizzes**: Multiplayer quiz battles
4. **Leaderboards**: Topic-specific rankings
5. **Explanation Videos**: AI-generated explainer clips
6. **Custom Prompts**: User-defined question styles

## Troubleshooting

### "No module named 'openai'"
```bash
pip install openai anthropic httpx-sse
```

### "OPENAI_API_KEY not configured"
```bash
echo "OPENAI_API_KEY=sk-..." >> backend/.env
```

### "Stream connection failed"
- Check firewall/proxy settings
- Disable nginx buffering: `X-Accel-Buffering: no`
- Increase client timeout

### Slow generation
- Use faster model (gpt-4o-mini instead of gpt-4)
- Reduce num_questions
- Use Ollama locally for zero latency

## Support
- Backend issues: Check `backend/app/services/llm_provider.py`
- Frontend issues: Check `src/lib/quizStream.ts`
- DB issues: Verify migrations with `alembic current`
