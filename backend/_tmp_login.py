import requests
import sys

BASE = "http://127.0.0.1:8001"
email = "test@example.com"
password = "password123"

s = requests.Session()
try:
    r = s.post(f"{BASE}/api/v1/auth/signup", json={"email": email, "password": password})
    print("signup:", r.status_code, r.text)
except Exception as e:
    print("signup error:", e)

r = s.post(f"{BASE}/api/v1/auth/login", json={"email": email, "password": password})
print("login:", r.status_code, r.text)
if 'token' in s.cookies:
    tok = s.cookies.get('token')
    print("token:", tok)
    # write a simple cookies.txt the test script expects (name=value per-line)
    with open('cookies.txt', 'w') as f:
        f.write(f"token={tok}\n")
    print('wrote cookies.txt')
else:
    print('no token cookie received; headers:', r.headers)
    sys.exit(1)
