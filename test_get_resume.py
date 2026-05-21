import requests
BASE = 'http://localhost:8001'
# Login
r = requests.post(f'{BASE}/api/v1/auth/login', json={'email': 'test_1767164081@test.com', 'password': 'TestPassword123!'})
c = r.cookies
# Get a resume
r = requests.get(f'{BASE}/api/v1x/session/resumes/4', cookies=c)
print('GET /session/resumes/4:', r.status_code)
if r.status_code == 200:
    resume = r.json()
    print('  Title:', resume.get('title'))
    print('  Version:', resume.get('version'))
    print('  Views:', resume.get('views'))
else:
    print('  Error:', r.text[:100])
