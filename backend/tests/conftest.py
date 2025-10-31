import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.db import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    """Create a test user and return credentials"""
    email = "test@example.com"
    password = "TestPass123!"
    
    response = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": password
    })
    
    return {
        "email": email,
        "password": password,
        "id": response.json().get("id"),
        "response": response
    }

@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    return response.cookies.get("token")

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with Bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}
