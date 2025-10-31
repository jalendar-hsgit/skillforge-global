from typing import List, Dict, Any
import requests
from dateutil.parser import isoparse
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modelsx.video import Video

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

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

def search_videos(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    api_key = settings.YOUTUBE_API_KEY
    params = {
        "part": "snippet",
        "type": "video",
        "maxResults": max_results,
        "q": query,
        "key": api_key,
        "safeSearch": "moderate",
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]

    if not video_ids:
        return []

    # get details (duration, channel) in one call
    params2 = {
        "part": "contentDetails,snippet",
        "id": ",".join(video_ids),
        "key": api_key,
        "maxHeight": 720,
        "maxWidth": 1280,
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
        title = snip.get("title") or "Untitled"
        duration_sec = _parse_iso8601_duration(cont.get("duration"))
        channel_title = snip.get("channelTitle")
        thumbnails = snip.get("thumbnails") or {}
        thumb = thumbnails.get("high") or thumbnails.get("medium") or thumbnails.get("default") or {}
        results.append({
            "youtube_id": vid,
            "title": title,
            "duration_sec": duration_sec,
            "channel": channel_title,
            "thumbnail": thumb.get("url"),
        })
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
