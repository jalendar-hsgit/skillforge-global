#!/usr/bin/env python3
"""
Test script to verify all student dashboard endpoints are working
Run this after logging in to get an auth token
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_BASE = "http://localhost:8001"
ENDPOINTS = [
    "/api/v1x/student/dashboard/overview",
    "/api/v1x/student/dashboard/courses",
    "/api/v1x/student/dashboard/recent-activity",
    "/api/v1x/student/dashboard/quiz-results",
    "/api/v1x/student/dashboard/achievements",
    "/api/v1x/student/dashboard/recommendations",
]

def test_endpoints(token: str):
    """Test all student dashboard endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("=" * 70)
    print("STUDENT DASHBOARD ENDPOINTS TEST")
    print("=" * 70)
    print(f"Testing {len(ENDPOINTS)} endpoints...\n")
    
    results = {
        "passed": [],
        "failed": [],
        "timestamp": datetime.now().isoformat()
    }
    
    for endpoint in ENDPOINTS:
        url = f"{BACKEND_BASE}{endpoint}"
        print(f"Testing: {endpoint}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: 200 OK")
                print(f"   Response keys: {list(data.keys())}")
                results["passed"].append({
                    "endpoint": endpoint,
                    "status": 200,
                    "response_keys": list(data.keys())
                })
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                results["failed"].append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "error": response.text[:200]
                })
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: Request took too long")
            results["failed"].append({
                "endpoint": endpoint,
                "error": "Request timeout"
            })
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Could not connect to backend")
            results["failed"].append({
                "endpoint": endpoint,
                "error": "Connection error - backend may not be running"
            })
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results["failed"].append({
                "endpoint": endpoint,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {len(results['passed'])}/{len(ENDPOINTS)}")
    print(f"❌ Failed: {len(results['failed'])}/{len(ENDPOINTS)}")
    print()
    
    if results["passed"]:
        print("✅ WORKING ENDPOINTS:")
        for result in results["passed"]:
            print(f"  - {result['endpoint']}")
            print(f"    Status: {result['status']}")
            print(f"    Response: {', '.join(result['response_keys'])}")
    
    if results["failed"]:
        print("\n❌ FAILED ENDPOINTS:")
        for result in results["failed"]:
            print(f"  - {result['endpoint']}")
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    # Save results to file
    with open("student_dashboard_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n📄 Results saved to: student_dashboard_test_results.json")
    
    return len(results["failed"]) == 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_student_dashboard.py <auth_token>")
        print("\nTo get an auth token:")
        print("1. Log in at http://localhost:3000/login")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application > Cookies")
        print("4. Find the 'token' cookie and copy its value")
        print("5. Run: python test_student_dashboard.py <token_value>")
        sys.exit(1)
    
    token = sys.argv[1]
    success = test_endpoints(token)
    sys.exit(0 if success else 1)
