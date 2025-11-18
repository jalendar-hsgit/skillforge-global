"""Test authentication endpoints directly."""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_signup():
    """Test user signup."""
    print("\n=== Testing Signup ===")
    url = f"{BASE_URL}/api/v1/auth/signup"
    
    # Generate unique email
    import time
    email = f"test_{int(time.time())}@example.com"
    
    payload = {
        "email": email,
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}")
        
        if response.ok:
            print("✅ Signup successful")
            return response.json(), response.cookies
        else:
            print(f"❌ Signup failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def test_login():
    """Test user login."""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/api/v1/auth/login"
    
    # Use known credentials or create new user first
    signup_data, _ = test_signup()
    if not signup_data:
        print("❌ Cannot test login - signup failed")
        return None, None
    
    payload = {
        "email": signup_data.get("email"),
        "password": "TestPass123!"
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Cookies: {dict(response.cookies)}")
        print(f"Response: {response.text[:500]}")
        
        if response.ok:
            print("✅ Login successful")
            return response.json(), response.cookies
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def test_me(cookies):
    """Test /me endpoint with auth cookie."""
    print("\n=== Testing /me Endpoint ===")
    url = f"{BASE_URL}/api/v1/auth/me"
    
    print(f"GET {url}")
    print(f"Cookies: {dict(cookies) if cookies else 'None'}")
    
    try:
        response = requests.get(url, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.ok:
            print("✅ /me successful")
            return response.json()
        else:
            print(f"❌ /me failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run all auth tests."""
    print("=" * 60)
    print("Authentication Endpoint Tests")
    print("=" * 60)
    
    # Test signup and login flow
    _, cookies = test_login()
    
    # Test authenticated endpoint
    if cookies:
        test_me(cookies)
    else:
        print("\n❌ Skipping /me test - no valid cookies")
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
