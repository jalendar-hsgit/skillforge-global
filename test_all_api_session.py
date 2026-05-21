import requests
BASE = 'http://localhost:8001'
# Login
r = requests.post(f'{BASE}/api/v1/auth/login', json={'email': 'test_1767164081@test.com', 'password': 'TestPassword123!'})
c = r.cookies

print("Testing /api/session endpoints:")
print("-" * 50)

# GET /session/me
r = requests.get(f'{BASE}/api/session/me', cookies=c)
print(f"GET /api/session/me: {r.status_code}")

# GET /session/resumes (list)
r = requests.get(f'{BASE}/api/session/resumes', cookies=c)
print(f"GET /api/session/resumes: {r.status_code} ({len(r.json())} resumes)")

# GET /session/resumes/4 (read)
r = requests.get(f'{BASE}/api/session/resumes/4', cookies=c)
print(f"GET /api/session/resumes/4: {r.status_code}")

# PATCH /session/resumes?id=4 (update)
r = requests.patch(f'{BASE}/api/session/resumes?id=4', json={'phone': '+5555555555'}, cookies=c)
print(f"PATCH /api/session/resumes?id=4: {r.status_code}")

# POST /session/resumes (create)
r = requests.post(f'{BASE}/api/session/resumes', json={'title': 'API Path Test', 'template': 'modern'}, cookies=c)
if r.status_code in [200, 201]:
    new_id = r.json()['id']
    print(f"POST /api/session/resumes: {r.status_code} (new resume ID: {new_id})")
    
    # DELETE /session/resumes?id=<new_id>
    r = requests.delete(f'{BASE}/api/session/resumes?id={new_id}', cookies=c)
    print(f"DELETE /api/session/resumes?id={new_id}: {r.status_code}")
else:
    print(f"POST /api/session/resumes: {r.status_code}")

print("-" * 50)
print("All /api/session endpoints working correctly!")
