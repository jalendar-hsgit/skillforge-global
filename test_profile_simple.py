#!/usr/bin/env python3
"""
Simple test to check profile endpoint and demo data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_endpoints():
    """Test profile and badges endpoints"""
    print("\n" + "="*70)
    print("PROFILE & BADGES ENDPOINT VERIFICATION")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Step 1: Login
    print("\nSTEP 1: Get Auth Token")
    print("-"*70)
    
    login_url = f"{BASE_URL}/api/v1x/auth/login"
    creds = {"email": "john.doe@example.com", "password": "john123"}
    
    # Use session to handle cookies and also get JWT
    session = requests.Session()
    
    try:
        response = session.post(login_url, json=creds, timeout=10)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login Failed: {response.text}")
            return
        
        data = response.json()
        print(f"Login Response: {data}")
        
        # Check if token is in cookie or response
        if 'token' in session.cookies:
            token = session.cookies['token']
            print(f"Token from cookie: {token[:20]}...")
        else:
            token = None
            print("No token cookie found - will test with /auth/me endpoint")
    except Exception as e:
        print(f"Login Error: {e}")
        return
    
    # Step 2: Test profile endpoint
    print("\nSTEP 2: Test Profile Endpoint")
    print("-"*70)
    print("Endpoint: GET /api/v1x/account/profile")
    
    profile_url = f"{BASE_URL}/api/v1x/account/profile"
    
    if token:
        # Use Bearer token
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(profile_url, headers=headers, timeout=10)
        except Exception as e:
            print(f"Error with Bearer token: {e}")
            return
    else:
        # Use session cookies
        try:
            response = session.get(profile_url, timeout=10)
        except Exception as e:
            print(f"Error with session: {e}")
            return
    
    print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nProfile Data:")
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
            
            if data.get('name') and data.get('bio'):
                print("\n[SUCCESS] Demo data is showing in profile!")
            else:
                print("\n[WARNING] Profile is missing demo data")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Step 3: Test badges endpoint
    print("\nSTEP 3: Test Badges Endpoint")
    print("-"*70)
    print("Endpoint: GET /api/v1x/badges/user/earned")
    
    badges_url = f"{BASE_URL}/api/v1x/badges/user/earned"
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(badges_url, headers=headers, timeout=10)
        except Exception as e:
            print(f"Error with Bearer token: {e}")
            return
    else:
        try:
            response = session.get(badges_url, timeout=10)
        except Exception as e:
            print(f"Error with session: {e}")
            return
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"\nBadges Data:")
                print(f"  Total Earned: {len(data)}")
                
                if len(data) > 0:
                    print("\n  First Badge:")
                    badge = data[0]
                    print(f"    Name: {badge.get('name')}")
                    print(f"    Rarity: {badge.get('rarity')}")
                    print(f"    Points: {badge.get('points_value')}")
                    print(f"    Earned: {badge.get('earned_at')}")
                else:
                    print("  No badges earned yet (normal for new users)")
                
                print("\n[SUCCESS] Badges endpoint is working!")
            else:
                print(f"Unexpected response: {type(data)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_endpoints()
