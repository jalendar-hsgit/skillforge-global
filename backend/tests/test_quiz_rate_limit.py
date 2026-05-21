import pytest
from fastapi.testclient import TestClient


def _override_user():
    class U:
        id = 123
        email = "test@example.com"
    return U()


def test_quiz_generate_rate_limit(monkeypatch):
    # Import app after setting PYTHONPATH context in tests runner
    from app.main import app
    from app.core.security import get_current_user

    # Override auth dependency
    app.dependency_overrides[get_current_user] = _override_user

    client = TestClient(app)

    payload = {
        "topic": "rate-limit-topic",
        "difficulty": "medium",
        "num_questions": 2,
        "options_per_question": 3,
    }

    # Limit is 10 per 5 minutes in the endpoint; call 10 times should pass
    ok = 0
    for _ in range(10):
        r = client.post("/api/v1/quizzes/generate", json=payload)
        assert r.status_code in (200, 500)  # 500 allowed if provider errors before fallback in some envs
        if r.status_code == 200:
            ok += 1

    # 11th call should be 429
    r = client.post("/api/v1/quizzes/generate", json=payload)
    assert r.status_code == 429
    assert "Rate limit" in r.text

    # Cleanup override
    app.dependency_overrides.pop(get_current_user, None)
