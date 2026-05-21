# ✅ AWS DevOps Fixed + Dynamic Quiz Plan

## 🔧 Issue Fixed: aws-devops "Content unavailable"

### Problem:
- Only `python-ai` course existed in database
- Other paths (fullstack, aws-devops, cybersec, flutter) had no course records
- Frontend couldn't fetch videos because courses didn't exist

### Solution:
✅ Created `complete_setup.py` script
✅ All 5 courses now in database:
- python-ai (22 videos)
- fullstack (18 videos)
- aws-devops (20 videos)
- cybersec (15 videos)
- flutter (17 videos)

### Test Results:
```
✅ http://localhost:3000/paths/python-ai
✅ http://localhost:3000/paths/fullstack
✅ http://localhost:3000/paths/aws-devops  ← NOW WORKING!
✅ http://localhost:3000/paths/cybersec
✅ http://localhost:3000/paths/flutter
```

---

## 🎯 Next: Dynamic Quiz Generation with AI

### Current Quiz System (Static):
- Quizzes stored in `quizzes.json`
- Manually written questions
- Fixed 3-5 questions per path
- No real-world scenarios

**Example (current):**
```json
{
  "python-ai": {
    "questions": [
      {
        "text": "What does list comprehension produce?",
        "options": ["A generator", "A list", "A tuple", "A dict"],
        "answerIndex": 1
      }
    ]
  }
}
```

---

## 🤖 Proposed: AI-Powered Quiz Generation

### Architecture:

```
User completes videos → AI analyzes content → Generates quiz
                                              ↓
                            Real-world scenarios, code challenges,
                            difficulty levels, personalized questions
```

### Database Structure (Already Exists!):

**Tables:**
- `quizzes` - Quiz metadata (course_id, title)
- `quiz_questions` - Individual questions (quiz_id, question, options, answer)
- `quiz_attempts` - User attempts (user_id, score, timestamp)

---

### Features to Implement:

#### 1. **AI Question Generator**
```python
# backend/app/services/quiz_ai.py

def generate_quiz_questions(
    video_titles: List[str],
    difficulty: str = "medium",
    num_questions: int = 10,
    include_code: bool = True
) -> List[Dict]:
    """
    Use OpenAI/Claude to generate quiz questions
    based on video content
    """
    prompt = f"""
    Generate {num_questions} multiple-choice quiz questions 
    for a course covering: {', '.join(video_titles)}
    
    Difficulty: {difficulty}
    Include code challenges: {include_code}
    
    Focus on:
    - Real-world scenarios
    - Practical application
    - Common interview questions
    - Best practices
    
    Return JSON format:
    [
      {{
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "answer_index": 2,
        "explanation": "...",
        "difficulty": "medium",
        "tags": ["python", "ml"]
      }}
    ]
    """
    
    # Call AI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_questions(response)
```

#### 2. **Scenario-Based Questions**
```python
def generate_scenario_question(topic: str) -> Dict:
    """Generate real-world scenario question"""
    prompt = f"""
    Create a realistic workplace scenario question about {topic}.
    
    Example format:
    "You're building a web app that needs to handle 10k users.
    Which database strategy would you choose and why?"
    
    Options should include:
    - Best practice answer
    - Common mistakes
    - Edge cases
    - Context-dependent solutions
    """
```

#### 3. **Adaptive Difficulty**
```python
def get_next_question(user_id: int, quiz_id: int) -> Dict:
    """
    Analyze user's previous answers
    Adjust difficulty dynamically
    """
    user_history = get_user_quiz_history(user_id)
    
    if user_history.accuracy > 0.8:
        difficulty = "hard"
    elif user_history.accuracy > 0.5:
        difficulty = "medium"
    else:
        difficulty = "easy"
    
    return generate_question(difficulty=difficulty)
```

#### 4. **Code Challenge Questions**
```python
def generate_code_challenge(language: str, topic: str) -> Dict:
    """Generate debugging/code completion questions"""
    return {
        "question": "What's wrong with this code?",
        "code": """
def process_data(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result[0]  # Bug: only returns first item
        """,
        "options": [
            "Missing return statement",
            "Returns only first item instead of list",
            "Loop doesn't iterate properly",
            "Variable name conflict"
        ],
        "answer_index": 1
    }
```

---

### API Endpoints to Create:

```python
# backend/app/api/v1x/quiz_ai.py

@router.post("/quizzes/generate")
def generate_quiz(
    course_id: int,
    difficulty: str = "medium",
    num_questions: int = 10
):
    """Generate AI quiz for a course"""
    course = get_course(course_id)
    videos = get_course_videos(course_id)
    
    questions = generate_quiz_questions(
        video_titles=[v.title for v in videos],
        difficulty=difficulty,
        num_questions=num_questions
    )
    
    # Save to database
    quiz = Quiz(course_id=course_id, title=f"{course.title} - AI Quiz")
    db.add(quiz)
    
    for q in questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question=q["question"],
            options=q["options"],
            answer=q["answer_index"],
            explanation=q.get("explanation")
        )
        db.add(question)
    
    db.commit()
    return {"quiz_id": quiz.id, "questions": len(questions)}

@router.get("/quizzes/{quiz_id}/adaptive")
def get_adaptive_question(
    quiz_id: int,
    user_id: int = Depends(get_current_user)
):
    """Get next question based on user performance"""
    return get_next_question(user_id, quiz_id)
```

---

### Frontend Changes:

```tsx
// src/pages/quiz/[slug].tsx

// Add quiz generation button
<button onClick={generateAIQuiz}>
  🤖 Generate AI Quiz
</button>

// Add difficulty selector
<select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
  <option value="easy">Easy</option>
  <option value="medium">Medium</option>
  <option value="hard">Hard</option>
</select>

// Add real-time scenarios
{question.scenario && (
  <div className="scenario-box">
    <h4>Real-World Scenario:</h4>
    <p>{question.scenario}</p>
  </div>
)}

// Add code challenges
{question.code && (
  <pre className="code-block">
    <code>{question.code}</code>
  </pre>
)}
```

---

### AI API Options:

#### Option 1: OpenAI GPT-4
```python
import openai

openai.api_key = settings.OPENAI_API_KEY

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)
```

**Pros:** Best quality, creative scenarios
**Cons:** Cost ($0.03/1k tokens)

#### Option 2: Claude (Anthropic)
```python
import anthropic

client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)

response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": prompt}]
)
```

**Pros:** Long context, good for technical content
**Cons:** Similar cost to GPT-4

#### Option 3: Local LLM (Ollama)
```python
import ollama

response = ollama.generate(
    model="llama2",
    prompt=prompt
)
```

**Pros:** Free, private
**Cons:** Lower quality, slower

---

### Question Types to Generate:

1. **Multiple Choice** - Traditional MCQ
2. **Code Debugging** - Find the bug
3. **Code Completion** - Fill in the blanks
4. **Scenario-Based** - Real-world problem solving
5. **True/False** - Concept verification
6. **Match Pairs** - Connect concepts
7. **Order Steps** - Sort steps in correct order

---

### Example AI-Generated Questions:

**Scenario-Based:**
```
Question: Your team's Python API is handling 1000 req/sec. 
Response times are increasing. What's your first optimization step?

A) Switch to Go/Rust
B) Add caching layer (Redis)
C) Increase server RAM
D) Rewrite in async/await

Answer: B
Explanation: Caching reduces database load. Profile first before rewriting.
```

**Code Challenge:**
```python
# What's the output?
def mystery(n):
    return [i**2 for i in range(n) if i % 2 == 0]

print(mystery(5))

A) [0, 4, 16]
B) [0, 1, 4, 9, 16]
C) [4, 16]
D) Error

Answer: A
```

---

### Implementation Plan:

**Phase 1: Setup** (1-2 days)
- [ ] Add AI API key to config
- [ ] Create quiz_ai.py service
- [ ] Test question generation

**Phase 2: Database** (1 day)
- [ ] Migrate quizzes to database
- [ ] Add quiz_questions table
- [ ] Add quiz_attempts tracking

**Phase 3: API** (2-3 days)
- [ ] Create /quizzes/generate endpoint
- [ ] Add adaptive difficulty logic
- [ ] Implement code challenge parser

**Phase 4: Frontend** (2-3 days)
- [ ] Add quiz generation UI
- [ ] Display code challenges
- [ ] Show scenarios with context
- [ ] Add difficulty selector

**Phase 5: Testing** (1-2 days)
- [ ] Test question quality
- [ ] Verify adaptive logic
- [ ] A/B test with users

---

### Cost Estimation:

**OpenAI GPT-4:**
- 1 quiz (10 questions) ≈ 2,000 tokens
- Cost: ~$0.06 per quiz
- 1000 quizzes/month = $60

**Optimization:**
- Cache generated questions
- Reuse for similar topics
- Use GPT-3.5 for easier questions ($0.01/quiz)

---

### Benefits:

✅ **Unlimited Questions** - Never run out
✅ **Real-World Scenarios** - Practical application
✅ **Adaptive Difficulty** - Personalized learning
✅ **Fresh Content** - Always up-to-date
✅ **Code Challenges** - Hands-on practice
✅ **Scalable** - Works for any topic

---

## 🚀 Quick Start (If You Want to Implement):

1. **Add AI API key:**
```bash
# backend/.env
OPENAI_API_KEY=sk-...
```

2. **Install dependencies:**
```bash
pip install openai anthropic
```

3. **Create quiz service:**
```bash
touch backend/app/services/quiz_ai.py
```

4. **Test generation:**
```python
from app.services.quiz_ai import generate_quiz_questions

questions = generate_quiz_questions(
    video_titles=["Python Basics", "Machine Learning Intro"],
    difficulty="medium",
    num_questions=5
)
print(questions)
```

---

Let me know if you want me to implement the AI quiz generation! 🤖
