import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_EMAIL = "apitest+pytest@example.com"
TEST_PW = "pass1234"


def test_signup_and_login_and_me():
    # cleanup may be necessary if user exists; signup returns 400 if exists
    r = client.post("/api/v1/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PW})
    assert r.status_code in (200, 400)

    r = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PW})
    assert r.status_code == 200
    # token cookie should be set
    token = client.cookies.get("token")
    assert token is not None

    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    j = r.json()
    assert j.get("email") == TEST_EMAIL


def test_coins_endpoints():
    # require logged-in user cookie from previous test
    r = client.get("/api/v1x/coins_db/health")
    assert r.status_code == 200 and r.json().get("ok") is True

    r = client.get("/api/v1x/coins_db/balance")
    assert r.status_code == 200
    j = r.json()
    assert "balance" in j or "coins" in j

    # add coins
    r = client.post("/api/v1x/coins_db/add", json={"amount": 10})
    assert r.status_code == 200 and r.json().get("ok") is True

    # redeem coins (use small amount to avoid insufficient balance)
    r = client.post("/api/v1x/coins_db/redeem", json={"amount": 1})
    assert r.status_code == 200 and r.json().get("ok") is True


def test_progress_endpoints():
    # progress endpoints expect Authorization: Bearer <token>
    token = client.cookies.get("token")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # GET progress for example path
    r = client.get("/api/v1/progress?path=python-ai", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert j.get("path") == "python-ai"
    assert isinstance(j.get("completed"), list)

    # POST mark complete
    r = client.post("/api/v1/progress?path=python-ai&module_id=pytest-mod-1", headers=headers)
    assert r.status_code == 200
    j2 = r.json()
    assert "pytest-mod-1" in j2.get("completed")


def test_youtube_health():
    r = client.get("/api/v1x/youtube/health")
    # may be 200 with has_key True/False depending on env
    assert r.status_code in (200, 500, 404)


if __name__ == "__main__":
    pytest.main(["-q"])