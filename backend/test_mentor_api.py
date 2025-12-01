"""
Comprehensive test suite for Mentor Portal API endpoints
Tests all 8 mentor-portal dashboard endpoints
"""
import sys
sys.path.insert(0, 'D:\\python code\\sfg\\skillforge-global\\backend')

import requests
from datetime import datetime, timedelta

# Config
API_BASE = "http://localhost:8001"
TEST_USER_EMAIL = "test@example.com"  # Change to your test mentor email
TEST_PASSWORD = "password123"  # Change to your test password

class MentorPortalTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login(self):
        """Login and get auth cookie"""
        print("\n🔐 Logging in...")
        res = self.session.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_PASSWORD}
        )
        if res.status_code == 200:
            print(f"✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {res.status_code} - {res.text}")
            return False
    
    def test_overview(self):
        """Test GET /api/v1x/mentor-portal/dashboard/overview"""
        print("\n📊 Testing Overview Endpoint...")
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/overview")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Overview endpoint successful")
            print(f"   Total earnings: ${data.get('total_earnings', 0):.2f}")
            print(f"   Total sessions: {data.get('total_sessions', 0)}")
            print(f"   Average rating: {data.get('average_rating', 0):.1f}⭐")
            print(f"   Unique students: {data.get('unique_students', 0)}")
            return True
        else:
            print(f"❌ Overview failed: {res.status_code} - {res.text}")
            return False
    
    def test_sessions(self):
        """Test GET /api/v1x/mentor-portal/dashboard/sessions"""
        print("\n📅 Testing Sessions Endpoint...")
        
        # Test without filter
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/sessions")
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Sessions endpoint successful (all)")
            print(f"   Total sessions: {data.get('total', 0)}")
            print(f"   Returned: {len(data.get('sessions', []))}")
        else:
            print(f"❌ Sessions (all) failed: {res.status_code}")
            return False
        
        # Test with status filter
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/sessions?status=pending")
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Sessions with filter successful")
            print(f"   Pending sessions: {len(data.get('sessions', []))}")
            return True
        else:
            print(f"❌ Sessions (filtered) failed: {res.status_code}")
            return False
    
    def test_earnings(self):
        """Test GET /api/v1x/mentor-portal/dashboard/earnings"""
        print("\n💰 Testing Earnings Endpoint...")
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/earnings")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Earnings endpoint successful")
            print(f"   Total earnings: ${data.get('total_earnings', 0):.2f}")
            print(f"   This month: ${data.get('this_month', 0):.2f}")
            print(f"   Pending payout: ${data.get('pending_payout', 0):.2f}")
            print(f"   Monthly breakdown: {len(data.get('monthly_breakdown', []))} months")
            print(f"   Top students: {len(data.get('top_students', []))}")
            return True
        else:
            print(f"❌ Earnings failed: {res.status_code} - {res.text}")
            return False
    
    def test_students(self):
        """Test GET /api/v1x/mentor-portal/dashboard/students"""
        print("\n👥 Testing Students Endpoint...")
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/students")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Students endpoint successful")
            print(f"   Total students: {data.get('total', 0)}")
            print(f"   Returned: {len(data.get('students', []))}")
            if data.get('students'):
                student = data['students'][0]
                print(f"   Sample: Student #{student.get('student_id')} - {student.get('session_count')} sessions")
            return True
        else:
            print(f"❌ Students failed: {res.status_code} - {res.text}")
            return False
    
    def test_analytics(self):
        """Test GET /api/v1x/mentor-portal/dashboard/analytics"""
        print("\n📈 Testing Analytics Endpoint...")
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/analytics")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Analytics endpoint successful")
            print(f"   Total sessions: {data.get('total_sessions', 0)}")
            print(f"   Status breakdown: {len(data.get('sessions_by_status', {}))} statuses")
            print(f"   Rating distribution: {len(data.get('rating_distribution', {}))} ratings")
            print(f"   Sessions by day: {len(data.get('sessions_by_day', []))} days")
            return True
        else:
            print(f"❌ Analytics failed: {res.status_code} - {res.text}")
            return False
    
    def test_reviews(self):
        """Test GET /api/v1x/mentor-portal/dashboard/reviews"""
        print("\n⭐ Testing Reviews Endpoint...")
        res = self.session.get(f"{API_BASE}/api/v1x/mentor-portal/dashboard/reviews")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Reviews endpoint successful")
            print(f"   Total reviews: {data.get('total', 0)}")
            print(f"   Average rating: {data.get('average_rating', 0):.1f}⭐")
            print(f"   Returned: {len(data.get('reviews', []))}")
            return True
        else:
            print(f"❌ Reviews failed: {res.status_code} - {res.text}")
            return False
    
    def test_profile_update(self):
        """Test PATCH /api/v1x/mentor-portal/profile"""
        print("\n✏️  Testing Profile Update Endpoint...")
        
        update_data = {
            "bio": "Updated bio - test at " + datetime.now().isoformat(),
            "expertise": ["Python", "FastAPI", "Testing"],
            "hourly_rate": 75
        }
        
        res = self.session.patch(
            f"{API_BASE}/api/v1x/mentor-portal/profile",
            json=update_data
        )
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Profile update successful")
            print(f"   Updated bio: {data.get('bio', '')[:50]}...")
            print(f"   Expertise: {data.get('expertise', [])}")
            print(f"   Hourly rate: ${data.get('hourly_rate', 0)}")
            return True
        else:
            print(f"❌ Profile update failed: {res.status_code} - {res.text}")
            return False
    
    def run_all_tests(self):
        """Run all mentor portal tests"""
        print("="*60)
        print("🚀 MENTOR PORTAL API TEST SUITE")
        print("="*60)
        
        if not self.login():
            print("\n❌ Cannot proceed without login. Please check credentials.")
            return
        
        results = {
            "Overview": self.test_overview(),
            "Sessions": self.test_sessions(),
            "Earnings": self.test_earnings(),
            "Students": self.test_students(),
            "Analytics": self.test_analytics(),
            "Reviews": self.test_reviews(),
            "Profile Update": self.test_profile_update()
        }
        
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test}")
        
        print(f"\n🎯 Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All tests passed!")
        else:
            print(f"⚠️  {total - passed} test(s) failed")
        
        print("="*60)

if __name__ == "__main__":
    print("\n⚙️  Configuration:")
    print(f"   API Base: {API_BASE}")
    print(f"   Test User: {TEST_USER_EMAIL}")
    print(f"\n💡 Make sure:")
    print(f"   1. Backend is running on {API_BASE}")
    print(f"   2. Test user exists and is an approved mentor")
    print(f"   3. Update TEST_USER_EMAIL and TEST_PASSWORD above")
    
    input("\nPress Enter to start tests...")
    
    tester = MentorPortalTester()
    tester.run_all_tests()

