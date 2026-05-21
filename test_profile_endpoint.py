#!/usr/bin/env python3
"""
Test script to verify profile endpoint returns demo data correctly
Tests both frontend and backend flows
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def get_auth_token():
    """Login and get JWT token"""
    login_url = f"{BASE_URL}/api/v1x/auth/login"
    
    # Try with demo user
    creds = {
        "email": "john.doe@example.com",
        "password": "john123"
    }
    
    try:
        response = requests.post(login_url, json=creds, timeout=5)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token obtained: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_profile_endpoint(token):
    """Test the profile endpoint"""
    if not token:
        print("❌ No token available")
        return
    
    profile_url = f"{BASE_URL}/api/v1x/account/profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*70)
    print("TESTING: GET /api/v1x/account/profile")
    print("="*70)
    
    try:
        response = requests.get(profile_url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ PROFILE DATA RECEIVED:")
            print(f"  ID: {data.get('id')}")
            print(f"  Name: {data.get('name')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Bio: {data.get('bio')}")
            print(f"  Avatar: {data.get('avatar_url')}")
            print(f"  Location: {data.get('location')}")
            print(f"  Skills: {data.get('skills')}")
            print(f"  Sessions Completed: {data.get('sessions_completed')}")
            print(f"  Avg Rating: {data.get('avg_rating')}")
            print(f"  Total Hours: {data.get('total_hours')}")
            print(f"  Created At: {data.get('created_at')}")
            
            # Check if demo data is showing
            if data.get('name') and data.get('bio'):
                print("\n✅ DEMO DATA IS SHOWING CORRECTLY!")
                return True
            else:
                print("\n⚠️  Missing bio or name")
                return False
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_badges_endpoint(token):
    """Test the badges endpoint"""
    if not token:
        print("❌ No token available")
        return
    
    badges_url = f"{BASE_URL}/api/v1x/badges/user/earned"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*70)
    print("TESTING: GET /api/v1x/badges/user/earned")
    print("="*70)
    
    try:
        response = requests.get(badges_url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"\n✅ BADGES DATA RECEIVED:")
                print(f"  Total Badges: {len(data)}")
                
                if len(data) > 0:
                    for i, badge in enumerate(data[:3]):
                        print(f"\n  Badge {i+1}:")
                        print(f"    Name: {badge.get('name')}")
                        print(f"    Rarity: {badge.get('rarity')}")
                        print(f"    Points: {badge.get('points_value')}")
                        print(f"    Earned: {badge.get('earned_at')}")
                else:
                    print("  No earned badges yet (this is normal for new users)")
                return True
            else:
                print(f"❌ Unexpected response format: {type(data)}")
                return False
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PROFILE ENDPOINT VERIFICATION TEST")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Step 1: Get auth token
    print("\n" + "-"*70)
    print("STEP 1: Authentication")
    print("-"*70)
    token = get_auth_token()
    
    if not token:
        print("\n❌ Cannot proceed without token")
        return
    
    # Step 2: Test profile endpoint
    print("\n" + "-"*70)
    print("STEP 2: Profile Endpoint")
    print("-"*70)
    profile_ok = test_profile_endpoint(token)
    
    # Step 3: Test badges endpoint
    print("\n" + "-"*70)
    print("STEP 3: Badges Endpoint")
    print("-"*70)
    badges_ok = test_badges_endpoint(token)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Profile Endpoint: {'✅ PASS' if profile_ok else '❌ FAIL'}")
    print(f"Badges Endpoint: {'✅ PASS' if badges_ok else '❌ FAIL'}")
    
    if profile_ok and badges_ok:
        print("\n✅ ALL TESTS PASSED - DEMO DATA IS SHOWING CORRECTLY!")
    else:
        print("\n⚠️  SOME TESTS FAILED - CHECK ABOVE FOR DETAILS")


if __name__ == "__main__":
    main()
