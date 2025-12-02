import requests

s = requests.Session()
s.post('http://localhost:8001/api/v1/auth/login', json={'email': 'mentor@test.com', 'password': 'password123'})

endpoints = [
    ('Overview', '/api/v1x/mentor-portal/dashboard/overview'),
    ('Sessions', '/api/v1x/mentor-portal/dashboard/sessions'),
    ('Earnings', '/api/v1x/mentor-portal/dashboard/earnings'),
    ('Students', '/api/v1x/mentor-portal/dashboard/students'),
    ('Analytics', '/api/v1x/mentor-portal/dashboard/analytics'),
    ('Reviews', '/api/v1x/mentor-portal/dashboard/reviews'),
]

print("=== MENTOR PORTAL ENDPOINTS ===")
for name, path in endpoints:
    r = s.get(f'http://localhost:8001{path}')
    print(f'{name}: {r.status_code}')
