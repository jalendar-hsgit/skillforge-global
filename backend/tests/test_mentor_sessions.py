"""
Automated Tests for Mentor Sessions API
Revenue Feature: $150K/mo
"""

import pytest
import requests
import json
from datetime import datetime, timedelta
import os

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
ADMIN_EMAIL = "admin@skillforge.com"
ADMIN_PASSWORD = "admin123"
MENTOR_EMAIL = "sarah.chen@example.com"
MENTOR_PASSWORD = "mentor123"
STUDENT_EMAIL = "john.doe@example.com"
STUDENT_PASSWORD = "student123"

class TestMentorSessions:
    """Test suite for mentor sessions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data and auth tokens"""
        self.student_token = self._get_token(STUDENT_EMAIL, STUDENT_PASSWORD)
        self.mentor_token = self._get_token(MENTOR_EMAIL, MENTOR_PASSWORD)
        self.admin_token = self._get_token(ADMIN_EMAIL, ADMIN_PASSWORD)
        
    def _get_token(self, email: str, password: str) -> str:
        """Login and get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/v1x/auth/login",
            json={"email": email, "password": password}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    def test_01_list_mentors(self):
        """Test: GET /mentors - List all mentors"""
        response = requests.get(f"{BASE_URL}/api/v1x/mentors")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "mentors" in data, "Response should have 'mentors' key"
        assert len(data["mentors"]) >= 4, "Should have at least 4 mentors from demo data"
        
        mentor = data["mentors"][0]
        assert "id" in mentor, "Mentor should have 'id'"
        assert "name" in mentor, "Mentor should have 'name'"
        assert "hourly_rate" in mentor, "Mentor should have 'hourly_rate'"
        assert "average_rating" in mentor, "Mentor should have 'average_rating'"
        assert isinstance(mentor["hourly_rate"], (int, float)), "Rate should be number"
        
        print(f"✅ Listed {len(data['mentors'])} mentors")
        return True
    
    def test_02_get_mentor_detail(self):
        """Test: GET /mentors/{id} - Mentor detail"""
        response = requests.get(f"{BASE_URL}/api/v1x/mentors/1")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["id"] == 1, "Should return mentor ID 1"
        assert "user" in data, "Should have user info"
        assert "availability" in data, "Should have availability slots"
        assert len(data["availability"]) > 0, "Should have availability slots"
        
        slot = data["availability"][0]
        assert "day_of_week" in slot, "Slot should have day_of_week"
        assert "start_time" in slot, "Slot should have start_time"
        assert "end_time" in slot, "Slot should have end_time"
        
        print(f"✅ Retrieved mentor detail: {data['user']['name']}")
        return True
    
    def test_03_get_mentor_availability(self):
        """Test: GET /mentors/{id}/availability - Availability slots"""
        response = requests.get(f"{BASE_URL}/api/v1x/mentors/1/availability")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "mentor_id" in data, "Should have mentor_id"
        assert "slots" in data, "Should have slots"
        assert len(data["slots"]) > 0, "Should have availability slots"
        
        slot = data["slots"][0]
        assert "day_of_week" in slot, "Slot should have day_of_week"
        assert 0 <= slot["day_of_week"] <= 6, "Day should be 0-6"
        assert "is_available" in slot, "Slot should have is_available"
        
        print(f"✅ Retrieved {len(data['slots'])} availability slots")
        return True
    
    def test_04_create_mentor_session(self):
        """Test: POST /mentors/sessions - Book session"""
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        
        session_data = {
            "mentor_id": 1,
            "topic": "Python OOP Fundamentals",
            "description": "Need help with classes and inheritance",
            "scheduled_at": future_date,
            "duration_minutes": 60
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["mentor_id"] == 1, "Should book with mentor ID 1"
        assert data["topic"] == "Python OOP Fundamentals", "Topic should match"
        assert data["status"] == "PENDING", "New session should be PENDING"
        assert data["payment_status"] == "PENDING", "Payment should be PENDING"
        assert data["price"] > 0, "Price should be calculated"
        
        self.session_id = data["id"]
        print(f"✅ Created session ID {self.session_id}: ${data['price']}")
        return True
    
    def test_05_get_my_sessions(self):
        """Test: GET /mentors/sessions/my - My sessions"""
        response = requests.get(
            f"{BASE_URL}/api/v1x/mentors/sessions/my",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "upcoming" in data, "Should have upcoming sessions"
        assert "past" in data, "Should have past sessions"
        
        # At least one session from previous test
        assert len(data["upcoming"]) > 0, "Should have at least one upcoming session"
        
        session = data["upcoming"][0]
        assert "mentor" in session, "Should have mentor info"
        assert "topic" in session, "Should have topic"
        assert "scheduled_at" in session, "Should have scheduled_at"
        
        print(f"✅ Retrieved {len(data['upcoming'])} upcoming sessions")
        return True
    
    def test_06_create_payment_intent(self):
        """Test: POST /payments/create-payment-intent - Create payment"""
        # Create a session first
        future_date = (datetime.utcnow() + timedelta(days=8)).isoformat() + "Z"
        
        session_data = {
            "mentor_id": 1,
            "topic": "Advanced Python",
            "scheduled_at": future_date,
            "duration_minutes": 60
        }
        
        session_response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]
        
        # Create payment intent
        response = requests.post(
            f"{BASE_URL}/api/v1x/payments/create-payment-intent",
            json={"session_id": session_id},
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "payment_intent_id" in data, "Should return payment_intent_id"
        assert "client_secret" in data, "Should return client_secret"
        assert data["payment_intent_id"].startswith("pi_"), "PI ID should start with pi_"
        assert "amount" in data, "Should have amount in cents"
        assert data["currency"] == "usd", "Currency should be USD"
        
        print(f"✅ Created payment intent: {data['payment_intent_id']}")
        return True
    
    def test_07_mentor_payout_summary(self):
        """Test: GET /mentors/payouts/summary - Earnings summary"""
        response = requests.get(
            f"{BASE_URL}/api/v1x/mentors/payouts/summary",
            headers={"Authorization": f"Bearer {self.mentor_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "total_earned" in data, "Should have total_earned"
        assert "available_balance" in data, "Should have available_balance"
        assert "pending_requests" in data, "Should have pending_requests"
        assert "completed_payouts" in data, "Should have completed_payouts"
        
        assert isinstance(data["total_earned"], (int, float)), "Should be number"
        assert data["available_balance"] <= data["total_earned"], "Balance <= total"
        
        print(f"✅ Mentor earnings: Total ${data['total_earned']}, Available ${data['available_balance']}")
        return True
    
    def test_08_request_payout(self):
        """Test: POST /mentors/payouts/payout-request - Request payout"""
        # First add payment method
        payment_method = {
            "payment_type": "BANK",
            "account_holder_name": "Sarah Chen",
            "bank_name": "Chase",
            "account_number": "123456789012",
            "routing_number": "987654321"
        }
        
        pm_response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/payouts/payment-methods",
            json=payment_method,
            headers={"Authorization": f"Bearer {self.mentor_token}"}
        )
        
        if pm_response.status_code in [200, 201]:
            payment_method_id = pm_response.json().get("id", 1)
        else:
            payment_method_id = 1  # Use existing
        
        # Request payout
        payout_data = {
            "amount": 100.00,
            "payment_method_id": payment_method_id,
            "notes": "Monthly withdrawal"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/payouts/payout-request",
            json=payout_data,
            headers={"Authorization": f"Bearer {self.mentor_token}"}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["amount"] == 100.00, "Amount should match"
        assert data["status"] == "PENDING", "Status should be PENDING"
        assert "id" in data, "Should return payout ID"
        
        print(f"✅ Requested payout: ${data['amount']} (ID: {data['id']})")
        return True


class TestMentorSessionsAuthentication:
    """Test authentication and authorization"""
    
    def test_unauthorized_access(self):
        """Test: Cannot access without token"""
        response = requests.get(f"{BASE_URL}/api/v1x/mentors/sessions/my")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✅ Protected endpoint correctly requires auth")
        return True
    
    def test_invalid_token(self):
        """Test: Invalid token rejected"""
        response = requests.get(
            f"{BASE_URL}/api/v1x/mentors/sessions/my",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✅ Invalid token correctly rejected")
        return True


class TestMentorSessionsValidation:
    """Test input validation"""
    
    @pytest.fixture
    def student_token(self):
        """Get student token"""
        response = requests.post(
            f"{BASE_URL}/api/v1x/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_missing_required_field(self, student_token):
        """Test: Missing required field validation"""
        session_data = {
            "mentor_id": 1
            # Missing: topic, scheduled_at, duration_minutes
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print(f"✅ Validation error for missing fields")
        return True
    
    def test_invalid_date(self, student_token):
        """Test: Past date validation"""
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        
        session_data = {
            "mentor_id": 1,
            "topic": "Python",
            "scheduled_at": past_date,
            "duration_minutes": 60
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1x/mentors/sessions",
            json=session_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"✅ Past date validation working")
        return True


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("MENTOR SESSIONS TEST SUITE")
    print("="*60 + "\n")
    
    test_suite = TestMentorSessions()
    test_suite.setup()
    
    results = []
    
    # Run all tests
    tests = [
        ("List Mentors", test_suite.test_01_list_mentors),
        ("Mentor Detail", test_suite.test_02_get_mentor_detail),
        ("Mentor Availability", test_suite.test_03_get_mentor_availability),
        ("Create Session", test_suite.test_04_create_mentor_session),
        ("Get My Sessions", test_suite.test_05_get_my_sessions),
        ("Create Payment Intent", test_suite.test_06_create_payment_intent),
        ("Payout Summary", test_suite.test_07_mentor_payout_summary),
        ("Request Payout", test_suite.test_08_request_payout),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS", None))
        except AssertionError as e:
            results.append((test_name, "FAIL", str(e)))
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
    
    # Auth tests
    auth_tests = TestMentorSessionsAuthentication()
    auth_test_list = [
        ("Unauthorized Access", auth_tests.test_unauthorized_access),
        ("Invalid Token", auth_tests.test_invalid_token),
    ]
    
    for test_name, test_func in auth_test_list:
        try:
            result = test_func()
            results.append((test_name, "PASS", None))
        except AssertionError as e:
            results.append((test_name, "FAIL", str(e)))
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
    
    # Print results
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    
    for test_name, status, error in results:
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(results)} | Passed: {passed} ✅ | Failed: {failed} ❌ | Errors: {errors} ⚠️")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    run_all_tests()
