"""Quick test script for admin signup functionality"""
import requests
import json

API_BASE = "http://localhost:8001"

def test_admin_signup():
    """Test admin signup endpoint"""
    print("Testing admin signup...")
    
    # Test data
    email = "admin_test@example.com"
    password = "SecurePass123"
    role = "admin"
    
    # Signup request
    signup_url = f"{API_BASE}/api/v1/auth/signup"
    signup_data = {
        "email": email,
        "password": password,
        "role": role
    }
    
    print(f"\n1. Signing up as {role}: {email}")
    try:
        response = requests.post(signup_url, json=signup_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✓ Signup successful!")
        else:
            print(f"   ✗ Signup failed: {response.json().get('detail')}")
            return
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Login to verify
    print(f"\n2. Logging in as {email}")
    login_url = f"{API_BASE}/api/v1/auth/login"
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✓ Login successful!")
            
            # Get session cookie
            session_cookie = response.cookies.get('token')
            if session_cookie:
                print(f"   Token cookie set: {session_cookie[:20]}...")
            
            # Check /me endpoint
            print(f"\n3. Checking user details via /api/v1/auth/me")
            me_url = f"{API_BASE}/api/v1/auth/me"
            me_response = requests.get(me_url, cookies=response.cookies)
            print(f"   Status: {me_response.status_code}")
            user_data = me_response.json()
            print(f"   User: {json.dumps(user_data, indent=2)}")
            
            if user_data.get('role') == role:
                print(f"   ✓ Role correctly set to '{role}'!")
            else:
                print(f"   ✗ Role mismatch: expected '{role}', got '{user_data.get('role')}'")
        else:
            print(f"   ✗ Login failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_superadmin_signup():
    """Test superadmin signup"""
    print("\n" + "="*60)
    print("Testing superadmin signup...")
    
    email = "superadmin_test@example.com"
    password = "SecurePass123"
    role = "superadmin"
    
    signup_url = f"{API_BASE}/api/v1/auth/signup"
    signup_data = {
        "email": email,
        "password": password,
        "role": role
    }
    
    print(f"\n1. Signing up as {role}: {email}")
    try:
        response = requests.post(signup_url, json=signup_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✓ Signup successful!")
            
            # Verify role
            print(f"\n2. Logging in to verify role")
            login_response = requests.post(
                f"{API_BASE}/api/v1/auth/login",
                json={"email": email, "password": password}
            )
            
            if login_response.status_code == 200:
                me_response = requests.get(
                    f"{API_BASE}/api/v1/auth/me",
                    cookies=login_response.cookies
                )
                user_data = me_response.json()
                print(f"   User role: {user_data.get('role')}")
                
                if user_data.get('role') == role:
                    print(f"   ✓ Superadmin role correctly set!")
                else:
                    print(f"   ✗ Role mismatch!")
        else:
            print(f"   ✗ Signup failed: {response.json().get('detail')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Admin Signup Test Suite")
    print("=" * 60)
    
    test_admin_signup()
    test_superadmin_signup()
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)
