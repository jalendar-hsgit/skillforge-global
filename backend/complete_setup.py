"""
Create all courses in database and sync YouTube videos
"""
import requests
import sqlite3
import os

BASE_URL = "http://127.0.0.1:8001"
DB_PATH = os.path.join(os.path.dirname(__file__), "app", "data", "skillforge.db")

# Define all courses
COURSES = [
    {"id": 1, "path": "python-ai", "title": "Python AI Mastery", "description": "Learn AI with Python"},
    {"id": 2, "path": "fullstack", "title": "Full Stack Development", "description": "Build complete web applications"},
    {"id": 3, "path": "aws-devops", "title": "AWS DevOps Professional", "description": "Master cloud and DevOps"},
    {"id": 4, "path": "cybersec", "title": "Cybersecurity Expert", "description": "Learn ethical hacking and security"},
    {"id": 5, "path": "flutter", "title": "Flutter Mobile Development", "description": "Build cross-platform mobile apps"},
]

# YouTube search queries
YOUTUBE_QUERIES = {
    "python-ai": [
        {"query": "python programming tutorial for beginners", "max": 5},
        {"query": "machine learning python tutorial", "max": 5},
        {"query": "deep learning tensorflow keras", "max": 3},
        {"query": "numpy pandas data science", "max": 3},
    ],
    "fullstack": [
        {"query": "react js tutorial", "max": 5},
        {"query": "nodejs express tutorial", "max": 5},
        {"query": "nextjs full course", "max": 3},
        {"query": "mongodb database tutorial", "max": 3},
    ],
    "aws-devops": [
        {"query": "aws tutorial for beginners", "max": 5},
        {"query": "docker kubernetes tutorial", "max": 5},
        {"query": "terraform infrastructure as code", "max": 3},
        {"query": "jenkins ci cd pipeline", "max": 3},
    ],
    "cybersec": [
        {"query": "cybersecurity fundamentals", "max": 5},
        {"query": "ethical hacking tutorial", "max": 5},
        {"query": "network security basics", "max": 3},
        {"query": "penetration testing tutorial", "max": 3},
    ],
    "flutter": [
        {"query": "flutter tutorial for beginners", "max": 5},
        {"query": "dart programming language", "max": 3},
        {"query": "flutter widgets tutorial", "max": 5},
        {"query": "flutter state management", "max": 3},
    ],
}

def setup_courses_in_db():
    """Create courses directly in database"""
    print("📚 Setting up courses in database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create courses table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            is_paid BOOLEAN DEFAULT 0,
            price REAL DEFAULT 0
        )
    """)
    
    # Create videos table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            youtube_id TEXT NOT NULL,
            duration INTEGER,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    """)
    
    # Insert courses
    for course in COURSES:
        cursor.execute("""
            INSERT OR REPLACE INTO courses (id, path, title, description, category, is_paid, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course["id"],
            course["path"],
            course["title"],
            course["description"],
            course["path"],
            0,
            0
        ))
        print(f"  ✅ Created course: {course['title']} ({course['path']})")
    
    conn.commit()
    conn.close()
    print("✅ All courses created in database\n")

def sync_videos_for_course(course_id: int, path: str):
    """Sync videos from YouTube for a specific course"""
    queries = YOUTUBE_QUERIES.get(path, [])
    
    total_synced = 0
    
    for query_config in queries:
        query = query_config["query"]
        max_results = query_config["max"]
        
        print(f"  📹 Syncing: '{query}' (max {max_results})...", end=" ")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1x/youtube/sync",
                json={
                    "course_id": course_id,
                    "query": query,
                    "max_results": max_results
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                inserted = data.get("inserted", 0)
                skipped = data.get("skipped", 0)
                print(f"✅ +{inserted} videos (skipped {skipped})")
                total_synced += inserted
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return total_synced

def main():
    print("=" * 70)
    print("🚀 Complete Setup - Courses + YouTube Videos")
    print("=" * 70)
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/api/v1x/youtube/health", timeout=5).json()
        if not health.get("has_key"):
            print("❌ YouTube API key not configured!")
            return
        print("✅ YouTube API key detected\n")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure backend is running: uvicorn app.main:app --reload --port 8001")
        return
    
    # Step 1: Create courses in database
    setup_courses_in_db()
    
    # Step 2: Sync YouTube videos for each course
    total_videos = 0
    
    for course in COURSES:
        course_id = course["id"]
        path = course["path"]
        title = course["title"]
        
        print(f"{'=' * 70}")
        print(f"📚 Course: {title} ({path})")
        print(f"{'=' * 70}")
        
        synced = sync_videos_for_course(course_id, path)
        total_videos += synced
        
        print(f"  ✅ Total synced for this course: {synced} videos\n")
    
    print(f"{'=' * 70}")
    print(f"🎉 Setup Complete!")
    print(f"{'=' * 70}")
    print(f"✅ Total videos synced: {total_videos}")
    print(f"\n📊 Test endpoints:")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db/python-ai/videos")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db/fullstack/videos")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db/aws-devops/videos")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db/cybersec/videos")
    print(f"  - http://127.0.0.1:8001/api/v1x/courses-db/flutter/videos")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
