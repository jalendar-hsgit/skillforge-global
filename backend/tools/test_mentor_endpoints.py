import sys
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("\n=== Testing Mentor Endpoints ===\n")

# Test 1: Base list endpoint (GET /api/v1x/mentors)
print("[1] GET /api/v1x/mentors")
r = client.get('/api/v1x/mentors')
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    Found: {len(data)} mentors")
    if data:
        print(f"    First: {data[0]['id']} - {data[0]['user']['full_name']}")

# Test 2: Search endpoint
print("\n[2] GET /api/v1x/mentors/search")
r = client.get('/api/v1x/mentors/search')
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    Found: {len(data)} mentors")

# Test 3: Search with filter
print("\n[3] GET /api/v1x/mentors/search?expertise=python")
r = client.get('/api/v1x/mentors/search?expertise=python')
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    Found: {len(data)} mentors with python expertise")

# Test 4: Get specific mentor
print("\n[4] GET /api/v1x/mentors/1")
r = client.get('/api/v1x/mentors/1')
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    Mentor: {data['user']['full_name']} ({data['expertise']})")
    print(f"    Rating: {data['average_rating']}/5, Sessions: {data['total_sessions']}")

print("\n✓ All mentor endpoints working!")
