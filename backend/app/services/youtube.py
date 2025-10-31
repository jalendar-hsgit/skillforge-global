import os, httpx
from typing import List, Dict, Any
from app.core.config import settings

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

class YouTubeError(RuntimeError):
    pass

def _get_key() -> str:
    key = settings.YOUTUBE_API_KEY or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise YouTubeError("YouTube API key is not configured")
    return key

def search_videos(query: str, max_results: int = 5, region: str | None = None) -> List[Dict[str, Any]]:
    key = _get_key()
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max(1, min(max_results, 25)),
        "key": key,
    }
    region_code = (region or settings.YOUTUBE_API_REGION or "US").upper()
    if region_code:
        params["regionCode"] = region_code

    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(YOUTUBE_SEARCH_URL, params=params)
        if r.status_code != 200:
            raise YouTubeError(f"search_videos HTTP {r.status_code}: {r.text[:300]}")
        data = r.json()
        items = data.get("items", [])
        out = []
        for it in items:
            vid = it.get("id", {}).get("videoId")
            snippet = it.get("snippet", {}) or {}
            if vid:
                out.append({
                    "youtube_id": vid,
                    "title": snippet.get("title") or "",
                    "channel": snippet.get("channelTitle") or "",
                })
        return out
    except httpx.RequestError as e:
        raise YouTubeError(f"search_videos network error: {e!r}") from e

def fetch_durations(video_ids: list[str]) -> dict[str, str]:
    if not video_ids:
        return {}
    key = _get_key()
    params = {
        "part": "contentDetails",
        "id": ",".join(video_ids[:50]),
        "key": key,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(YOUTUBE_VIDEOS_URL, params=params)
        if r.status_code != 200:
            raise YouTubeError(f"fetch_durations HTTP {r.status_code}: {r.text[:300]}")
        data = r.json()
        out = {}
        for it in data.get("items", []):
            vid = it.get("id")
            dur = (it.get("contentDetails", {}) or {}).get("duration") or ""
            if vid:
                out[vid] = dur
        return out
    except httpx.RequestError as e:
        raise YouTubeError(f"fetch_durations network error: {e!r}") from e
