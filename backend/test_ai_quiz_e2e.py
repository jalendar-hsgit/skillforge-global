"""
End-to-end test script for AI Quiz endpoints via Next.js proxies.
Tests signup, login, generate, stream, saved quizzes, and session flows.
"""
import requests
import json
import time

# Config
NEXT_BASE = "http://localhost:3000"
API_BASE = "http://localhost:8001"

def test_auth():
    """Test signup and login to get auth cookie."""
    print("🔐 Testing Auth...")
    
    # Signup
    signup_payload = {
        "email": f"quiztest_{int(time.time())}@example.com",
        "password": "Test123!",
        "name": "Quiz Test User"
    }
    r = requests.post(f"{API_BASE}/api/v1/auth/signup", json=signup_payload)
    print(f"  Signup: {r.status_code}")
    assert r.status_code == 200, f"Signup failed: {r.text}"
    
    # Login
    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"]
    }
    r = requests.post(f"{API_BASE}/api/v1/auth/login", json=login_payload)
    print(f"  Login: {r.status_code}")
    assert r.status_code == 200, f"Login failed: {r.text}"
    
    # Extract cookie
    cookie = r.headers.get('set-cookie', '').split(';')[0]
    print(f"  ✅ Auth OK, cookie: {cookie[:30]}...")
    return cookie


def test_generate_quiz(cookie):
    """Test POST /api/quizzes/generate via Next proxy."""
    print("\n🧠 Testing Generate Quiz (POST /api/quizzes/generate)...")
    
    payload = {
        "topic": "Python Decorators",
        "difficulty": "medium",
        "num_questions": 3,
        "options_per_question": 4
    }
    
    headers = {"Cookie": cookie, "Content-Type": "application/json"}
    r = requests.post(f"{NEXT_BASE}/api/quizzes/generate", json=payload, headers=headers)
    
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Quiz ID: {data.get('id')}")
        print(f"  Title: {data.get('title')}")
        print(f"  Questions: {len(data.get('questions', []))}")
        print(f"  ✅ Generate OK")
        return data
    else:
        print(f"  ⚠️ Generate returned {r.status_code}: {r.text[:200]}")
        return None


def test_generate_stream(cookie):
    """Test GET /api/quizzes/generate-stream via Next proxy (SSE)."""
    print("\n📡 Testing Generate Stream (GET /api/quizzes/generate-stream)...")
    
    params = {
        "topic": "React Hooks",
        "difficulty": "easy",
        "num_questions": 2,
        "options_per_question": 3
    }
    
    headers = {"Cookie": cookie}
    url = f"{NEXT_BASE}/api/quizzes/generate-stream"
    
    try:
        r = requests.get(url, params=params, headers=headers, stream=True, timeout=30)
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            events = []
            for line in r.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    event_data = json.loads(line[6:])
                    events.append(event_data)
                    print(f"  Event: {event_data.get('type')}")
                    if event_data.get('type') == 'complete':
                        break
            
            print(f"  ✅ Stream OK ({len(events)} events)")
            return events
        else:
            print(f"  ⚠️ Stream returned {r.status_code}: {r.text[:200]}")
            return []
    except Exception as e:
        print(f"  ⚠️ Stream error: {e}")
        return []


def test_saved_quizzes(cookie):
    """Test GET /api/quizzes/saved via Next proxy."""
    print("\n💾 Testing Saved Quizzes (GET /api/quizzes/saved)...")
    
    headers = {"Cookie": cookie}
    r = requests.get(f"{NEXT_BASE}/api/quizzes/saved", headers=headers)
    
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Saved count: {len(data)}")
        print(f"  ✅ Saved OK")
        return data
    else:
        print(f"  ⚠️ Saved returned {r.status_code}: {r.text[:200]}")
        return []


def test_session_start(cookie):
    """Test POST /api/quizzes/session/start via Next proxy."""
    print("\n🎯 Testing Session Start (POST /api/quizzes/session/start)...")
    
    params = {"path": "python-decorators"}
    headers = {"Cookie": cookie}
    r = requests.post(f"{NEXT_BASE}/api/quizzes/session/start", params=params, headers=headers)
    
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Session ID: {data.get('session_id')}")
        print(f"  Started at: {data.get('started_at')}")
        print(f"  ✅ Session Start OK")
        return data
    else:
        print(f"  ⚠️ Session Start returned {r.status_code}: {r.text[:200]}")
        return None


def test_rate_limit(cookie):
    """Test rate limiting on generate endpoint."""
    print("\n⚠️ Testing Rate Limit (POST /api/quizzes/generate x11)...")
    
    payload = {
        "topic": "rate-limit-test",
        "difficulty": "easy",
        "num_questions": 1,
        "options_per_question": 2
    }
    
    headers = {"Cookie": cookie, "Content-Type": "application/json"}
    success_count = 0
    rate_limited = False
    
    for i in range(11):
        r = requests.post(f"{NEXT_BASE}/api/quizzes/generate", json=payload, headers=headers)
        if r.status_code == 200:
            success_count += 1
        elif r.status_code == 429:
            rate_limited = True
            print(f"  Request {i+1}: 429 (Rate Limited) ✅")
            break
        else:
            print(f"  Request {i+1}: {r.status_code}")
    
    print(f"  Success: {success_count}, Rate Limited: {rate_limited}")
    if rate_limited:
        print(f"  ✅ Rate Limit enforced correctly")
    else:
        print(f"  ⚠️ Rate Limit not triggered after 10 requests")


def main():
    print("🚀 AI Quiz E2E Test Suite\n")
    print("=" * 60)
    
    try:
        # Auth
        cookie = test_auth()
        
        # Generate quiz (sync)
        quiz = test_generate_quiz(cookie)
        
        # Generate quiz (streaming)
        stream_events = test_generate_stream(cookie)
        
        # Saved quizzes
        saved = test_saved_quizzes(cookie)
        
        # Session start
        session = test_session_start(cookie)
        
        # Rate limit
        test_rate_limit(cookie)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
