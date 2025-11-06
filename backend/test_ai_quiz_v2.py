"""
Test script for AI Quiz Generation v2 features.
Tests rate limiting, admin endpoints, saved quizzes, and session tracking.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Test credentials
TEST_USER = {"email": "test@example.com", "password": "testpass123"}
session = requests.Session()


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_auth():
    """Login to get session cookie."""
    print_section("Authentication")
    
    # Try signup first (might fail if user exists)
    r = session.post(f"{API_V1}/auth/signup", json=TEST_USER)
    print(f"Signup: {r.status_code}")
    
    # Login
    r = session.post(f"{API_V1}/auth/login", json=TEST_USER)
    print(f"Login: {r.status_code}")
    
    if r.status_code == 200:
        print("✓ Authenticated successfully")
        return True
    else:
        print(f"✗ Authentication failed: {r.text}")
        return False


def test_quiz_generation():
    """Test AI quiz generation with rate limiting."""
    print_section("AI Quiz Generation")
    
    payload = {
        "topic": "Python AsyncIO",
        "difficulty": "medium",
        "num_questions": 3,
        "options_per_question": 4
    }
    
    r = session.post(f"{API_V1}/quizzes/generate", json=payload)
    print(f"Generate quiz: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Generated quiz: {data.get('title')}")
        print(f"  Questions: {len(data.get('questions', []))}")
        return data
    else:
        print(f"✗ Generation failed: {r.text}")
        return None


def test_rate_limiting():
    """Test rate limiting on generation endpoints."""
    print_section("Rate Limiting Test")
    
    print("Attempting 11 rapid requests (limit is 10 per 5min)...")
    
    payload = {
        "topic": "JavaScript",
        "difficulty": "easy",
        "num_questions": 2,
        "options_per_question": 4
    }
    
    success_count = 0
    rate_limited = False
    
    for i in range(11):
        r = session.post(f"{API_V1}/quizzes/generate", json=payload)
        if r.status_code == 200:
            success_count += 1
            print(f"  Request {i+1}: ✓ Success")
        elif r.status_code == 429:
            rate_limited = True
            print(f"  Request {i+1}: ⚠ Rate limited")
            print(f"    Response: {r.json().get('detail')}")
            break
        else:
            print(f"  Request {i+1}: ✗ Error {r.status_code}")
        
        time.sleep(0.1)  # Small delay between requests
    
    if rate_limited:
        print(f"✓ Rate limiting working: {success_count} succeeded, then limited")
    else:
        print(f"⚠ No rate limit hit (sent {success_count} requests)")


def test_saved_quizzes():
    """Test saved quiz management."""
    print_section("Saved Quiz Management")
    
    # Generate and save a quiz
    payload = {
        "topic": "React Hooks",
        "difficulty": "hard",
        "num_questions": 3,
        "options_per_question": 4
    }
    
    r = session.post(f"{API_V1}/quizzes/generate?save=true", json=payload)
    print(f"Generate & save: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        saved_id = data.get('saved_id')
        print(f"✓ Saved quiz ID: {saved_id}")
        
        # List saved quizzes
        r = session.get(f"{API_V1}/quizzes/saved")
        if r.status_code == 200:
            quizzes = r.json()
            print(f"✓ User has {len(quizzes)} saved quizzes")
            
            # Retrieve specific quiz
            if saved_id:
                r = session.get(f"{API_V1}/quizzes/saved/{saved_id}")
                if r.status_code == 200:
                    print(f"✓ Retrieved saved quiz: {r.json().get('title')}")
                    
                    # Toggle favorite
                    r = session.post(f"{API_V1}/quizzes/saved/{saved_id}/favorite")
                    if r.status_code == 200:
                        print(f"✓ Favorited: {r.json().get('is_favorite')}")
    else:
        print(f"✗ Save failed: {r.text}")


def test_session_tracking():
    """Test quiz session tracking."""
    print_section("Session Tracking")
    
    # Start a session
    r = session.post(f"{API_V1}/quizzes/session/start?path=test-session")
    print(f"Start session: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        session_id = data.get('session_id')
        print(f"✓ Session ID: {session_id}")
        print(f"  Started at: {data.get('started_at')}")
    else:
        print(f"✗ Session start failed: {r.text}")


def test_admin_endpoints():
    """Test admin analytics endpoints."""
    print_section("Admin Analytics")
    
    # Stats
    r = session.get(f"{API_V1}/admin/quizzes/stats")
    print(f"Admin stats: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Total generated: {data.get('total_generated')}")
        print(f"  Last 24h: {data.get('last_24h')}")
        print(f"  Avg score: {data.get('avg_score_pct')}%")
        print(f"  Top topics: {[t['topic'] for t in data.get('top_topics', [])[:3]]}")
    elif r.status_code == 403:
        print("⚠ Admin access denied (expected for non-admin users)")
    else:
        print(f"✗ Stats failed: {r.text}")
    
    # Recent quizzes
    r = session.get(f"{API_V1}/admin/quizzes/recent?limit=5")
    print(f"Recent quizzes: {r.status_code}")
    
    if r.status_code == 200:
        quizzes = r.json()
        print(f"✓ Got {len(quizzes)} recent quizzes")
    elif r.status_code == 403:
        print("⚠ Admin access denied")


def test_streaming():
    """Test SSE streaming endpoint."""
    print_section("Streaming Generation (SSE)")
    
    params = {
        "topic": "TypeScript Generics",
        "difficulty": "medium",
        "num_questions": 2,
        "options_per_question": 4
    }
    
    print("Starting SSE stream...")
    try:
        r = session.get(f"{API_V1}/quizzes/generate-stream", params=params, stream=True, timeout=30)
        print(f"Stream status: {r.status_code}")
        
        if r.status_code == 200:
            question_count = 0
            for line in r.iter_lines(decode_unicode=True):
                if line and line.startswith('data: '):
                    data = json.loads(line[6:])
                    event_type = data.get('type')
                    
                    if event_type == 'metadata':
                        print(f"✓ Stream started: {data.get('title')}")
                    elif event_type == 'question':
                        question_count += 1
                        q = data.get('data', {})
                        print(f"  Question {question_count}: {q.get('text', '')[:50]}...")
                    elif event_type == 'complete':
                        print(f"✓ Stream complete: {data.get('total')} questions")
                        break
                    elif event_type == 'error':
                        print(f"✗ Stream error: {data.get('message')}")
                        break
        elif r.status_code == 429:
            print("⚠ Rate limited (expected after previous tests)")
        else:
            print(f"✗ Stream failed: {r.text}")
    except Exception as e:
        print(f"✗ Stream error: {e}")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("  AI Quiz Generation v2 - Integration Tests")
    print("="*60)
    
    if not test_auth():
        print("\n✗ Authentication failed - stopping tests")
        return
    
    test_quiz_generation()
    test_saved_quizzes()
    test_session_tracking()
    test_streaming()
    test_rate_limiting()  # Run this last as it will hit limits
    test_admin_endpoints()
    
    print("\n" + "="*60)
    print("  Test Suite Complete")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
