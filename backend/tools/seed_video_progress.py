"""
Seed Video Progress Data
Creates realistic video progress for existing users to populate dashboards
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.db import SessionLocal
from sqlalchemy import text
import random
from datetime import datetime, timedelta

db = SessionLocal()

print("=" * 80)
print("SEEDING VIDEO PROGRESS DATA")
print("=" * 80)

try:
    # Get users (skip test users)
    print("\n[1] Finding real users...")
    users = db.execute(text("""
        SELECT id, email FROM users 
        WHERE email NOT LIKE '%test%' 
        AND email NOT LIKE '%admin%'
        ORDER BY id 
        LIMIT 50
    """)).fetchall()
    
    print(f"✅ Found {len(users)} users to seed progress for")
    
    # Get all videos
    print("\n[2] Finding available videos...")
    videos = db.execute(text("""
        SELECT id, title, duration FROM videos
        ORDER BY id
    """)).fetchall()
    
    print(f"✅ Found {len(videos)} videos")
    
    if len(videos) == 0:
        print("❌ No videos found - cannot seed progress")
        sys.exit(1)
    
    # Seed progress for each user
    print(f"\n[3] Creating progress records...")
    total_created = 0
    
    for user in users:
        user_id = user[0]
        user_email = user[1]
        
        # Each user watches 3-15 random videos
        num_videos_to_watch = random.randint(3, min(15, len(videos)))
        watched_videos = random.sample(list(videos), num_videos_to_watch)
        
        for video in watched_videos:
            video_id = video[0]
            
            # Check if progress already exists
            existing = db.execute(text("""
                SELECT id FROM video_progress 
                WHERE user_id = :uid AND video_id = :vid
            """), {"uid": user_id, "vid": video_id}).fetchone()
            
            if existing:
                continue  # Skip if already exists
            
            # Random progress distribution:
            # 30% - Complete (100%)
            # 40% - In progress (25-95%)
            # 30% - Just started (5-24%)
            rand = random.random()
            if rand < 0.3:
                progress = 100
            elif rand < 0.7:
                progress = random.randint(25, 95)
            else:
                progress = random.randint(5, 24)
            
            # Random last position (0 to duration)
            duration = video[2]
            if isinstance(duration, str):
                try:
                    duration = int(duration)
                except (ValueError, TypeError):
                    duration = 300  # Default 5 minutes
            elif not duration:
                duration = 300
            
            last_position = int(duration * (progress / 100.0))
            
            # Random timestamps in last 30 days
            days_ago = random.randint(1, 30)
            created = datetime.now() - timedelta(days=days_ago)
            
            # Updated time is 0-5 days after created
            updated_days = random.randint(0, min(5, days_ago))
            updated = created + timedelta(days=updated_days)
            
            # Insert progress
            db.execute(text("""
                INSERT INTO video_progress 
                (user_id, video_id, progress_percent, last_position_sec, created_at, updated_at)
                VALUES (:uid, :vid, :prog, :pos, :created, :updated)
            """), {
                "uid": user_id,
                "vid": video_id,
                "prog": progress,
                "pos": last_position,
                "created": created,
                "updated": updated
            })
            
            total_created += 1
        
        # Commit every user to avoid losing data on error
        db.commit()
        print(f"   ✅ User {user_id} ({user_email}): {num_videos_to_watch} videos")
    
    print(f"\n✅ Created {total_created} progress records")
    
    # Show statistics
    print("\n[4] Progress Statistics:")
    
    stats = db.execute(text("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT user_id) as users_with_progress,
            COUNT(DISTINCT video_id) as videos_watched,
            AVG(progress_percent) as avg_progress,
            COUNT(CASE WHEN progress_percent = 100 THEN 1 END) as completed_videos,
            COUNT(CASE WHEN progress_percent >= 25 AND progress_percent < 100 THEN 1 END) as in_progress,
            COUNT(CASE WHEN progress_percent < 25 THEN 1 END) as just_started
        FROM video_progress
    """)).fetchone()
    
    print(f"   Total Records: {stats[0]}")
    print(f"   Users with Progress: {stats[1]}")
    print(f"   Videos Watched: {stats[2]}")
    print(f"   Average Progress: {stats[3]:.1f}%")
    print(f"   Completed Videos: {stats[4]}")
    print(f"   In Progress: {stats[5]}")
    print(f"   Just Started: {stats[6]}")
    
    print("\n" + "=" * 80)
    print("✅ VIDEO PROGRESS DATA SEEDED SUCCESSFULLY")
    print("=" * 80)
    print("\n🎯 Next Steps:")
    print("   1. Check student dashboards - should show progress now")
    print("   2. Test /api/v1/dashboard/stats endpoint")
    print("   3. Verify achievements unlock based on video counts")

except Exception as e:
    print(f"\n❌ Error seeding data: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()
