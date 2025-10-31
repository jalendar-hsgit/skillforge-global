import requests, re, datetime
from typing import Iterator, Dict, Any, List, Optional
from app.core.config import settings
from app.core.db import SessionLocal
from app.modelsx.video import Video
from app.modelsx.course import Course

YOUTUBE_API = "https://www.googleapis.com/youtube/v3"

def _parse_iso8601_duration(iso: str) -> int:
    # PT#H#M#S -> seconds
    pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    m = pattern.fullmatch(iso)
    if not m:
        return 0
    h, m_, s = m.groups()
    total = (int(h or 0) * 3600) + (int(m_ or 0) * 60) + int(s or 0)
    return total

def _fetch_playlist_items(playlist_id: str, api_key: str) -> Iterator[Dict[str, Any]]:
    pageToken = None
    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key,
        }
        if pageToken:
            params["pageToken"] = pageToken
        r = requests.get(f"{YOUTUBE_API}/playlistItems", params=params, timeout=20)
        r.raise_for_status()
        j = r.json()
        for item in j.get("items", []):
            yield item
        pageToken = j.get("nextPageToken")
        if not pageToken:
            break

def _fetch_video_durations(video_ids: List[str], api_key: str) -> Dict[str,int]:
    out: Dict[str,int] = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "part": "contentDetails",
            "id": ",".join(batch),
            "key": api_key,
        }
        r = requests.get(f"{YOUTUBE_API}/videos", params=params, timeout=20)
        r.raise_for_status()
        j = r.json()
        for it in j.get("items", []):
            vid = it["id"]
            dur_iso = it["contentDetails"]["duration"]
            out[vid] = _parse_iso8601_duration(dur_iso)
    return out

def sync_course_videos(course_id: int) -> Dict[str, Any]:
    if not settings.YOUTUBE_API_KEY:
        return {"ok": False, "error": "YOUTUBE_API_KEY not configured"}
    api_key = settings.YOUTUBE_API_KEY

    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return {"ok": False, "error": "Course not found"}

        playlist_id = getattr(course, "youtube_playlist_id", None)
        if not playlist_id:
            return {"ok": False, "error": "Course missing youtube_playlist_id"}

        # gather items
        items = list(_fetch_playlist_items(playlist_id, api_key))
        video_map: Dict[str, Dict[str, Any]] = {}
        for it in items:
            snippet = it.get("snippet", {})
            cd = it.get("contentDetails", {})
            vid = cd.get("videoId")
            if not vid:
                continue
            video_map[vid] = {
                "title": snippet.get("title") or "Untitled",
                "published_at": snippet.get("publishedAt"),
                "youtube_id": vid,
            }

        # durations
        durations = _fetch_video_durations(list(video_map.keys()), api_key)

        # upsert
        created = 0
        updated = 0
        for vid, meta in video_map.items():
            v = db.query(Video).filter(Video.youtube_id == vid, Video.course_id == course_id).first()
            dur = durations.get(vid, 0)
            if not v:
                v = Video(course_id=course_id, title=meta["title"], youtube_id=vid, duration=dur)
                db.add(v)
                created += 1
            else:
                changed = False
                if v.title != meta["title"]:
                    v.title = meta["title"]; changed = True
                if dur and v.duration != dur:
                    v.duration = dur; changed = True
                if changed:
                    updated += 1

        # mark course
        now = datetime.datetime.utcnow().isoformat()
        setattr(course, "last_synced_at", now)

        db.commit()
        return {"ok": True, "created": created, "updated": updated, "total_seen": len(video_map)}
    finally:
        db.close()
