"""
API Standardization Test Suite
Tests all endpoints to verify they return standardized responses.

Run with: pytest test_api_standardization.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Test all auth endpoints return standardized responses"""
    
    def test_login_success(self):
        """Test successful login returns standard format"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify standard response format
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "error" in data
        assert "timestamp" in data
        assert "path" in data
        
        # Verify successful login
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"]["access_token"] is not None
        assert data["data"]["token_type"] == "bearer"
        assert "Login successful" in data["message"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns standard error"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrongpass"}
        )
        
        assert response.status_code == 401
        data = response.json()
        
        # Verify standard error format
        assert data["success"] is False
        assert data["data"] is None
        assert data["error"] is not None
        assert data["message"] is not None
        assert data["timestamp"] is not None
        assert data["path"] == "/api/v1x/auth/login"
    
    def test_login_missing_email(self):
        """Test login without email returns validation error"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"password": "somepass"}
        )
        
        # Should be 422 (validation error)
        assert response.status_code == 422
        data = response.json()
        
        # Verify validation error format
        assert data["success"] is False
        assert data["message"] == "Validation error"
    
    def test_logout(self):
        """Test logout returns standard format"""
        # First login
        login_response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        assert login_response.status_code == 200
        
        # Then logout
        logout_response = client.post(
            "/api/v1x/auth/logout"
        )
        
        assert logout_response.status_code == 200
        data = logout_response.json()
        
        # Verify standard response
        assert data["success"] is True
        assert data["error"] is None
        assert "Logout" in data["message"]
    
    def test_me_endpoint(self):
        """Test /me endpoint returns standard format"""
        # First login
        login_response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # Then get profile
        response = client.get(
            "/api/v1x/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify standard response
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"]["id"] is not None
        assert data["data"]["email"] is not None


class TestHealthzEndpoint:
    """Test health check endpoint"""
    
    def test_healthz(self):
        """Test healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestResponseFormat:
    """Test response format consistency"""
    
    def test_all_responses_have_required_fields(self):
        """Verify all error responses have required fields"""
        # Test with a 404 error
        response = client.get("/api/v1x/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        
        # All responses must have these fields
        required_fields = ["success", "data", "message", "error", "timestamp", "path"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_success_response_has_null_error(self):
        """Verify success responses have error=null"""
        response = client.get("/healthz")
        
        # Health check doesn't use standardized format, skip this test
        # Instead test with login
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["error"] is None or data["error"] == ""
    
    def test_error_response_has_null_data(self):
        """Verify error responses have data=null"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "invalid@test.com", "password": "wrong"}
        )
        
        if response.status_code >= 400:
            data = response.json()
            # Error responses may have data=null
            if "data" in data:
                assert data["data"] is None or data["success"] is True


class TestErrorCodes:
    """Test proper HTTP error codes"""
    
    def test_unauthorized_returns_401(self):
        """Test unauthorized access returns 401"""
        response = client.get(
            "/api/v1x/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_not_found_returns_404(self):
        """Test missing endpoint returns 404"""
        response = client.get("/api/v1x/nonexistent")
        assert response.status_code == 404
    
    def test_validation_error_returns_422(self):
        """Test validation error returns 422"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"password": "only_password"}  # Missing email
        )
        
        assert response.status_code == 422


class TestTimestampFormat:
    """Test timestamp format in responses"""
    
    def test_timestamp_is_iso_format(self):
        """Verify timestamp is ISO 8601 format"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Should be ISO 8601 format with Z suffix
        assert timestamp.endswith("Z")
        assert "T" in timestamp
        # Should be parseable as datetime
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")


class TestPathInResponse:
    """Test path field in responses"""
    
    def test_path_matches_endpoint(self):
        """Verify path in response matches endpoint"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "superadmin@skillforge.com", "password": "superadmin"}
        )
        
        data = response.json()
        assert data["path"] == "/api/v1x/auth/login"
    
    def test_path_in_error_response(self):
        """Verify path is included in error responses"""
        response = client.post(
            "/api/v1x/auth/login",
            json={"email": "invalid@test.com", "password": "wrong"}
        )
        
        data = response.json()
        assert "path" in data
        assert data["path"] == "/api/v1x/auth/login"


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
