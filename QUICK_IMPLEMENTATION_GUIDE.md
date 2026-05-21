# Quick Implementation Guide - Start Here

**Focus**: Phase 1 (Critical) + Phase 2.1 (High Impact Mentor Features)  
**Estimated Time**: 8-10 hours for both phases

---

## PHASE 1: CRITICAL FIXES (5-7 hours)

### 1. Authentication End-to-End Testing

**Current Problem**: Login/signup might work, but integration unclear with demo accounts  
**Impact**: Blocks all user testing  
**Time**: 1.5 hours

#### Step 1: Verify Login Works
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Test login with demo account
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@skillforge.com",
    "password": "super123"
  }'

# Expected response:
# {"access_token": "eyJ...", "token_type": "bearer", "user": {...}}
```

#### Step 2: Check Token Handling
```typescript
// src/lib/api.ts - Verify token is saved correctly
// After login, check localStorage:
localStorage.getItem('token')  // Should exist

// Make authenticated request:
await api('GET', '/api/v1/auth/me')
// Should return current user data
```

#### Step 3: Frontend Integration
```typescript
// src/pages/login.tsx - Add error handling
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include'  // Important for cookies
    })
    
    if (!response.ok) {
      console.error('Login failed:', await response.text())
      return
    }
    
    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    router.push('/dashboard')
  } catch (error) {
    console.error('Login error:', error)
  }
}
```

#### Step 4: Test All Demo Accounts
```bash
# Create test script: backend/test_auth.py
accounts = [
  ("superadmin@skillforge.com", "super123", "SUPERADMIN"),
  ("admin@skillforge.com", "admin123", "ADMIN"),
  ("mentor.sarah@skillforge.com", "mentor123", "MENTOR"),
  ("john.doe@example.com", "john123", "USER"),
]

for email, pwd, role in accounts:
    response = requests.post(
        'http://localhost:8001/api/v1/auth/login',
        json={'email': email, 'password': pwd}
    )
    assert response.status_code == 200
    assert response.json()['user']['role'] == role
    print(f"✓ {email} ({role})")
```

---

### 2. Fix Coding Practice 500 Error

**Current Problem**: GET `/api/v1x/coding-practice/challenges` returns 500  
**Data Available**: 38 challenges in DB  
**Time**: 1 hour

#### Step 1: Identify the Error
```bash
# Terminal: Run the failing endpoint with debugging
cd backend

# Add this to app/api/v1x/coding_practice.py at top:
import logging
logging.basicConfig(level=logging.DEBUG)

# Test endpoint
curl http://localhost:8001/api/v1x/coding-practice/challenges

# Check server console for full error traceback
```

#### Step 2: Common Fixes Checklist
```python
# backend/app/api/v1x/coding_practice.py

# Check 1: Router exists and is mounted
# In app/main.py, verify:
# from app.api.v1x import coding_practice
# app.include_router(coding_practice.router, prefix="/api/v1x")

# Check 2: Model relationships are correct
from app.modelsx.coding_practice import CodingChallenge, ChallengeHint

def get_challenges():
    try:
        challenges = db.query(CodingChallenge).all()
        # Verify no null foreign keys
        for ch in challenges:
            if ch.environment_id and not ch.environment:
                print(f"WARNING: Challenge {ch.id} has missing environment")
        return challenges
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise

# Check 3: Schema is correct
# Verify Pydantic models match SQLAlchemy models
```

#### Step 3: Test Fixed Endpoint
```bash
# After fix, test should work:
curl http://localhost:8001/api/v1x/coding-practice/challenges
# Should return: [{"id": 1, "title": "...", ...}, ...]
```

---

### 3. Fix Missing v1x Routes

**Current Problem**: Code snippets, learning paths return 404  
**Time**: 30 minutes

#### Step 1: Check What's Mounted
```python
# backend/app/main.py - Add debugging

# Add this near the end of main.py:
def print_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append((route.path, route.methods))
    
    missing = [
        '/api/v1x/snippets',
        '/api/v1x/learning-paths',
        '/api/v1/paths'
    ]
    
    mounted = [r[0] for r in routes]
    for m in missing:
        found = any(m in r for r in mounted)
        print(f"{m}: {'✓ FOUND' if found else '❌ MISSING'}")

if __name__ == "__main__":
    print_routes()
```

#### Step 2: Mount Missing Routers
```python
# In backend/app/main.py, add near other router includes:

try:
    from app.api.v1x import code_snippets
    app.include_router(code_snippets.router, prefix="/api/v1x")
except ImportError as e:
    print(f"Warning: Could not import code_snippets: {e}")

try:
    from app.api.v1x import learning_paths
    app.include_router(learning_paths.router, prefix="/api/v1x")
except ImportError as e:
    print(f"Warning: Could not import learning_paths: {e}")

try:
    from app.api.v1 import paths
    app.include_router(paths.router, prefix="/api/v1")
except ImportError as e:
    print(f"Warning: Could not import paths: {e}")
```

#### Step 3: Verify Routes
```bash
# Restart backend and test
curl http://localhost:8001/api/v1x/code-snippets
# Should return list or 200, not 404
```

---

### 4. Database Integrity Verification

**Current Problem**: Unknown schema issues  
**Time**: 1 hour

#### Create Verification Script
```python
# backend/verify_integrity.py
import sqlite3
from app.core.db import SessionLocal

def check_integrity():
    db = SessionLocal()
    conn = sqlite3.connect('app/data/skillforge.db')
    cursor = conn.cursor()
    
    print("="*60)
    print("DATABASE INTEGRITY REPORT")
    print("="*60)
    
    # 1. Check foreign key constraints
    print("\n1. Checking Foreign Key Integrity...")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA foreign_key_check")
    violations = cursor.fetchall()
    
    if violations:
        print(f"❌ Found {len(violations)} foreign key violations:")
        for v in violations:
            print(f"   Table: {v[0]}, Row: {v[1]}, Column: {v[2]}")
    else:
        print("✓ All foreign keys valid")
    
    # 2. Check table row counts
    print("\n2. Table Population Summary:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    total_rows = 0
    for (table,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   {table}: {count} rows")
            total_rows += count
    
    print(f"\n   TOTAL: {total_rows} records across {len(tables)} tables")
    
    # 3. Check for NULL primary keys
    print("\n3. Checking for NULL Primary Keys...")
    issues = []
    for (table,) in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        pk_cols = [c[1] for c in columns if c[5]]  # pk=1
        
        for pk in pk_cols:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {pk} IS NULL")
            if cursor.fetchone()[0] > 0:
                issues.append(f"{table}.{pk}")
    
    if issues:
        print(f"❌ Found {len(issues)} NULL primary keys: {issues}")
    else:
        print("✓ No NULL primary keys found")
    
    print("\n" + "="*60)
    conn.close()

if __name__ == "__main__":
    check_integrity()
```

Run it:
```bash
cd backend
python verify_integrity.py
```

---

### 5. Seed Missing Data

**If data is corrupt**, reseed:
```bash
cd backend

# Backup current database
cp app/data/skillforge.db app/data/skillforge.db.backup

# Delete and reseed
rm app/data/skillforge.db
python seed_all_demo_data.py

# Verify results
sqlite3 app/data/skillforge.db ".schema" | head -20
```

---

## PHASE 2.1: MENTOR BOOKING FLOW (3 hours)

**Why First**: Core feature with immediate user value  
**Data Ready**: 4 mentors, 20 availability slots, backend complete

### Step 1: Create Mentor Listing Page

```typescript
// src/pages/mentors/index.tsx
import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Mentor {
  id: number
  user: { name: string; bio: string }
  expertise: string
  hourly_rate: number
  average_rating: number
  total_sessions: number
}

export default function MentorsPage() {
  const [mentors, setMentors] = useState<Mentor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMentors()
  }, [])

  const fetchMentors = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentors`)
      const data = await response.json()
      setMentors(data)
    } catch (error) {
      console.error('Failed to fetch mentors:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading mentors...</div>

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Expert Mentors</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {mentors.map(mentor => (
          <div key={mentor.id} className="border rounded-lg p-4 shadow hover:shadow-lg">
            <h3 className="text-xl font-semibold">{mentor.user.name}</h3>
            <p className="text-gray-600 text-sm mb-2">{mentor.user.bio}</p>
            
            <div className="mb-3">
              <div className="text-sm font-semibold">${mentor.hourly_rate}/hour</div>
              <div className="text-xs text-gray-500">
                ⭐ {mentor.average_rating.toFixed(1)} ({mentor.total_sessions} sessions)
              </div>
            </div>

            <div className="mb-3 text-xs">
              <div className="font-semibold">Expertise:</div>
              <div className="flex flex-wrap gap-1">
                {mentor.expertise.split(',').map((skill, i) => (
                  <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {skill.trim()}
                  </span>
                ))}
              </div>
            </div>

            <Link href={`/mentors/${mentor.id}/book`}>
              <button className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
                Book Session
              </button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Step 2: Create Booking Form

```typescript
// src/pages/mentors/[id]/book.tsx
import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'

interface Availability {
  id: number
  day_of_week: string
  start_time: string
  end_time: string
}

export default function BookSessionPage() {
  const router = useRouter()
  const { id } = router.query
  const [mentor, setMentor] = useState<any>(null)
  const [availability, setAvailability] = useState<Availability[]>([])
  const [formData, setFormData] = useState({
    topic: '',
    date: '',
    time: '',
    duration: 60
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (id) {
      fetchMentorAndAvailability()
    }
  }, [id])

  const fetchMentorAndAvailability = async () => {
    try {
      const menRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentors/${id}`
      )
      const mentorData = await menRes.json()
      setMentor(mentorData)

      const availRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentors/${id}/availability`
      )
      const availData = await availRes.json()
      setAvailability(availData)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/mentors/${id}/sessions`,
        {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            mentor_id: id,
            topic: formData.topic,
            scheduled_at: `${formData.date}T${formData.time}`,
            duration_minutes: formData.duration
          })
        }
      )

      if (!response.ok) throw new Error('Booking failed')

      alert('Booking submitted! Waiting for mentor confirmation.')
      router.push('/student/sessions')
    } catch (error) {
      alert(`Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  if (!mentor) return <div>Loading...</div>

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Book Session with {mentor.user?.name}</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Session Topic</label>
          <input
            type="text"
            placeholder="e.g., Python Fundamentals"
            value={formData.topic}
            onChange={(e) => setFormData({...formData, topic: e.target.value})}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Preferred Date</label>
          <input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({...formData, date: e.target.value})}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Preferred Time</label>
          <input
            type="time"
            value={formData.time}
            onChange={(e) => setFormData({...formData, time: e.target.value})}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium">Duration (minutes)</label>
          <select
            value={formData.duration}
            onChange={(e) => setFormData({...formData, duration: parseInt(e.target.value)})}
            className="w-full border rounded px-3 py-2"
          >
            <option value={30}>30 minutes - ${mentor.hourly_rate / 2}</option>
            <option value={60}>60 minutes - ${mentor.hourly_rate}</option>
            <option value={90}>90 minutes - ${(mentor.hourly_rate * 1.5).toFixed(2)}</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-500 text-white py-3 rounded font-semibold hover:bg-green-600 disabled:opacity-50"
        >
          {loading ? 'Booking...' : 'Request Session'}
        </button>
      </form>

      <div className="mt-8 p-4 bg-gray-50 rounded">
        <h3 className="font-semibold mb-2">Mentor Availability</h3>
        <div className="space-y-2 text-sm">
          {availability.map(slot => (
            <div key={slot.id}>
              {slot.day_of_week}: {slot.start_time} - {slot.end_time}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

### Step 3: Student Sessions View

```typescript
// src/pages/student/sessions.tsx
import { useEffect, useState } from 'react'

interface Session {
  id: number
  mentor: { user: { name: string } }
  topic: string
  scheduled_at: string
  status: string
  price: number
}

export default function MySessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/my-sessions`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      const data = await response.json()
      setSessions(data)
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'confirmed': 'bg-green-100 text-green-800',
      'completed': 'bg-blue-100 text-blue-800',
      'cancelled': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100'
  }

  if (loading) return <div>Loading sessions...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">My Mentor Sessions</h1>

      {sessions.length === 0 ? (
        <p className="text-gray-500">No sessions yet. <a href="/mentors" className="text-blue-500">Book one now!</a></p>
      ) : (
        <div className="space-y-4">
          {sessions.map(session => (
            <div key={session.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{session.mentor.user.name}</h3>
                  <p className="text-gray-600">{session.topic}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(session.scheduled_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <div className={`px-3 py-1 rounded text-sm font-semibold ${getStatusColor(session.status)}`}>
                    {session.status}
                  </div>
                  <div className="text-lg font-bold mt-2">${session.price}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## Testing Checklist

Before moving to next phase:

```
PHASE 1 (Critical Fixes)
□ Login/signup working with all 4 demo accounts
□ Coding practice endpoint returns 200 with 38 challenges
□ All v1x routes mounted and accessible
□ Database integrity check shows no violations
□ No console errors when loading pages

PHASE 2.1 (Mentor Booking)
□ Mentor listing page shows 4 mentors
□ Each mentor card shows expertise, rate, rating
□ Clicking "Book" opens booking form
□ Form validates date/time selection
□ Submitting creates MentorSession with PENDING status
□ Student can view their sessions with PENDING status
□ Mentor sees session in their queue (pending confirmation)
```

---

## Next Actions

1. **Start Phase 1 today** - Should take 5-7 hours
2. **Immediately after**: Proceed to Phase 2.1 (3 hours)
3. **Then**: Continue with Phase 2.2-2.5 as time allows

**Total for today**: 8-10 hours gets you core functionality working with demo data

Good luck! 🚀
