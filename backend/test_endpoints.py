import requests
import json
from urllib.parse import urlencode


def get_cookies(path="cookies.txt"):
    try:
        with open(path) as f:
            return dict(line.strip().split("=", 1) for line in f if "=" in line)
    except Exception:
        return {}


def get_token_from_cookies(path="cookies.txt"):
    c = get_cookies(path)
    return c.get("token")


def test_endpoint(url, method='GET', data=None, headers=None, cookies_path="cookies.txt"):
    try:
        cookies = get_cookies(cookies_path)
        headers = headers or {}
        if method == 'GET':
            r = requests.get(url, cookies=cookies, headers=headers)
        else:
            r = requests.post(url, json=data, cookies=cookies, headers=headers)
        print(f"\n{method} {url}")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        return r
    except Exception as e:
        print(f"Error: {e}")
        return None


BASE_V1 = "http://127.0.0.1:8001/api/v1"
BASE_V1X = "http://127.0.0.1:8001/api/v1x"


print("=== AUTH / ME (cookie) ===")
test_endpoint(f"{BASE_V1}/auth/me")

print("=== COURSES LIST ===")
test_endpoint(f"{BASE_V1}/courses")

print("=== COINS (v1x) ===")
test_endpoint(f"{BASE_V1X}/coins_db/health")
test_endpoint(f"{BASE_V1X}/coins_db/balance")
test_endpoint(f"{BASE_V1X}/coins_db/add", method='POST', data={"amount": 100})
test_endpoint(f"{BASE_V1X}/coins_db/redeem", method='POST', data={"amount": 20})


# Progress endpoints (requires Bearer token)
token = get_token_from_cookies()
auth_headers = {}
if token:
    auth_headers['Authorization'] = 'Bearer ' + token

print("=== PROGRESS (requires Authorization: Bearer <token>) ===")
test_endpoint(f"{BASE_V1}/progress?path=python-ai", headers=auth_headers)
test_endpoint(f"{BASE_V1}/progress?path=python-ai&module_id=mod-unique-1", method='POST', headers=auth_headers)
# duplicate mark (should be idempotent)
test_endpoint(f"{BASE_V1}/progress?path=python-ai&module_id=mod-unique-1", method='POST', headers=auth_headers)
test_endpoint(f"{BASE_V1}/progress?path=python-ai", headers=auth_headers)


print("=== YOUTUBE (v1x) ===")
test_endpoint(f"{BASE_V1X}/youtube/health")

print("\nDone")