#!/usr/bin/env python
"""
Test Admin Analytics Backend Integration
Verifies all 6 analytics endpoints respond correctly
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_analytics_endpoints():
    print("\n" + "="*60)
    print("Testing Admin Analytics Endpoints")
    print("="*60)
    
    endpoints = [
        ("/api/v1x/analytics/overview", "GET", "KPI Overview"),
        ("/api/v1x/analytics/daily-active-users?days=30", "GET", "Daily Active Users"),
        ("/api/v1x/analytics/revenue-breakdown", "GET", "Revenue Breakdown"),
        ("/api/v1x/analytics/feature-adoption", "GET", "Feature Adoption"),
        ("/api/v1x/analytics/mentors-performance?limit=10", "GET", "Mentor Performance"),
        ("/api/v1x/analytics/student-engagement", "GET", "Student Engagement"),
    ]
    
    results = []
    
    for endpoint, method, description in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n📊 Testing: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            
            print(f"   Status: {status}")
            
            if status == 401:
                print(f"   ✅ EXPECTED: 401 (Auth Required) - Endpoint exists and is protected")
                results.append((description, "✅ WORKING (auth protected)"))
            elif status == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Returned {len(json.dumps(data))} bytes")
                    results.append((description, "✅ WORKING"))
                except:
                    print(f"   ✅ SUCCESS: Got 200 response")
                    results.append((description, "✅ WORKING"))
            elif status == 404:
                print(f"   ❌ NOT FOUND: Endpoint does not exist")
                results.append((description, "❌ NOT FOUND"))
            elif status == 500:
                print(f"   ❌ SERVER ERROR: {response.text[:100]}")
                results.append((description, "❌ ERROR"))
            else:
                print(f"   ⚠️  UNKNOWN: Status {status}")
                results.append((description, f"⚠️ {status}"))
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to {BASE_URL}")
            results.append((description, "❌ CONNECTION ERROR"))
            break
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append((description, "❌ ERROR"))
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for desc, status in results:
        print(f"  {status:<30} {desc}")
    
    total = len(results)
    working = len([r for r in results if "WORKING" in r[1]])
    print(f"\n✅ {working}/{total} endpoints responding")

if __name__ == "__main__":
    test_analytics_endpoints()
