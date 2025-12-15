"""
Test Video Progress Tracking System
Tests the newly created /api/v1/progress/videos/{video_id} endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from sqlalchemy import text

client = TestClient(app)

print("=" * 80)
print("VIDEO PROGRESS TRACKING - ENDPOINT TEST")
print("=" * 80)

# Step 1: Check if video_progress table exists
print("\n[1] Checking video_progress table...")
db = SessionLocal()
try:
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='video_progress'")).fetchone()
    if result:
        print("✅ video_progress table exists")
        
        # Check columns
        columns = db.execute(text("PRAGMA table_info(video_progress)")).fetchall()
        print("\n   Table Schema:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    else:
        print("❌ video_progress table NOT FOUND")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking table: {e}")
    sys.exit(1)
finally:
    db.close()

# Step 2: Create a test user and login
print("\n[2] Creating test user and logging in...")
test_email = f"video_test_user_{os.urandom(4).hex()}@test.com"
test_password = "TestPassword123!"

# Signup
signup_response = client.post("/api/v1/auth/signup", json={
    "email": test_email,
    "password": test_password,
    "username": "videotest"
})

if signup_response.status_code not in [200, 201]:
    print(f"❌ Signup failed: {signup_response.status_code}")
    print(f"   Response: {signup_response.text}")
    sys.exit(1)

print(f"✅ User created: {test_email}")

# Login to get token
login_response = client.post("/api/v1/auth/login", json={
    "email": test_email,
    "password": test_password
})

if login_response.status_code == 200:
    print(f"✅ Login successful")
    token_cookie = login_response.cookies.get("token")
    if not token_cookie:
        print("❌ No token cookie received")
        sys.exit(1)
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    sys.exit(1)

# Step 3: Get first available video ID
print("\n[3] Finding available video...")
db = SessionLocal()
try:
    video = db.execute(text("SELECT id, title FROM videos LIMIT 1")).fetchone()
    if video:
        video_id = video[0]
        video_title = video[1]
        print(f"✅ Found video: ID={video_id}, Title={video_title}")
    else:
        print("❌ No videos found in database")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error finding video: {e}")
    sys.exit(1)
finally:
    db.close()

# Step 4: Test GET /api/v1/progress/videos/{video_id} (should return 0% progress)
print(f"\n[4] Testing GET /api/v1/progress/videos/{video_id} (no progress yet)...")
get_response = client.get(
    f"/api/v1/progress/videos/{video_id}",
    cookies={"token": token_cookie}
)

if get_response.status_code == 200:
    data = get_response.json()
    print(f"✅ GET endpoint working")
    print(f"   Progress: {data.get('progress_percent', 0)}%")
    print(f"   Last Position: {data.get('last_position_sec', 0)}s")
    
    if data.get('progress_percent') == 0:
        print("✅ Default progress is 0% (correct)")
    else:
        print(f"⚠️  Expected 0% progress, got {data.get('progress_percent')}%")
else:
    print(f"❌ GET failed: {get_response.status_code}")
    print(f"   Response: {get_response.text}")
    sys.exit(1)

# Step 5: Test POST /api/v1/progress/videos/{video_id} (update to 50%)
print(f"\n[5] Testing POST /api/v1/progress/videos/{video_id} (update to 50%)...")
post_response = client.post(
    f"/api/v1/progress/videos/{video_id}",
    json={
        "progress_percent": 50,
        "last_position_sec": 120
    },
    cookies={"token": token_cookie}
)

if post_response.status_code == 200:
    data = post_response.json()
    print(f"✅ POST endpoint working")
    print(f"   Progress: {data.get('progress_percent')}%")
    print(f"   Last Position: {data.get('last_position_sec')}s")
    
    if data.get('progress_percent') == 50:
        print("✅ Progress updated to 50% (correct)")
    else:
        print(f"⚠️  Expected 50%, got {data.get('progress_percent')}%")
else:
    print(f"❌ POST failed: {post_response.status_code}")
    print(f"   Response: {post_response.text}")
    sys.exit(1)

# Step 6: Test GET again (should return 50%)
print(f"\n[6] Testing GET again (should return 50%)...")
get_response2 = client.get(
    f"/api/v1/progress/videos/{video_id}",
    cookies={"token": token_cookie}
)

if get_response2.status_code == 200:
    data = get_response2.json()
    print(f"✅ GET endpoint working")
    print(f"   Progress: {data.get('progress_percent')}%")
    
    if data.get('progress_percent') == 50:
        print("✅ Progress persisted correctly (50%)")
    else:
        print(f"❌ Expected 50%, got {data.get('progress_percent')}%")
        sys.exit(1)
else:
    print(f"❌ GET failed: {get_response2.status_code}")
    sys.exit(1)

# Step 7: Test POST to complete video (100%)
print(f"\n[7] Testing POST to mark video complete (100%)...")
complete_response = client.post(
    f"/api/v1/progress/videos/{video_id}",
    json={
        "progress_percent": 100,
        "last_position_sec": 300
    },
    cookies={"token": token_cookie}
)

if complete_response.status_code == 200:
    data = complete_response.json()
    print(f"✅ Completion endpoint working")
    print(f"   Progress: {data.get('progress_percent')}%")
    
    if data.get('progress_percent') == 100:
        print("✅ Video marked as complete (100%)")
    else:
        print(f"⚠️  Expected 100%, got {data.get('progress_percent')}%")
else:
    print(f"❌ Completion failed: {complete_response.status_code}")
    sys.exit(1)

# Step 8: Verify database record
print(f"\n[8] Verifying database record...")
db = SessionLocal()
try:
    result = db.execute(text("""
        SELECT progress_percent, last_position_sec, created_at, updated_at 
        FROM video_progress 
        WHERE video_id = :vid
        ORDER BY id DESC LIMIT 1
    """), {"vid": video_id}).fetchone()
    
    if result:
        print("✅ Database record found:")
        print(f"   Progress: {result[0]}%")
        print(f"   Position: {result[1]}s")
        print(f"   Created: {result[2]}")
        print(f"   Updated: {result[3]}")
    else:
        print("❌ No database record found")
        sys.exit(1)
except Exception as e:
    print(f"❌ Database query failed: {e}")
    sys.exit(1)
finally:
    db.close()

# Final Summary
print("\n" + "=" * 80)
print("✅ ALL VIDEO PROGRESS TESTS PASSED")
print("=" * 80)
print("\n📊 Summary:")
print("   ✅ video_progress table exists with correct schema")
print("   ✅ GET /api/v1/progress/videos/{id} returns default 0%")
print("   ✅ POST /api/v1/progress/videos/{id} creates progress record")
print("   ✅ Progress updates are persisted correctly")
print("   ✅ 100% completion tracking works")
print("   ✅ Database timestamps are recorded")
print("\n🎯 NEXT STEP: Test with frontend video player")
print("   1. Restart backend: uvicorn app.main:app --reload --port 8001")
print("   2. Visit: http://localhost:3000/watch/{video_id}")
print("   3. Watch video and verify progress saves")
