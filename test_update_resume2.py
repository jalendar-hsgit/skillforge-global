import requests
BASE = 'http://localhost:8001'
# Login
r = requests.post(f'{BASE}/api/v1/auth/login', json={'email': 'test_1767164081@test.com', 'password': 'TestPassword123!'})
c = r.cookies
# Update resume with 'summary' field
r = requests.patch(f'{BASE}/api/v1x/session/resumes?id=4', json={'summary': 'Updated summary field!'}, cookies=c)
print('PATCH /session/resumes?id=4:', r.status_code)
if r.status_code == 200:
    resume = r.json()
    print('  Title:', resume.get('title'))
    print('  Summary:', resume.get('summary'))
    print('  Professional Summary:', resume.get('professional_summary'))
    print('  Version:', resume.get('version'))
else:
    print('  Error:', r.text[:100])
