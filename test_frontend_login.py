"""
Test login flow via Next.js frontend API proxy
"""
import requests
import json
from datetime import datetime

FRONTEND_BASE = "http://localhost:3000"
BACKEND_BASE = "http://127.0.0.1:8001"

def test_backend_health():
    """Test backend is responding"""
    print("\n" + "="*60)
    print("TEST 1: Backend Health Check")
    print("="*60)
    try:
        r = requests.get(f"{BACKEND_BASE}/healthz", timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_frontend_health():
    """Test frontend is responding"""
    print("\n" + "="*60)
    print("TEST 2: Frontend Health Check")
    print("="*60)
    try:
        r = requests.get(f"{FRONTEND_BASE}/", timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response length: {len(r.text)} bytes")
        return r.status_code == 200
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_direct_backend_login():
    """Test login directly against backend"""
    print("\n" + "="*60)
    print("TEST 3: Direct Backend Login")
    print("="*60)
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        r = requests.post(
            f"{BACKEND_BASE}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        # Check Set-Cookie
        set_cookie = r.headers.get("set-cookie", "")
        if set_cookie:
            print(f"Set-Cookie: {set_cookie[:100]}...")
            return r.status_code == 200
        else:
            print("FAIL: No Set-Cookie header!")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_frontend_proxy_login():
    """Test login via Next.js proxy route"""
    print("\n" + "="*60)
    print("TEST 4: Frontend Proxy Login (/api/session/login)")
    print("="*60)
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
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
        
        # Check Set-Cookie in response
        set_cookie = r.headers.get("set-cookie", "")
        if set_cookie:
            print(f"Set-Cookie: {set_cookie[:100]}...")
        else:
            print("WARNING: No Set-Cookie in response headers")
        
        # Check cookies in session
        print(f"Session cookies: {session.cookies.get_dict()}")
        
        if r.status_code == 200:
            print("PASS: Login via frontend proxy successful!")
            return True, session
        else:
            print(f"FAIL: Login returned status {r.status_code}")
            return False, None
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False, None

def test_authenticated_request(session):
    """Test /api/v1/auth/me with authenticated session"""
    print("\n" + "="*60)
    print("TEST 5: Authenticated Request (/api/v1/auth/me)")
    print("="*60)
    
    if not session:
        print("SKIP: No authenticated session")
        return False
    
    try:
        # Try via backend directly
        print("\n5a. Direct backend call:")
        r = session.get(f"{BACKEND_BASE}/api/v1/auth/me")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        # Try via frontend proxy
        print("\n5b. Via frontend proxy:")
        r2 = session.get(f"{FRONTEND_BASE}/api/session/v1x/auth/me")
        print(f"Status: {r2.status_code}")
        print(f"Response: {r2.text}")
        
        return r.status_code == 200 or r2.status_code == 200
        
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" FRONTEND LOGIN FLOW COMPREHENSIVE TEST")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Frontend: {FRONTEND_BASE}")
    print(f"Backend: {BACKEND_BASE}")
    
    results = []
    
    # Test 1: Backend health
    results.append(("Backend Health", test_backend_health()))
    
    # Test 2: Frontend health
    results.append(("Frontend Health", test_frontend_health()))
    
    # Test 3: Direct backend login
    results.append(("Direct Backend Login", test_direct_backend_login()))
    
    # Test 4: Frontend proxy login
    success, session = test_frontend_proxy_login()
    results.append(("Frontend Proxy Login", success))
    
    # Test 5: Authenticated request
    if success:
        results.append(("Authenticated Request", test_authenticated_request(session)))
    else:
        results.append(("Authenticated Request", False))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED - See details above")

if __name__ == "__main__":
    main()
