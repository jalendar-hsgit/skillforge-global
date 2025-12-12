import sys
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
r = client.get('/api/v1x/mentors/search')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Mentors found: {len(data)}')
for m in data[:5]:
    print(f'  ID: {m["id"]}, User: {m.get("user",{}).get("full_name","?")}, Expertise: {m["expertise"]}')
