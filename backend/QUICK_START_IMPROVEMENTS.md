# 🚀 Quick Start Guide - Course & Practice Improvements

## ⚡ Quick Setup (5 minutes)

### 1. Update Database
```bash
cd backend
# Tables auto-create on next app start
```

### 2. Seed Premium Content
```bash
python seed_premium_practice.py
```

### 3. Configure YouTube API (Optional)
```bash
# Add to .env
YOUTUBE_API_KEY=your_key_here
```

### 4. Start Backend
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 📍 New API Endpoints

### Premium Courses
```bash
GET  /api/v1x/courses?is_premium=true&tier=premium
GET  /api/v1x/courses/{id}
```

### YouTube Sync (Quality Filtered)
```bash
POST /api/v1x/youtube/preview    # Preview filtered videos
POST /api/v1x/youtube/sync       # Import quality videos
```

### Coding Practice
```bash
# Challenges
GET  /api/v1x/coding-practice/challenges
GET  /api/v1x/coding-practice/challenges/{slug}
POST /api/v1x/coding-practice/challenges/{id}/submit
GET  /api/v1x/coding-practice/challenges/{id}/hints

# Sessions
POST /api/v1x/coding-practice/sessions/start
GET  /api/v1x/coding-practice/sessions/{token}
POST /api/v1x/coding-practice/sessions/{token}/save
POST /api/v1x/coding-practice/sessions/{token}/end

# Cloud Labs
GET  /api/v1x/coding-practice/cloud-labs
GET  /api/v1x/coding-practice/cloud-labs/{slug}

# Progress
GET  /api/v1x/coding-practice/my-submissions
GET  /api/v1x/coding-practice/my-stats

# Metadata
GET  /api/v1x/coding-practice/categories
GET  /api/v1x/coding-practice/languages
GET  /api/v1x/coding-practice/simulators
```

---

## 💡 Key Features

### ✅ Premium Courses
- 8 premium courses ($79.99 - $149.99)
- Tiered pricing (free/premium/enterprise)
- Instructor profiles
- Difficulty levels
- Rating system
- YouTube playlist sync

### ✅ YouTube Quality Filtering
- **Excludes:** Shorts (<3 min), spam, clickbait, gaming, low views
- **Includes:** Trusted channels, educational content, high engagement
- **Filters:** Duration, view count, engagement ratio, keywords

### ✅ Coding Practice
- **15+ languages:** Python, JS, Java, C++, Go, Rust, SQL, etc.
- **12 categories:** Algorithms, Cloud, DevOps, Database, Security, etc.
- **Simulators:** Code editor, cloud console, Kubernetes, terminal
- **Gamification:** Points, coins, hints, leaderboards

### ✅ Cloud Labs
- AWS, Azure, GCP hands-on scenarios
- Infrastructure as Code templates
- Validation scripts
- Architecture diagrams
- Real-world projects

---

## 🎯 Usage Examples

### Filter Quality Videos
```python
# Python example
import requests

response = requests.post(
    "http://localhost:8001/api/v1x/youtube/preview",
    json={
        "course_id": 1,
        "query": "python tutorial",
        "max_results": 10
    }
)

videos = response.json()["items"]
# Returns only quality educational videos
```

### Submit Coding Challenge
```python
response = requests.post(
    "http://localhost:8001/api/v1x/coding-practice/challenges/1/submit",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "challenge_id": 1,
        "language": "python",
        "code": "def two_sum(nums, target):\n    ..."
    }
)

result = response.json()
print(f"Score: {result['score']}%")
print(f"Coins earned: {result['coins_earned']}")
```

### Start Practice Session
```python
response = requests.post(
    "http://localhost:8001/api/v1x/coding-practice/sessions/start",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "environment_id": 1,
        "language": "python"
    }
)

session = response.json()
print(f"Access URL: {session['access_url']}")
print(f"Expires: {session['expires_at']}")
```

---

## 🔍 Testing Checklist

### ✅ Premium Courses
- [ ] Seed premium courses: `python seed_premium_practice.py`
- [ ] Query courses: `GET /api/v1x/courses?is_premium=true`
- [ ] Verify pricing and tiers
- [ ] Check instructor and difficulty fields

### ✅ YouTube Filtering
- [ ] Set YOUTUBE_API_KEY
- [ ] Search: `POST /api/v1x/youtube/preview` with "python tutorial"
- [ ] Verify no shorts (<3 min) returned
- [ ] Verify no spam/gaming content
- [ ] Check trusted channels included

### ✅ Coding Practice
- [ ] List challenges: `GET /api/v1x/coding-practice/challenges`
- [ ] Get categories: `GET /api/v1x/coding-practice/categories`
- [ ] Get languages: `GET /api/v1x/coding-practice/languages`
- [ ] Submit solution (creates mock execution)
- [ ] Check user stats: `GET /api/v1x/coding-practice/my-stats`

### ✅ Cloud Labs
- [ ] List labs: `GET /api/v1x/coding-practice/cloud-labs`
- [ ] Get lab details: `GET /api/v1x/coding-practice/cloud-labs/{slug}`
- [ ] Verify AWS/Azure/GCP scenarios

---

## 📊 Database Tables

### New Tables
- `coding_challenges` - Challenge definitions
- `coding_submissions` - User submissions  
- `challenge_hints` - Progressive hints
- `simulator_environments` - Environment configs
- `practice_sessions` - Active sessions
- `cloud_lab_scenarios` - Cloud labs

### Updated Tables
- `courses` - Added: tier, is_premium, instructor, difficulty, rating, youtube_playlist_id

---

## 🎓 Premium Courses Available

1. **Advanced Python Mastery** - $79.99 (Advanced)
2. **System Design Interview Prep** - $99.99 (Advanced)
3. **AWS Solutions Architect Pro** - $149.99 (Advanced)
4. **Kubernetes for Production** - $89.99 (Intermediate)
5. **Machine Learning Engineering** - $129.99 (Advanced)
6. **Full-Stack Next.js Enterprise** - $94.99 (Intermediate)
7. **Data Engineering Masterclass** - $119.99 (Advanced)
8. **Cybersecurity & Ethical Hacking** - $109.99 (Intermediate)

---

## 🏆 Coding Challenges Available

1. **Two Sum Problem** (Easy) - Arrays & Hash Tables
2. **Binary Tree Level Order** (Medium) - Trees & BFS
3. **AWS Lambda + API Gateway** (Medium) - Cloud/AWS
4. **Kubernetes Multi-Container** (Hard) - DevOps
5. **SQL Query Optimization** (Medium) - Database

---

## 🖥️ Simulator Environments

1. **Python 3.11 Sandbox** (Free) - Standard Python
2. **AWS Developer Environment** (Premium) - AWS CLI/SDK
3. **Kubernetes Cluster** (Premium) - K8s practice
4. **PostgreSQL Database** (Free) - SQL practice

---

## ☁️ Cloud Lab Scenarios

1. **Serverless REST API** (AWS) - 90 min, 100 points
2. **Microservices on K8s** (AWS EKS) - 120 min, 150 points
3. **Azure Functions + Cosmos** (Azure) - 75 min, 90 points

---

## 🚨 Common Issues

### YouTube Sync Returns No Results
```bash
# Check API key is set
echo $YOUTUBE_API_KEY

# Increase max_results (filters remove low-quality)
# Or disable filters: apply_filters=false
```

### Coding Practice Tables Not Created
```bash
# Restart backend to trigger table creation
# Or check main.py imports all models
```

### Session Not Starting
```bash
# Check simulator_environments table has data
python seed_premium_practice.py

# Verify environment_id exists
```

---

## 📈 Metrics to Track

- Premium course enrollments
- YouTube video quality scores
- Coding challenge completion rates
- Average submission scores
- Active practice sessions
- Cloud lab completions
- Coins earned per user

---

## 🎉 Success Indicators

✅ Premium courses visible in API  
✅ YouTube search returns only quality videos  
✅ Coding challenges loadable  
✅ Submissions create and execute  
✅ Sessions start and save state  
✅ Cloud labs list correctly  
✅ No database errors  
✅ All endpoints return 200 OK  

---

## 📞 Need Help?

1. Check `COURSE_PRACTICE_IMPROVEMENTS.md` for detailed docs
2. Review API endpoint responses for errors
3. Check backend logs for exceptions
4. Verify database tables created: `.tables` in sqlite3
5. Ensure all seed data loaded

---

**Status:** ✅ Ready for Testing  
**Deployment:** Staging Ready  
**Production:** Requires Docker for simulators
