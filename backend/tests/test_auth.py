def test_auth_flow(client):
    email = "user1@example.com"
    password = "secret123"
    # signup
    r = client.post('/api/v1/auth/signup', json={'email': email, 'password': password})
    assert r.status_code in (200, 400)  # already exists ok in repeat runs
    # login
    r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    # me
    r = client.get('/api/v1/auth/me')
    assert r.status_code == 200
    body = r.json()
    assert body.get('email') == email
    # logout
    r = client.post('/api/v1/auth/logout')
    assert r.status_code == 200
import pytest
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup_success(self, client):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        assert data["created"] is True
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test signup with existing email fails"""
        response = client.post("/api/v1/auth/signup", json={
            "email": test_user["email"],
            "password": "AnotherPass123!"
        })
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "notanemail",
            "password": "Pass123!"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_signup_weak_password(self, client):
        """Test signup with weak password"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "weak@example.com",
            "password": "123"
        })
        
        assert response.status_code in [400, 422]
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        assert response.status_code == 200
        assert "token" in response.cookies
        data = response.json()
        assert "logged" in data
        assert data["logged"] is True
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "Pass123!"
        })
        
        assert response.status_code == 401
    
    def test_get_me_authenticated(self, client, test_user, auth_token):
        """Test getting current user when authenticated"""
        response = client.get("/api/v1/auth/me", cookies={"token": auth_token})
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["id"] == test_user["id"]
    
    def test_get_me_unauthenticated(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get("/api/v1/auth/me", cookies={"token": "invalid_token"})
        
        assert response.status_code == 401


class TestJWTTokens:
    """Test JWT token creation and validation"""
    
    def test_create_token(self):
        """Test JWT token creation"""
        user_id = 123
        token = create_access_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token_valid(self):
        """Test decoding valid JWT token"""
        user_id = 456
        token = create_access_token(user_id)
        decoded = decode_token(token)
        decoded_id = decoded.get("sub")
        
        assert decoded_id == str(user_id)
    
    def test_decode_token_invalid(self):
        """Test decoding invalid JWT token"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            decode_token("invalid_token_string")
    
    def test_decode_token_expired(self):
        """Test decoding expired token"""
        import jwt
        from app.core.config import settings
        from fastapi import HTTPException
        
        # Create token with past expiry
        token = jwt.encode({"sub": "123", "exp": 0}, settings.JWT_SECRET, algorithm="HS256")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException):
            decode_token(token)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "MySecretPass123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Different due to salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestAuthIntegration:
    """Integration tests for complete auth flow"""
    
    def test_complete_auth_flow(self, client):
        """Test complete authentication flow: signup -> login -> get user"""
        # 1. Signup
        email = "flowtest@example.com"
        password = "FlowTest123!"
        
        signup_response = client.post("/api/v1/auth/signup", json={
            "email": email,
            "password": password
        })
        assert signup_response.status_code == 200
        assert signup_response.json()["created"] is True
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        assert login_response.status_code == 200
        token = login_response.cookies.get("token")
        assert token is not None
        
        # 3. Get current user
        me_response = client.get("/api/v1/auth/me", cookies={"token": token})
        assert me_response.status_code == 200
        data = me_response.json()
        assert data["email"] == email
        assert "id" in data
    
    def test_token_persistence(self, client, test_user):
        """Test that token works across multiple requests"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        token = login_response.cookies.get("token")
        
        # Make multiple requests with same token
        for _ in range(3):
            response = client.get("/api/v1/auth/me", cookies={"token": token})
            assert response.status_code == 200
            assert response.json()["email"] == test_user["email"]
