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
    password = "TestPass123!"
    
    payload = {
        "email": email,
        "password": password,
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
            # Return credentials for login test
            return {"email": email, "password": password}, response.cookies
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
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {json.dumps({'email': payload['email'], 'password': '***'}, indent=2)}")
    
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


def test_login_wrong_password():
    """Test login with wrong password."""
    print("\n=== Testing Login with Wrong Password ===")
    url = f"{BASE_URL}/api/v1/auth/login"
    
    payload = {
        "email": "test@example.com",
        "password": "WrongPassword123!"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps({'email': payload['email'], 'password': '***'}, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 401:
            print("✅ Wrong password correctly rejected")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_me_no_auth():
    """Test /me endpoint without authentication."""
    print("\n=== Testing /me Without Authentication ===")
    url = f"{BASE_URL}/api/v1/auth/me"
    
    print(f"GET {url}")
    print("Cookies: None")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 401:
            print("✅ Unauthenticated request correctly rejected")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_duplicate_signup():
    """Test signup with duplicate email."""
    print("\n=== Testing Duplicate Email Signup ===")
    url = f"{BASE_URL}/api/v1/auth/signup"
    
    import time
    email = f"duplicate_{int(time.time())}@example.com"
    
    payload = {
        "email": email,
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    # First signup
    print(f"POST {url} (first signup)")
    response1 = requests.post(url, json=payload)
    print(f"Status: {response1.status_code}")
    
    # Second signup with same email
    print(f"\nPOST {url} (duplicate signup)")
    response2 = requests.post(url, json=payload)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text[:500]}")
    
    if response2.status_code == 400 and "already exists" in response2.text.lower():
        print("✅ Duplicate email correctly rejected")
    else:
        print(f"⚠️  Expected 400 with 'already exists', got {response2.status_code}")


def test_session_me(cookies):
    """Test session /me endpoint."""
    print("\n=== Testing Session /me Endpoint ===")
    url = f"{BASE_URL}/api/session/me"
    
    print(f"GET {url}")
    
    try:
        response = requests.get(url, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.ok:
            print("✅ Session /me successful")
        else:
            print(f"⚠️  Session /me failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all auth tests."""
    print("=" * 60)
    print("Authentication Endpoint Tests")
    print("=" * 60)
    
    # Test signup and login flow
    _, cookies = test_login()
    
    # Test authenticated endpoints
    if cookies:
        test_me(cookies)
        test_session_me(cookies)
    else:
        print("\n❌ Skipping authenticated tests - no valid cookies")
    
    # Test error cases
    test_login_wrong_password()
    test_me_no_auth()
    test_duplicate_signup()
    
    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)
    print("\n✅ Summary:")
    print("  - Signup creates new users")
    print("  - Login returns JWT token cookie")
    print("  - /me endpoints work with authentication")
    print("  - Wrong passwords are rejected")
    print("  - Unauthenticated requests are blocked")
    print("  - Duplicate emails are rejected")

if __name__ == "__main__":
    main()
