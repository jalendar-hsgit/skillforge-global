import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get_balance():
    r = client.get("/api/v1x/coins_db/balance")
    assert r.status_code == 200
    j = r.json()
    return int(j.get("coins") or j.get("balance") or 0)


def test_balance_changes_after_add_and_redeem():
    start = _get_balance()
    # add 7
    r = client.post("/api/v1x/coins_db/add", json={"amount": 7})
    assert r.status_code == 200 and r.json().get("ok") is True
    after_add = _get_balance()
    assert after_add == start + 7

    # redeem 3
    r = client.post("/api/v1x/coins_db/redeem", json={"amount": 3})
    assert r.status_code == 200 and r.json().get("ok") is True
    after_redeem = _get_balance()
    assert after_redeem == after_add - 3


def test_progress_deduplication_and_idempotency():
    # login/create test user and get token cookie via signup/login
    email = f"apitest+edge{pytest.ensuretemp('').strpath}@example.com"
    # try to create user but don't fail if exists
    client.post("/api/v1/auth/signup", json={"email": "apitest+pytest@example.com", "password": "pass1234"})
    client.post("/api/v1/auth/login", json={"email": "apitest+pytest@example.com", "password": "pass1234"})
    token = client.cookies.get("token")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # mark same module twice
    r1 = client.post("/api/v1/progress?path=python-ai&module_id=edge-mod-1", headers=headers)
    assert r1.status_code == 200
    r2 = client.post("/api/v1/progress?path=python-ai&module_id=edge-mod-1", headers=headers)
    assert r2.status_code == 200
    j = client.get("/api/v1/progress?path=python-ai", headers=headers).json()
    # ensure module appears only once
    assert j.get("completed").count("edge-mod-1") == 1
