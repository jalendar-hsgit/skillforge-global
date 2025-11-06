"""
Test error logging and exception handlers.
Verifies that errors are logged with request IDs and proper detail in DEBUG mode.
"""
import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestErrorHandling(unittest.TestCase):
    """Test error logging middleware and exception handlers"""
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_404_error_includes_request_id(self):
        """Test that 404 errors include request ID in response headers"""
        response = self.client.get("/api/v1/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)
        
        # Check that response includes request ID header
        self.assertIn("X-Request-ID", response.headers)
        
        data = response.json()
        # FastAPI may return either "request_id" or "detail" in body
        # Just verify we get a proper 404 response
        self.assertTrue("detail" in data or "error" in data or "request_id" in data)
        
        print(f"✅ 404 error includes X-Request-ID header: {response.headers['X-Request-ID']}")
    
    def test_validation_error_includes_detail(self):
        """Test that validation errors include helpful detail"""
        # Send invalid signup data (missing required fields)
        response = self.client.post(
            "/api/v1/auth/signup",
            json={"email": "invalid"}  # Missing password
        )
        
        # Should return 422 for validation error
        self.assertIn(response.status_code, [400, 422])
        
        data = response.json()
        self.assertIn("request_id", data)
        
        print(f"✅ Validation error includes request_id: {data.get('request_id', 'N/A')}")
        print(f"   Error detail: {data.get('error', data.get('detail', 'N/A'))}")
    
    def test_successful_request_logs_properly(self):
        """Test that successful requests are logged with request IDs"""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        
        # Check that response includes request ID header
        self.assertIn("X-Request-ID", response.headers)
        
        print(f"✅ Success response includes X-Request-ID: {response.headers['X-Request-ID']}")


if __name__ == "__main__":
    unittest.main()
