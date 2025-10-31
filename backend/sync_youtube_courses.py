"""
YouTube Sync Script - Populate courses from YouTube API

This script uses your YouTube API key to search and import videos
into the database dynamically.

Usage:
    python sync_youtube_courses.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

# Define search queries for each learning path
SYNC_CONFIG = [
    {
        "path": "python-ai",
        "searches": [
            {"query": "python programming tutorial", "max": 10},
            {"query": "machine learning python", "max": 10},
            {"query": "numpy pandas tutorial", "max": 5},
            {"query": "deep learning tensorflow", "max": 5},
        ]
    },
    {
        "path": "fullstack",
        "searches": [
            {"query": "react tutorial", "max": 10},
            {"query": "nodejs express tutorial", "max": 10},
            {"query": "mongodb tutorial", "max": 5},
            {"query": "next.js tutorial", "max": 5},
        ]
    },
    {
        "path": "aws-devops",
        "searches": [
            {"query": "aws tutorial", "max": 10},
            {"query": "docker kubernetes tutorial", "max": 10},
            {"query": "terraform tutorial", "max": 5},
            {"query": "CI/CD pipeline tutorial", "max": 5},
        ]
    },
    {
        "path": "cybersec",
        "searches": [
            {"query": "cybersecurity fundamentals", "max": 10},
            {"query": "ethical hacking tutorial", "max": 10},
            {"query": "network security", "max": 5},
            {"query": "penetration testing", "max": 5},
        ]
    },
    {
        "path": "flutter",
        "searches": [
            {"query": "flutter tutorial", "max": 10},
            {"query": "dart programming", "max": 10},
            {"query": "flutter widgets", "max": 5},
            {"query": "flutter state management", "max": 5},
        ]
    },
]

def preview_videos(query: str, max_results: int = 10):
    """Preview videos from YouTube without saving"""
    url = f"{BASE_URL}/api/v1x/youtube/preview"
    payload = {
        "course_id": 1,  # Dummy, not used in preview
        "query": query,
        "max_results": max_results
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"❌ Error previewing '{query}': {e}")
        return []

def sync_videos_to_db(course_id: int, query: str, max_results: int = 10):
    """Sync videos from YouTube to database"""
    url = f"{BASE_URL}/api/v1x/youtube/sync"
    payload = {
        "course_id": course_id,
        "query": query,
        "max_results": max_results
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"❌ Error syncing '{query}': {e}")
        return None

def main():
    print("=" * 60)
    print("🎬 YouTube Course Sync Tool")
    print("=" * 60)
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/api/v1x/youtube/health").json()
        if not health.get("has_key"):
            print("❌ YouTube API key not configured!")
            return
        print("✅ YouTube API key detected\n")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Preview mode or sync mode?
    mode = input("Choose mode:\n  1. Preview (see videos without saving)\n  2. Sync (save to database)\nChoice: ").strip()
    
    if mode == "1":
        # Preview mode
        print("\n📺 PREVIEW MODE - Videos will NOT be saved\n")
        for path_config in SYNC_CONFIG:
            path = path_config["path"]
            print(f"\n🔹 Path: {path}")
            print("-" * 40)
            
            for search in path_config["searches"]:
                query = search["query"]
                max_results = search["max"]
                print(f"\n  Search: '{query}' (max {max_results})")
                
                videos = preview_videos(query, max_results)
                print(f"  Found: {len(videos)} videos")
                
                for i, video in enumerate(videos[:3], 1):  # Show first 3
                    print(f"    {i}. {video['title']}")
                    print(f"       Duration: {video['duration_sec']}s | Channel: {video['channel']}")
                
                if len(videos) > 3:
                    print(f"    ... and {len(videos) - 3} more")
    
    elif mode == "2":
        # Sync mode
        print("\n💾 SYNC MODE - Videos will be saved to database\n")
        confirm = input("⚠️  This will add videos to your database. Continue? (y/n): ").strip().lower()
        
        if confirm != "y":
            print("Cancelled.")
            return
        
        total_synced = 0
        
        for path_config in SYNC_CONFIG:
            path = path_config["path"]
            print(f"\n🔹 Path: {path}")
            print("-" * 40)
            
            # Note: This assumes course_id corresponds to path order
            # You may need to fetch actual course IDs from your database
            course_id = 1  # Placeholder - adjust based on your DB
            
            for search in path_config["searches"]:
                query = search["query"]
                max_results = search["max"]
                print(f"  Syncing: '{query}' (max {max_results})...", end=" ")
                
                result = sync_videos_to_db(course_id, query, max_results)
                
                if result:
                    inserted = result.get("inserted", 0)
                    skipped = result.get("skipped", 0)
                    print(f"✅ Added {inserted}, Skipped {skipped}")
                    total_synced += inserted
                else:
                    print("❌ Failed")
        
        print(f"\n{'=' * 60}")
        print(f"✅ Total videos synced: {total_synced}")
        print(f"{'=' * 60}")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
