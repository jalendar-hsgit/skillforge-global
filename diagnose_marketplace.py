#!/usr/bin/env python3
"""
Marketplace Courses Diagnostic
Checks why courses aren't showing in marketplace
"""

import sqlite3
import sys

def check_database():
    """Check if courses exist in database"""
    try:
        conn = sqlite3.connect('backend/app/data/skillforge.db')
        cursor = conn.cursor()
        
        # Check courses table
        cursor.execute('SELECT COUNT(*) FROM courses')
        count = cursor.fetchone()[0]
        print(f"\n✅ Database Check:")
        print(f"   Total courses in DB: {count}")
        
        if count == 0:
            print("   ❌ NO COURSES IN DATABASE!")
            print("   → Need to run: python backend/seed_all_demo_data.py")
            return False
        
        # Show first 3 courses
        cursor.execute('SELECT id, title, is_paid, price FROM courses LIMIT 3')
        courses = cursor.fetchall()
        for course in courses:
            print(f"   - ID: {course[0]}, Title: {course[1]}, Paid: {course[2]}, Price: ${course[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        return False

def check_api_endpoint():
    """Check if API endpoint returns courses"""
    try:
        import requests
        print(f"\n🔍 API Endpoint Check:")
        
        url = "http://localhost:8001/api/v1x/marketplace/courses"
        print(f"   Testing: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Returns list with {len(data)} courses")
                if len(data) > 0:
                    print(f"   First course: {data[0].get('title', 'No title')}")
                    return True
            else:
                print(f"   ⚠️  Returns object (not array): {type(data)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Backend not running!")
        print(f"   → Start backend: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def check_frontend():
    """Check frontend marketplace page"""
    print(f"\n🌐 Frontend Check:")
    print(f"   URL: http://localhost:3000/marketplace")
    print(f"   Check browser console for errors (F12)")
    print(f"   Expected: Courses list displaying")
    print(f"   If showing 'No courses found':")
    print(f"      → Backend might not be returning courses")
    print(f"      → Check API response: http://localhost:8001/api/v1x/marketplace/courses")

def main():
    print("=" * 70)
    print("MARKETPLACE COURSES - DIAGNOSTIC REPORT")
    print("=" * 70)
    
    # Check database
    db_ok = check_database()
    
    if not db_ok:
        print("\n🔧 FIX:")
        print("   1. Make sure backend is initialized:")
        print("      python backend/init_db.py")
        print("   2. Seed demo data:")
        print("      python backend/seed_all_demo_data.py")
        sys.exit(1)
    
    # Check API
    api_ok = check_api_endpoint()
    
    if not api_ok:
        print("\n🔧 FIX:")
        print("   1. Make sure backend is running:")
        print("      cd backend")
        print("      uvicorn app.main:app --reload")
        print("   2. Wait for startup to complete")
        print("   3. Try accessing: http://localhost:8001/api/v1x/marketplace/courses")
        sys.exit(1)
    
    # Check frontend
    check_frontend()
    
    print("\n" + "=" * 70)
    print("✅ ALL CHECKS PASSED")
    print("=" * 70)
    print("\nIf marketplace still shows 'No courses found':")
    print("  1. Open browser console (F12)")
    print("  2. Look for network errors")
    print("  3. Check 'Network' tab for API call responses")
    print("  4. Verify NEXT_PUBLIC_API_BASE is set correctly:")
    print("     Should be: http://localhost:8001")
    print("\nIf still stuck:")
    print("  $ curl http://localhost:8001/api/v1x/marketplace/courses")

if __name__ == "__main__":
    main()
