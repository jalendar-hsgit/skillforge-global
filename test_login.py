#!/usr/bin/env python3
"""
Quick test script to check if backend is running and login works
Run this from the repo root: python test_login.py
"""

import sys
import subprocess
import time
import requests
import json

def check_backend_running():
    """Check if backend is running on port 8001"""
    try:
        response = requests.get("http://localhost:8001/", timeout=2)
        return True
    except:
        return False

def start_backend():
    """Start the backend if not running"""
    print("[TEST] Starting backend...")
    try:
        # Change to backend directory and start uvicorn
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("[TEST] Backend process started. Waiting for startup (5 seconds)...")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"[TEST] Error starting backend: {e}")
        return False

def test_login():
    """Test the login endpoint"""
    print("\n" + "=" * 60)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8001/api/v1x/auth/login",
            json={
                "email": "superadmin@skillforge.com",
                "password": "superadmin"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ LOGIN SUCCESSFUL!")
                print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
                print(f"   User ID: {data.get('user_id')}")
                return True
            else:
                print(f"\n❌ LOGIN FAILED")
                print(f"   Error: {data.get('detail', 'Unknown error')}")
                return False
        except:
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (database may be locked)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused (backend not running)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("LOGIN TEST SCRIPT")
    print("=" * 60)
    
    # Check if backend is running
    if not check_backend_running():
        print("\n[TEST] Backend not running. Attempting to start...")
        if not start_backend():
            print("\n[TEST] Failed to start backend automatically")
            print("[TEST] Please start manually:")
            print("       cd backend && python -m uvicorn app.main:app --reload")
            return False
    else:
        print("[TEST] ✅ Backend already running")
    
    # Test login
    if test_login():
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - LOGIN IS WORKING!")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ LOGIN FAILED - SEE ERROR ABOVE")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
