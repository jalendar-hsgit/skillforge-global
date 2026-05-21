#!/usr/bin/env python3
"""
Test profile endpoint and verify demo data is showing
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def main():
    print("\n" + "="*70)
    print("PROFILE & BADGES ENDPOINT VERIFICATION")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Step 1: Login to get token via cookies
    print("\nSTEP 1: Login to get authentication")
    print("-"*70)
    
    session = requests.Session()
    login_url = f"{BASE_URL}/api/v1x/auth/login"
    creds = {"email": "john.doe@example.com", "password": "john123"}
    
    try:
        resp = session.post(login_url, json=creds, timeout=10)
        print(f"Login Status: {resp.status_code}")
        print(f"Login Response: {resp.json()}")
        
        if resp.status_code != 200:
            print(f"Login failed!")
            return
        
        if 'token' in session.cookies:
            print(f"Auth cookie set: token present")
        else:
            print(f"Auth cookie not found in response")
            
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Step 2: Get profile
    print("\nSTEP 2: Fetch Profile Data")
    print("-"*70)
    print("Endpoint: GET /api/v1x/account/profile")
    
    profile_url = f"{BASE_URL}/api/v1x/account/profile"
    
    try:
        resp = session.get(profile_url, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("\nProfile Data Retrieved:")
            print(f"  Name: {data.get('name')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Bio: {data.get('bio')}")
            print(f"  Skills: {data.get('skills')}")
            print(f"  Avatar: {data.get('avatar_url')}")
            print(f"  Location: {data.get('location')}")
            print(f"  Sessions Completed: {data.get('sessions_completed')}")
            print(f"  Avg Rating: {data.get('avg_rating')}")
            print(f"  Total Hours: {data.get('total_hours')}")
            
            # Check if demo data is showing
            if data.get('name') and data.get('bio'):
                print("\n[SUCCESS] Demo data is showing in profile!")
            else:
                print("\n[WARNING] Profile fields are empty")
        else:
            print(f"Error: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Step 3: Get badges
    print("\nSTEP 3: Fetch Badges")
    print("-"*70)
    print("Endpoint: GET /api/v1x/badges/user/earned")
    
    badges_url = f"{BASE_URL}/api/v1x/badges/user/earned"
    
    try:
        resp = session.get(badges_url, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            
            if isinstance(data, list):
                print(f"Badges Retrieved: {len(data)} earned")
                
                if len(data) > 0:
                    print("\nFirst Badge:")
                    badge = data[0]
                    print(f"  Name: {badge.get('name')}")
                    print(f"  Rarity: {badge.get('rarity')}")
                    print(f"  Points: {badge.get('points_value')}")
                else:
                    print("No badges earned yet (normal for new user)")
            else:
                print(f"Unexpected response type: {type(data)}")
                print(f"Response: {data}")
        else:
            print(f"Error: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
