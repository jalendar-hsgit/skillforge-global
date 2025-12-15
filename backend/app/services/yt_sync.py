from typing import List, Dict, Any
import requests
from dateutil.parser import isoparse
from datetime import timedelta
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modelsx.video import Video

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Quality filters
MIN_DURATION_SECONDS = 180  # 3 minutes - exclude shorts
MAX_DURATION_SECONDS = 18000  # 5 hours - exclude extremely long content
MIN_VIEW_COUNT = 1000  # Minimum views for quality content

# Spam/unwanted keywords
SPAM_KEYWORDS = [
    "subscribe", "like and share", "click here", "free money",
    "get rich quick", "this one trick", "doctors hate", 
    "you won't believe", "shocking", "clickbait",
    "fortnite", "among us", "roblox", "minecraft" # gaming content
]

TRUSTED_CHANNELS = [
    "freecodecamp.org", "traversy media", "programming with mosh",
    "academind", "net ninja", "corey schafer", "tech with tim",
    "fireship", "web dev simplified", "kevin powell", "aws",
    "microsoft azure", "google cloud tech", "docker", "kubernetes"
]

def _parse_iso8601_duration(iso_duration: str) -> int:
    # Example: PT1H2M3S
    # dateutil doesn't parse durations, so do a quick manual parse
    # Fallback to 0 on weird input
    if not iso_duration or not iso_duration.startswith("PT"):
        return 0
    hours = minutes = seconds = 0
    num = ""
    for ch in iso_duration[2:]:
        if ch.isdigit():
            num += ch
        else:
            if ch == "H":
                hours = int(num or 0); num = ""
            elif ch == "M":
                minutes = int(num or 0); num = ""
            elif ch == "S":
                seconds = int(num or 0); num = ""
    return int(timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds())

def _is_quality_video(video_data: Dict[str, Any]) -> bool:
    """
    Filter out low-quality, spam, or irrelevant videos
    Returns True if video passes quality checks
    """
    title = video_data.get("title", "").lower()
    duration = video_data.get("duration_sec", 0)
    channel = video_data.get("channel", "").lower()
    view_count = video_data.get("view_count", 0)
    like_count = video_data.get("like_count", 0)
    
    # 1. Duration check - exclude shorts and extremely long content
    if duration < MIN_DURATION_SECONDS or duration > MAX_DURATION_SECONDS:
        return False
    
    # 2. Trust established educational channels
    for trusted in TRUSTED_CHANNELS:
        if trusted in channel:
            return True
    
    # 3. Check for spam keywords in title
    spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in title)
    if spam_count >= 2:  # Multiple spam indicators
        return False
    
    # 4. View count filter (unless from trusted channel)
    if view_count < MIN_VIEW_COUNT:
        return False
    
    # 5. Engagement ratio check (likes should be reasonable)
    if view_count > 0 and like_count > 0:
        engagement_ratio = like_count / view_count
        # Too low engagement might indicate low quality
        if engagement_ratio < 0.001:  # Less than 0.1% likes
            return False
    
    # 6. Title quality check - should contain relevant keywords
    educational_keywords = [
        "tutorial", "course", "guide", "learn", "beginner",
        "advanced", "complete", "crash course", "explained",
        "introduction", "masterclass", "fundamentals", "basics"
    ]
    has_educational_keyword = any(kw in title for kw in educational_keywords)
    
    # If no educational keywords and not from trusted channel, be more strict
    if not has_educational_keyword and view_count < MIN_VIEW_COUNT * 5:
        return False
    
    return True

def search_videos(query: str, max_results: int = 10, apply_filters: bool = True) -> List[Dict[str, Any]]:
    """
    Search YouTube videos with quality filtering
    
    Args:
        query: Search query
        max_results: Maximum results to return
        apply_filters: Whether to apply quality filters (default True)
    """
    api_key = settings.YOUTUBE_API_KEY
    
    # Search with higher max to compensate for filtering
    search_max = max_results * 3 if apply_filters else max_results
    
    params = {
        "part": "snippet",
        "type": "video",
        "maxResults": min(search_max, 50),  # API limit
        "q": query,
        "key": api_key,
        "safeSearch": "strict",
        "videoDefinition": "high",  # Prefer HD content
        "order": "relevance",  # Most relevant first
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]

    if not video_ids:
        return []

    # Get details including statistics
    params2 = {
        "part": "contentDetails,snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    r2 = requests.get(YOUTUBE_VIDEOS_URL, params=params2, timeout=15)
    r2.raise_for_status()
    d2 = r2.json()

    detail_by_id = {v["id"]: v for v in d2.get("items", [])}

    results = []
    for vid in video_ids:
        detail = detail_by_id.get(vid)
        if not detail:
            continue
        
        snip = detail.get("snippet", {})
        cont = detail.get("contentDetails", {})
        stats = detail.get("statistics", {})
        
        title = snip.get("title") or "Untitled"
        duration_sec = _parse_iso8601_duration(cont.get("duration", ""))
        channel_title = snip.get("channelTitle", "")
        
        # Get statistics
        view_count = int(stats.get("viewCount", 0))
        like_count = int(stats.get("likeCount", 0))
        
        thumbnails = snip.get("thumbnails") or {}
        thumb = thumbnails.get("high") or thumbnails.get("medium") or thumbnails.get("default") or {}
        
        video_data = {
            "youtube_id": vid,
            "title": title,
            "duration_sec": duration_sec,
            "channel": channel_title,
            "thumbnail": thumb.get("url"),
            "view_count": view_count,
            "like_count": like_count,
        }
        
        # Apply quality filter
        if apply_filters:
            if not _is_quality_video(video_data):
                continue
        
        results.append(video_data)
        
        # Stop when we have enough quality videos
        if len(results) >= max_results:
            break
    
    return results

def save_videos(db: Session, course_id: int, videos: List[Dict[str, Any]]) -> Dict[str, int]:
    inserted = 0
    skipped = 0
    for v in videos:
        youtube_id = v["youtube_id"]
        # skip if already present for this course + youtube_id
        exists = db.execute(
            select(Video.id).where(
                Video.course_id == course_id,
                Video.youtube_id == youtube_id
            )
        ).first()
        if exists:
            skipped += 1
            continue
        row = Video(
            course_id=course_id,
            title=v["title"],
            youtube_id=youtube_id,
            duration=str(v["duration_sec"] or 0),
        )
        db.add(row)
        inserted += 1
    db.commit()
    return {"inserted": inserted, "skipped": skipped}
