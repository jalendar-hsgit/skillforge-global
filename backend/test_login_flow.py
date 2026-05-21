"""
Test login flow directly against backend and via Next.js proxy
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"
NEXT_API_BASE = "http://localhost:3000"

def test_direct_backend_login():
    """Test login directly against backend"""
    print("=" * 60)
    print("TEST 1: Direct backend login")
    print("=" * 60)
    
    # Use credentials from previous successful tests
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        
        # Check for Set-Cookie header
        if "set-cookie" in response.headers:
            print(f"\nSet-Cookie: {response.headers['set-cookie']}")
        else:
            print("\nWARNING: No Set-Cookie header in response!")
        
        if response.status_code == 200:
            print("\nDirect backend login: PASS")
            return True
        else:
            print(f"\nDirect backend login: FAIL (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_health_check():
    """Test backend health check"""
    print("\n" + "=" * 60)
    print("TEST 0: Backend health check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("LOGIN FLOW DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test 0: Health check
    if not test_health_check():
        print("\nBackend is not responding. Make sure it's running on port 8001.")
        return
    
    # Test 1: Direct backend login
    test_direct_backend_login()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. If direct backend login works, test via Next.js proxy")
    print("2. Start Next.js dev server: npm run dev")
    print("3. Try logging in via http://localhost:3000/login")
    print("4. Check browser console for errors")
    print("5. Check browser Network tab for cookie setting")

if __name__ == "__main__":
    main()
