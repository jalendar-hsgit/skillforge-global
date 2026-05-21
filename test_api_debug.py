import requests
import json

# Test the API endpoint directly
print("Testing backend API...")
try:
    response = requests.get(
        "http://localhost:8001/api/v1x/coding-practice/challenges?limit=10",
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.ok:
        challenges = response.json()
        print(f"✅ Success! Loaded {len(challenges)} challenges")
        if challenges:
            print(f"First challenge: {challenges[0]['title']}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test the database
print("\nTesting database...")
try:
    from app.core.db import SessionLocal
    from app.modelsx.coding_practice import CodingChallenge
    
    db = SessionLocal()
    count = db.query(CodingChallenge).count()
    challenges = db.query(CodingChallenge).limit(3).all()
    
    print(f"✅ Database has {count} challenges")
    for c in challenges:
        print(f"  - {c.title} ({c.difficulty})")
    
    db.close()
except Exception as e:
    print(f"❌ Database error: {e}")
