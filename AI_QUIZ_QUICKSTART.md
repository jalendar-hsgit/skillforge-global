# 🚀 AI Quiz Quick Start

Get AI-powered quiz generation running in 5 minutes.

## Prerequisites
- Python 3.10+ with backend dependencies installed
- Node.js 18+ with frontend dependencies installed
- OpenAI or Anthropic API key

## Step 1: Install LLM Packages
```bash
cd backend
pip install openai==1.54.0 anthropic==0.39.0 httpx-sse==0.4.0
```

## Step 2: Configure Provider
```bash
# Create backend/.env file
echo "AI_PROVIDER=openai" >> backend/.env
echo "OPENAI_API_KEY=sk-your-key-here" >> backend/.env
echo "OPENAI_MODEL=raptor-mini" >> backend/.env  # Raptor mini (Preview)
```

## Step 3: Run Database Migration
```bash
cd backend
alembic revision --autogenerate -m "Add quiz templates and sessions"
alembic upgrade head
```

## Step 4: Start Servers
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
npm run dev
```

## Step 5: Test Generation

### Browser Test
Visit: `http://localhost:3000/quiz/python-basics`

If quiz doesn't exist, AI will auto-generate one!

### Streaming Demo
Visit: `http://localhost:3000/quiz/stream?topic=react&difficulty=medium`

Watch questions appear in real-time!

### API Test
```bash
# Login first to get token
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Generate quiz
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

## Troubleshooting

### "OPENAI_API_KEY not configured"
→ Check `backend/.env` file exists with `OPENAI_API_KEY=sk-...`

### "No module named 'openai'"
→ Run: `pip install openai anthropic httpx-sse`

### "Quiz generation failed"
→ Check API key is valid, or change to `AI_PROVIDER=ollama` for local (requires Ollama installed)

### Migration errors
→ Ensure you're in `backend/` directory when running `alembic` commands

## Using Different Providers

### Anthropic (Claude)
```bash
# backend/.env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Ollama (Local/Free)
```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2

# backend/.env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Demo Workflows

### 1. Generate and Save Quiz
1. Visit `/quiz/machine-learning` (doesn't exist)
2. AI generates questions automatically
3. Questions saved to your library
4. Retake anytime from saved quizzes

### 2. Streaming Generation
1. Visit `/quiz/stream?topic=javascript&difficulty=hard`
2. Watch progress bar as questions stream in
3. Questions appear with fade-in animations
4. Click "Start Quiz" when complete

### 3. Adaptive Difficulty
1. Start quiz session via API: `POST /api/v1/quizzes/session/start`
2. Answer questions (tracked with performance)
3. Next questions adjust difficulty based on your score
4. Review adaptive progression at end

## Cost Estimates

### Per 5-Question Quiz
- **OpenAI raptor-mini (Preview)**: ~$0.002 (0.2 cents)
- **Anthropic claude-3.5-sonnet**: ~$0.015 (1.5 cents)
- **Ollama (local)**: $0.00 (free)

### Monthly (1000 quizzes)
- **OpenAI**: ~$2
- **Anthropic**: ~$15
- **Ollama**: $0

## Next Steps

- Read `AI_QUIZ_GUIDE.md` for full API reference
- Check `AI_QUIZ_IMPLEMENTATION.md` for technical details
- Explore adaptive difficulty in session tracking
- Implement rate limiting for production

## Support

**Docs:**
- Full guide: `AI_QUIZ_GUIDE.md`
- Implementation: `AI_QUIZ_IMPLEMENTATION.md`
- API reference: `API_TESTING_GUIDE.md`

**Code:**
- LLM providers: `backend/app/services/llm_provider.py`
- Adaptive engine: `backend/app/services/adaptive_difficulty.py`
- Streaming client: `src/lib/quizStream.ts`

**Issues:**
- Check logs: Backend terminal output
- Enable debug: `DEBUG=true` in `backend/.env`
- Test fallback: Remove API key to verify deterministic generation works
