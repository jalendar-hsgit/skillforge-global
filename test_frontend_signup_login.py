"""
Create test user and test login flow
"""
import requests
import json
import random
from datetime import datetime

FRONTEND_BASE = "http://localhost:3000"
BACKEND_BASE = "http://127.0.0.1:8001"

# Generate unique email to avoid rate limiting
TEST_EMAIL = f"testuser{random.randint(1000, 9999)}@example.com"
TEST_PASSWORD = "TestPass123!"

def test_signup():
    """Create a new test user"""
    print("\n" + "="*60)
    print("TEST 1: Sign Up New User")
    print("="*60)
    print(f"Email: {TEST_EMAIL}")
    print(f"Password: {TEST_PASSWORD}")
    
    signup_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    
    try:
        r = requests.post(
            f"{FRONTEND_BASE}/api/session/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code in [200, 201]:
            print("PASS: User created successfully!")
            return True
        else:
            print(f"FAIL: Signup returned status {r.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_login():
    """Test login with the created user"""
    print("\n" + "="*60)
    print("TEST 2: Login via Frontend Proxy")
    print("="*60)
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        session = requests.Session()
        r = session.post(
            f"{FRONTEND_BASE}/api/session/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        # Check Set-Cookie
        set_cookie = r.headers.get("set-cookie", "")
        if set_cookie:
            print(f"Set-Cookie: {set_cookie[:150]}...")
            print("PASS: Cookie set successfully!")
        else:
            print("WARNING: No Set-Cookie header")
        
        # Check session cookies
        cookies = session.cookies.get_dict()
        print(f"Session cookies: {cookies}")
        
        if r.status_code == 200:
            if "token" in cookies or set_cookie:
                print("PASS: Login successful with cookie!")
                return True, session
            else:
                print("WARNING: Login successful but no token cookie found")
                return True, session
        else:
            print(f"FAIL: Login returned status {r.status_code}")
            return False, None
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False, None

def test_me_endpoint(session):
    """Test /me endpoint with authenticated session"""
    print("\n" + "="*60)
    print("TEST 3: Get Current User (/api/v1/auth/me)")
    print("="*60)
    
    if not session:
        print("SKIP: No authenticated session")
        return False
    
    try:
        # Try via backend directly with cookies
        print("\n3a. Direct backend call:")
        r = session.get(f"{BACKEND_BASE}/api/v1/auth/me")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        backend_ok = r.status_code == 200
        
        # Try via frontend proxy
        print("\n3b. Via frontend proxy (/api/session/me):")
        r2 = session.get(f"{FRONTEND_BASE}/api/session/me")
        print(f"Status: {r2.status_code}")
        print(f"Response: {r2.text}")
        proxy_ok = r2.status_code == 200
        
        if backend_ok or proxy_ok:
            print("PASS: Authenticated request successful!")
            return True
        else:
            print("FAIL: Both authenticated requests failed")
            return False
        
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" FRONTEND LOGIN FLOW TEST - WITH USER CREATION")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Frontend: {FRONTEND_BASE}")
    print(f"Backend: {BACKEND_BASE}")
    
    results = []
    
    # Test 1: Sign up
    signup_ok = test_signup()
    results.append(("Sign Up", signup_ok))
    
    if not signup_ok:
        print("\nCANNOT CONTINUE: Signup failed")
        return
    
    # Test 2: Login
    login_ok, session = test_login()
    results.append(("Login", login_ok))
    
    # Test 3: Authenticated request
    if login_ok and session:
        me_ok = test_me_endpoint(session)
        results.append(("Authenticated Request", me_ok))
    else:
        results.append(("Authenticated Request", False))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "checkmark" if passed else "X"
        print(f"{symbol} {name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n** ALL TESTS PASSED! **")
        print(f"\nTest credentials:")
        print(f"  Email: {TEST_EMAIL}")
        print(f"  Password: {TEST_PASSWORD}")
    else:
        print("\n** SOME TESTS FAILED **")

if __name__ == "__main__":
    main()
