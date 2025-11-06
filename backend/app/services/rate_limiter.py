"""
Simple in-memory rate limiter for FastAPI endpoints.
Not suitable for multi-process production; replace with Redis for scaling.
"""
from __future__ import annotations

import time
from typing import Dict, Tuple
from fastapi import HTTPException

# key: (user_id, bucket) -> list of timestamps (seconds)
_events: Dict[Tuple[int, str], list] = {}


def rate_limit(user_id: int, bucket: str, limit: int, window_seconds: int) -> None:
    """
    Enforce a simple sliding window rate limit.

    Args:
        user_id: The authenticated user's id
        bucket: Logical bucket name (e.g., 'quizzes:generate')
        limit: Allowed requests in the window
        window_seconds: Window size in seconds

    Raises:
        HTTPException 429 when limit exceeded
    """
    now = time.time()
    key = (int(user_id), str(bucket))
    history = _events.get(key, [])
    # drop events outside window
    cutoff = now - window_seconds
    history = [t for t in history if t >= cutoff]

    if len(history) >= limit:
        # retry-after = time until next event drops out
        retry_after = int(max(1, window_seconds - (now - history[0])))
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after}s.",
            headers={"Retry-After": str(retry_after)}
        )

    history.append(now)
    _events[key] = history


def get_remaining(user_id: int, bucket: str, limit: int, window_seconds: int) -> int:
    """Get remaining requests in current window."""
    now = time.time()
    key = (int(user_id), str(bucket))
    history = _events.get(key, [])
    cutoff = now - window_seconds
    history = [t for t in history if t >= cutoff]
    return max(0, limit - len(history))
