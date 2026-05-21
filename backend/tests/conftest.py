import os
import pytest
from fastapi.testclient import TestClient

# Ensure test DB before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./app/data/test_e2e.db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:3000")

from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import get_password_hash
from app.modelsx.mentor import Mentor, MentorStatus

@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def create_user(db_session):
    def _create(email: str = "test@example.com", password: str = "testpass") -> User:
        u = db_session.query(User).filter(User.email==email).first()
        if u:
            return u
        u = User(email=email, password_hash=get_password_hash(password))
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
        return u
    return _create

@pytest.fixture()
def login(client, create_user):
    def _login(email: str = "test@example.com", password: str = "testpass"):
        create_user(email, password)
        r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200
        return client
    return _login

@pytest.fixture()
def ensure_mentor(db_session, create_user):
    def _ensure(email: str = "mentor@example.com") -> Mentor:
        u = create_user(email=email)
        m = db_session.query(Mentor).filter(Mentor.user_id==u.id).first()
        if m:
            return m
        m = Mentor(user_id=u.id, bio="Experienced mentor", expertise="python,react", hourly_rate=50.0, status=MentorStatus.APPROVED)
        db_session.add(m)
        db_session.commit()
        db_session.refresh(m)
        return m
    return _ensure
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
