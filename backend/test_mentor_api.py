"""
Comprehensive test suite for Mentor Portal API endpoints
Tests all 8 mentor-portal dashboard endpoints
"""
import sys
sys.path.insert(0, 'D:\\python code\\sfg\\skillforge-global\\backend')

import os
import requests
from datetime import datetime, timedelta

# Config
API_BASE = "http://localhost:8001"
TEST_USER_EMAIL = "mentor@test.com"  # Test mentor email
TEST_PASSWORD = "password123"  # Test password

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

    def test_session_actions(self):
        """Test PATCH /api/v1x/mentors/sessions/{id} to confirm/cancel/complete."""
        print("\n🛠️  Testing Session Actions (confirm/cancel/complete)...")

        # 1) Fetch sessions as mentor to find candidates
        # Try to get a pending session first
        res = self.session.get(
            f"{API_BASE}/api/v1x/mentors/sessions/my",
            params={"as_mentor": "true", "status_filter": "pending"}
        )
        if res.status_code != 200:
            print(f"❌ Unable to fetch mentor sessions: {res.status_code} - {res.text}")
            return False
        data = res.json()
        pending_list = data.get("sessions", [])

        # If none pending, fetch confirmed to later complete/cancel
        if not pending_list:
            res2 = self.session.get(
                f"{API_BASE}/api/v1x/mentors/sessions/my",
                params={"as_mentor": "true", "status_filter": "confirmed"}
            )
            if res2.status_code != 200:
                print(f"❌ Unable to fetch confirmed sessions: {res2.status_code} - {res2.text}")
                return False
            confirmed_list = res2.json().get("sessions", [])
        else:
            confirmed_list = []

        # 2) If we have a pending session, confirm it
        confirmed_session_id = None
        if pending_list:
            s = pending_list[0]
            sid = s.get("id")
            print(f"   ➜ Confirming pending session #{sid} ...")
            pr = self.session.patch(
                f"{API_BASE}/api/v1x/mentors/sessions/{sid}",
                json={"status": "confirmed"}
            )
            if pr.status_code != 200:
                print(f"❌ Confirm failed: {pr.status_code} - {pr.text}")
                return False
            payload = pr.json()
            session_data = payload.get("session", {})
            if session_data.get("status") != "confirmed":
                print(f"❌ Confirm did not persist. Status: {session_data.get('status')}")
                return False
            if not session_data.get("meeting_url"):
                print(f"⚠️  meeting_url not present after confirmation")
            confirmed_session_id = sid

        # 3) If we have a confirmed session (either from step 2 or pre-existing), complete it
        target_confirmed = None
        if confirmed_session_id is not None:
            # Fetch the session again to ensure it is confirmed
            target_confirmed = confirmed_session_id
        elif confirmed_list:
            target_confirmed = confirmed_list[0].get("id")

        if target_confirmed is not None:
            print(f"   ➜ Completing confirmed session #{target_confirmed} ...")
            cr = self.session.patch(
                f"{API_BASE}/api/v1x/mentors/sessions/{target_confirmed}",
                json={"status": "completed"}
            )
            if cr.status_code != 200:
                print(f"❌ Complete failed: {cr.status_code} - {cr.text}")
                return False
            cp = cr.json()
            session_data = cp.get("session", {})
            if session_data.get("status") != "completed":
                print(f"❌ Complete did not persist. Status: {session_data.get('status')}")
                return False

        # 4) Cancel any remaining pending/confirmed session (not the one we completed if possible)
        res3 = self.session.get(
            f"{API_BASE}/api/v1x/mentors/sessions/my",
            params={"as_mentor": "true"}
        )
        if res3.status_code == 200:
            all_list = res3.json().get("sessions", [])
            cancel_target = None
            for s in all_list:
                sid = s.get("id")
                st = s.get("status")
                if st in ("pending", "confirmed") and sid != (target_confirmed or confirmed_session_id):
                    cancel_target = sid
                    break
            if cancel_target:
                print(f"   ➜ Cancelling session #{cancel_target} ...")
                rr = self.session.patch(
                    f"{API_BASE}/api/v1x/mentors/sessions/{cancel_target}",
                    json={"status": "cancelled", "mentor_notes": "Test cancellation"}
                )
                if rr.status_code != 200:
                    print(f"❌ Cancel failed: {rr.status_code} - {rr.text}")
                    return False
                rj = rr.json()
                session_data = rj.get("session", {})
                if session_data.get("status") != "cancelled":
                    print(f"❌ Cancel did not persist. Status: {session_data.get('status')}")
                    return False
        else:
            print(f"⚠️  Could not fetch all sessions for cancel step: {res3.status_code}")

        print("✅ Session actions covered (confirm/complete/cancel)")
        return True
    
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
            "Profile Update": self.test_profile_update(),
            "Session Actions": self.test_session_actions(),
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
    
    # Allow non-interactive runs via AUTO_RUN=1 or when stdin is not a TTY
    if os.environ.get("AUTO_RUN") != "1" and sys.stdin.isatty():
        input("\nPress Enter to start tests...")
    
    tester = MentorPortalTester()
    tester.run_all_tests()

