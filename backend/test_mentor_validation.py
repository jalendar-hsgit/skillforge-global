"""
Test suite for mentor API validation and error handling
"""
import requests
import os

BASE = os.getenv("API_BASE", "http://localhost:8001")
TEST_EMAIL = "mentor@test.com"
TEST_PASSWORD = "password123"


def login():
    """Login and return token cookie"""
    res = requests.post(f"{BASE}/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    return res.cookies


def test_profile_validation():
    """Test profile update validation"""
    cookies = login()
    
    print("\n=== Testing Profile Validation ===\n")
    
    # Test bio too short
    print("1. Testing bio too short...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"bio": "Too short"}
    )
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    assert "at least 50" in res.text.lower()
    print("✅ Bio length validation works")
    
    # Test bio too long
    print("2. Testing bio too long...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"bio": "x" * 2001}
    )
    assert res.status_code == 400
    assert "exceed 2000" in res.text.lower()
    print("✅ Bio max length validation works")
    
    # Test invalid hourly rate (negative)
    print("3. Testing negative hourly rate...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"hourly_rate": -10}
    )
    assert res.status_code == 400
    assert "negative" in res.text.lower()
    print("✅ Negative rate validation works")
    
    # Test invalid hourly rate (too low)
    print("4. Testing hourly rate too low...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"hourly_rate": 5}
    )
    assert res.status_code == 400
    assert "at least $10" in res.text.lower()
    print("✅ Minimum rate validation works")
    
    # Test invalid hourly rate (too high)
    print("5. Testing hourly rate too high...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"hourly_rate": 1500}
    )
    assert res.status_code == 400
    assert "exceed $1000" in res.text.lower()
    print("✅ Maximum rate validation works")
    
    # Test too many skills
    print("6. Testing too many skills...")
    skills = ','.join([f"skill{i}" for i in range(25)])
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"expertise": skills}
    )
    assert res.status_code == 400
    assert "20 skills" in res.text.lower()
    print("✅ Max skills validation works")
    
    # Test valid update
    print("7. Testing valid profile update...")
    valid_bio = "I am an experienced full-stack developer with over 10 years of experience in building web applications."
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={
            "bio": valid_bio,
            "expertise": "Python,JavaScript,React,Node.js",
            "hourly_rate": 75
        }
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["bio"] == valid_bio
    assert data["hourly_rate"] == 75
    print("✅ Valid profile update works")


def test_session_state_transitions():
    """Test session state transition validation"""
    cookies = login()
    
    print("\n=== Testing Session State Transitions ===\n")
    
    # Get a pending session
    res = requests.get(f"{BASE}/api/v1x/mentor-portal/dashboard/sessions", cookies=cookies)
    sessions = res.json()["sessions"]
    
    if not sessions:
        print("⚠️  No sessions found, skipping state transition tests")
        return
    
    # Find a completed session to test invalid transitions
    completed = [s for s in sessions if s["status"] == "completed"]
    if completed:
        session_id = completed[0]["id"]
        
        print(f"1. Testing invalid transition: completed -> pending...")
        res = requests.patch(
            f"{BASE}/api/v1x/mentors/sessions/{session_id}",
            cookies=cookies,
            json={"status": "pending"}
        )
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        assert "invalid" in res.text.lower()
        print("✅ Prevents uncompleting sessions")
    
    # Find a confirmed session to test completion validation
    confirmed = [s for s in sessions if s["status"] == "confirmed"]
    if confirmed:
        session_id = confirmed[0]["id"]
        
        print(f"2. Testing valid transition: confirmed -> completed...")
        res = requests.patch(
            f"{BASE}/api/v1x/mentors/sessions/{session_id}",
            cookies=cookies,
            json={"status": "completed"}
        )
        # May fail if session is in the future, which is expected
        if res.status_code == 400:
            assert "hasn't started" in res.text.lower()
            print("✅ Prevents completing future sessions")
        else:
            assert res.status_code == 200
            print("✅ Allows completing past confirmed sessions")


def test_error_responses():
    """Test error response format and codes"""
    cookies = login()
    
    print("\n=== Testing Error Response Format ===\n")
    
    # Test 404 - mentor not found
    print("1. Testing 404 response...")
    res = requests.get(f"{BASE}/api/v1x/mentors/999999", cookies=cookies)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"
    data = res.json()
    assert "detail" in data or "error" in data, f"Expected error field in response: {data}"
    print("✅ 404 response format correct")
    
    # Test 400 - validation error
    print("2. Testing 400 validation error...")
    res = requests.patch(
        f"{BASE}/api/v1x/mentor-portal/profile",
        cookies=cookies,
        params={"hourly_rate": -50}
    )
    assert res.status_code == 400, f"Expected 400, got {res.status_code}"
    data = res.json()
    assert "detail" in data or "error" in data, f"Expected error field: {data}"
    print("✅ 400 validation error format correct")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 MENTOR API VALIDATION TESTS")
    print("=" * 60)
    
    try:
        test_profile_validation()
        test_session_state_transitions()
        test_error_responses()
        
        print("\n" + "=" * 60)
        print("✅ ALL VALIDATION TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
