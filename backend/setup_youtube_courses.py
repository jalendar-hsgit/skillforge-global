"""
Quick setup script to populate courses and sync YouTube videos
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8001"

# Define courses for each path
COURSES = [
    {"id": 1, "path": "python-ai", "title": "Python AI Mastery", "description": "Learn AI with Python"},
    {"id": 2, "path": "fullstack", "title": "Full Stack Development", "description": "Build complete web applications"},
    {"id": 3, "path": "aws-devops", "title": "AWS DevOps Professional", "description": "Master cloud and DevOps"},
    {"id": 4, "path": "cybersec", "title": "Cybersecurity Expert", "description": "Learn ethical hacking and security"},
    {"id": 5, "path": "flutter", "title": "Flutter Mobile Development", "description": "Build cross-platform mobile apps"},
]

# YouTube search queries for each course
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
    print("🚀 YouTube API Setup - Populating Courses with Videos")
    print("=" * 70)
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/api/v1x/youtube/health").json()
        if not health.get("has_key"):
            print("❌ YouTube API key not configured!")
            sys.exit(1)
        print("✅ YouTube API key detected\n")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        sys.exit(1)
    
    total_videos = 0
    
    for course in COURSES:
        course_id = course["id"]
        path = course["path"]
        title = course["title"]
        
        print(f"\n{'=' * 70}")
        print(f"📚 Course: {title} ({path})")
        print(f"{'=' * 70}")
        
        synced = sync_videos_for_course(course_id, path)
        total_videos += synced
        
        print(f"  ✅ Total synced for this course: {synced} videos")
    
    print(f"\n{'=' * 70}")
    print(f"🎉 Setup Complete!")
    print(f"{'=' * 70}")
    print(f"✅ Total videos synced: {total_videos}")
    print(f"\n💡 Next step: Update frontend to use /api/v1x/courses-db endpoints")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
