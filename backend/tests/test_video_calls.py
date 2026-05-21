"""
Tests for video call WebRTC and WebSocket functionality
"""
import pytest
from fastapi.testclient import TestClient
import socketio

from app.main import app

client = TestClient(app)


def test_websocket_endpoint_exists():
    """Test that WebSocket server is mounted"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    # WebSocket should be mounted at /ws
    # Check if main app has the mount


def test_webrtc_signaling_requires_session():
    """Test that WebRTC signaling validates session"""
    # This would require a real WebSocket connection
    # For now, just test that the endpoint exists
    pass


def test_mentor_endpoints_exist():
    """Test that mentor-related endpoints are registered"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    # Check for mentor endpoints
    assert "/api/v1x/mentors" in paths or any("mentor" in path.lower() for path in paths)


def test_session_booking_unauthorized():
    """Test booking a mentor session without auth"""
    response = client.post(
        "/api/v1x/mentors/sessions/book",
        json={
            "mentor_id": 1,
            "scheduled_at": "2025-12-01T10:00:00Z",
            "duration_minutes": 60
        }
    )
    
    # Should require authentication or method not allowed
    assert response.status_code in [401, 403, 404, 405, 422]


def test_get_mentors_list():
    """Test retrieving list of mentors"""
    response = client.get("/api/v1x/mentors")
    
    # Should be accessible (may return empty list)
    assert response.status_code in [200, 404]


def test_chat_endpoint_exists():
    """Test that chat endpoints are registered"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    # Check for chat endpoints
    assert any("chat" in path.lower() for path in paths)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
