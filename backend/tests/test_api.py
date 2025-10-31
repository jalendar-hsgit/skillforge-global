import uuid
from app.main import app
from app.core.config import settings
from fastapi.testclient import TestClient


def test_healthz():
    client = TestClient(app)
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_list_courses():
    client = TestClient(app)
    r = client.get('/api/v1/courses')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_auth_and_add_course():
    # use a unique email to avoid collisions with existing test data
    email = f"test+{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123!"

    # set admin key for protected v1 routes
    settings.ADMIN_KEY = 'test-admin-key'

    client = TestClient(app)

    # signup
    r = client.post('/api/v1/auth/signup', json={'email': email, 'password': password})
    assert r.status_code in (200, 201, 400)

    # login
    r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200

    # me
    r = client.get('/api/v1/auth/me')
    assert r.status_code == 200
    j = r.json()
    assert 'email' in j and j['email'] == email

    # add a course (protected)
    course = {
        'id': f'apitest-{uuid.uuid4().hex[:8]}',
        'path': 'python-ai',
        'title': 'API Test Course',
        'youtubeId': 'TESTID',
    }
    r = client.post('/api/v1/courses', json=course, headers={'X-Admin-Key': settings.ADMIN_KEY})
    assert r.status_code == 200
    cj = r.json()
    assert cj.get('id') == course['id']
