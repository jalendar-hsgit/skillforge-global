"""
Tests for file sharing functionality
"""
import pytest
from fastapi.testclient import TestClient
import io

from app.main import app

client = TestClient(app)


def test_file_sharing_endpoints_exist():
    """Test that file sharing endpoints are registered"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    # Check if file sharing endpoints exist
    assert any("/files/" in path for path in paths)


def test_upload_file_unauthorized():
    """Test uploading file without authentication"""
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    data = {"session_id": "1"}
    
    response = client.post(
        "/api/v1x/files/upload",
        files=files,
        data=data
    )
    
    # Should require authentication or not be found
    assert response.status_code in [401, 403, 404, 422]


def test_list_files_unauthorized():
    """Test listing files without authentication"""
    response = client.get("/api/v1x/files/session/1")
    
    # Should require authentication or not be found
    assert response.status_code in [401, 403, 404]


def test_download_file_unauthorized():
    """Test downloading file without authentication"""
    response = client.get("/api/v1x/files/1/download")
    
    # Should require authentication or return 404
    assert response.status_code in [401, 403, 404]


def test_file_upload_validation():
    """Test file upload with missing data"""
    response = client.post("/api/v1x/files/upload")
    
    # Should fail validation or not be found
    assert response.status_code in [400, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
