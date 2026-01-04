import requests
BASE = 'http://localhost:8001'
# Login
r = requests.post(f'{BASE}/api/v1/auth/login', json={'email': 'test_1767164081@test.com', 'password': 'TestPassword123!'})
c = r.cookies
# First, create a new resume to delete
r = requests.post(f'{BASE}/api/v1x/session/resumes', json={'title': 'To Delete', 'template': 'modern'}, cookies=c)
resume_id = r.json()['id']
print(f'Created resume ID: {resume_id}')
# Delete it
r = requests.delete(f'{BASE}/api/v1x/session/resumes?id={resume_id}', cookies=c)
print(f'DELETE /session/resumes?id={resume_id}: {r.status_code}')
if r.status_code in [200, 204]:
    print('  OK: Resume deleted')
    # Try to get it (should 404)
    r = requests.get(f'{BASE}/api/v1x/session/resumes/{resume_id}', cookies=c)
    print(f'  Verification GET /session/resumes/{resume_id}: {r.status_code}')
else:
    print(f'  Error: {r.text[:100]}')
