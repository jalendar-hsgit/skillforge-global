# 🦙 Ollama Setup Guide for SkillForge Global

This guide covers setting up Ollama for local AI quiz generation without requiring API keys.

## What is Ollama?

Ollama allows you to run large language models locally on your machine. This is perfect for:
- Development without API costs
- Privacy-focused deployments
- Offline AI quiz generation
- Testing and experimentation

## Installation

### Windows (PowerShell)
```powershell
# Download and run the Ollama installer
# Visit: https://ollama.com/download/windows
# Or use winget:
winget install Ollama.Ollama
```

### macOS
```bash
# Download from https://ollama.com/download/mac
# Or use Homebrew:
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Setup Steps

### 1. Start Ollama Service

**Windows (after installation):**
- Ollama runs as a background service automatically
- Check status: `ollama list`

**macOS/Linux:**
```bash
ollama serve
```

### 2. Pull a Model

For quiz generation, we recommend `llama3.2` (4.7GB) or `mistral` (4.1GB):

```bash
# Recommended: Llama 3.2 (good balance of speed and quality)
ollama pull llama3.2

# Alternative: Mistral (faster, lighter)
ollama pull mistral

# For better quality (larger download):
ollama pull llama3.2:13b
```

### 3. Verify Installation

```bash
# List installed models
ollama list

# Test generation
ollama run llama3.2 "What is Python?"
```

### 4. Configure SkillForge Backend

Edit `backend/.env`:
```bash
# Set provider to ollama
AI_PROVIDER=ollama

# Configure Ollama settings (defaults should work)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 5. Restart Backend

```powershell
# Stop current server (Ctrl+C in terminal)
# Then restart:
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Test AI Quiz Generation

```powershell
# Login first
$login = @{email="testquiz@test.com"; password="Test123!"} | ConvertTo-Json
$r = Invoke-WebRequest -Method Post -Uri http://localhost:8001/api/v1/auth/login -ContentType 'application/json' -Body $login -SessionVariable 'session'

# Generate quiz with Ollama
$body = @{
    topic = "Python Decorators"
    difficulty = "medium"
    num_questions = 3
    options_per_question = 4
} | ConvertTo-Json

$quiz = Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/v1/quizzes/generate -ContentType 'application/json' -Body $body -WebSession $session

Write-Host "Quiz ID: $($quiz.id)"
Write-Host "Title: $($quiz.title)"
Write-Host "Questions: $($quiz.questions.Count)"
```

## Model Recommendations

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.2` | 4.7GB | Fast | Good | **Recommended** - Best balance |
| `mistral` | 4.1GB | Very Fast | Good | Development/testing |
| `llama3.2:13b` | 7.4GB | Moderate | Excellent | Production (if hardware allows) |
| `llama3.1:70b` | 40GB | Slow | Outstanding | High-end workstations only |

## Performance Tips

### 1. GPU Acceleration
- Ollama automatically uses GPU if available (NVIDIA, AMD, or Apple Silicon)
- Check GPU usage: `nvidia-smi` (NVIDIA) or Activity Monitor (macOS)

### 2. Memory Requirements
- Minimum: 8GB RAM for 7B models
- Recommended: 16GB RAM for 13B models
- Optimal: 32GB+ RAM for larger models

### 3. Concurrent Requests
- Default: 1 request at a time
- Increase via environment variable: `OLLAMA_MAX_LOADED_MODELS=2`

### 4. Response Speed
- First request: ~2-5 seconds (model loading)
- Subsequent requests: ~500ms - 2s per question
- Streaming: Appears faster (gradual delivery)

## Troubleshooting

### Ollama Not Found
```powershell
# Windows: Ensure Ollama is in PATH
ollama --version

# If not found, restart terminal or add to PATH:
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"
```

### Connection Refused
```bash
# Check if Ollama is running:
curl http://localhost:11434/api/tags

# Restart Ollama service:
# Windows: Restart Ollama from system tray
# macOS/Linux: killall ollama && ollama serve
```

### Slow Generation
- Use smaller model (`mistral` instead of `llama3.2:13b`)
- Reduce `num_questions` during testing
- Enable GPU acceleration (automatic if available)

### Out of Memory
```bash
# Use quantized models (smaller, faster):
ollama pull llama3.2:7b-q4_0  # 4-bit quantization
```

## Switching Between Providers

You can easily switch between Ollama, OpenAI, and Anthropic:

```bash
# backend/.env

# Use Ollama (local, free)
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# Or use OpenAI (cloud, paid)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=raptor-mini  # Raptor mini (Preview)

# Or use Anthropic (cloud, paid)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

No code changes needed - just update `.env` and restart backend!

## Cost Comparison

| Provider | Cost per 1K Questions | Notes |
|----------|----------------------|-------|
| **Ollama** | $0 | Free, runs locally |
| OpenAI (raptor-mini) | ~$0.15 | Fast, lower-cost preview model (Raptor mini) |
| Anthropic (Claude 3.5) | ~$3.00 | Excellent quality |

**Recommendation:** Use Ollama for development/testing, cloud providers for production scale.

## Next Steps

1. Install Ollama: https://ollama.com/download
2. Pull a model: `ollama pull llama3.2`
3. Configure `backend/.env`: `AI_PROVIDER=ollama`
4. Test generation: Visit http://localhost:3000/quiz/stream?topic=python&difficulty=medium

## Resources

- Ollama Website: https://ollama.com
- Model Library: https://ollama.com/library
- GitHub: https://github.com/ollama/ollama
- Discord: https://discord.gg/ollama
