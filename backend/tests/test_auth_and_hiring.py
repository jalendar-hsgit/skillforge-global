import unittest
import time
from fastapi.testclient import TestClient

from app.main import app


class AuthAndHiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_auth_signup_login_me(self):
        ts = int(time.time() * 1000)
        email = f"user{ts}@example.com"
        password = "Passw0rd!"

        # Signup
        resp = self.client.post(
            "/api/v1/auth/signup",
            json={"email": email, "password": password}
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertIn("created", resp.json())

        # Login
        resp = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        self.assertEqual(resp.status_code, 200, resp.text)

        # Me
        resp = self.client.get("/api/v1/auth/me")
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        self.assertEqual(data.get("email"), email)

    def test_hiring_router_exposed_in_openapi(self):
        resp = self.client.get("/openapi.json")
        self.assertEqual(resp.status_code, 200, resp.text)
        spec = resp.json()
        paths = spec.get("paths", {})
        # Look for any hiring endpoint as a presence check
        hiring_paths = [p for p in paths.keys() if p.startswith("/api/v1x/hiring/")]
        self.assertTrue(
            any("/api/v1x/hiring/jobs/" in p for p in hiring_paths),
            msg=f"Hiring endpoints not found in OpenAPI spec. Paths seen: {list(paths.keys())[:20]}"
        )


if __name__ == "__main__":
    unittest.main()
