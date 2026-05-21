"""
Gamification Leaderboard API
Rankings based on coins, achievements, quizzes, and more
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.db import SessionLocal
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

class LeaderboardEntry:
    """Individual leaderboard entry"""
    def __init__(self, rank: int, user_id: int, username: str, value: int, avatar: str = None):
        self.rank = rank
        self.user_id = user_id
        self.username = username
        self.value = value
        self.avatar = avatar

@router.get("/global/coins")
def get_global_coins_leaderboard(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get global coins leaderboard.
    Top users by total coins earned.
    """
    db = SessionLocal()
    try:
        # Get users with most coins
        rows = db.execute(text("""
            SELECT 
                u.id, 
                u.email,
                COALESCE(SUM(cl.delta), 0) as total_coins
            FROM users u
            LEFT JOIN coin_ledger cl ON u.id = cl.user_id
            GROUP BY u.id, u.email
            ORDER BY total_coins DESC
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset}).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": offset + idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],  # Extract username from email
                "coins": int(row[2]) if row[2] else 0,
                "badge": "👑" if offset + idx == 0 else "🥈" if offset + idx == 1 else "🥉" if offset + idx == 2 else None
            })
        
        return {
            "leaderboard": leaderboard,
            "limit": limit,
            "offset": offset,
            "total": len(rows)
        }
    finally:
        db.close()

@router.get("/global/achievements")
def get_achievements_leaderboard(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get leaderboard by number of achievements unlocked.
    """
    db = SessionLocal()
    try:
        # Get users with most achievements
        rows = db.execute(text("""
            SELECT 
                u.id,
                u.email,
                COUNT(DISTINCT ua.achievement_id) as achievement_count
            FROM users u
            LEFT JOIN user_achievements ua ON u.id = ua.user_id
            GROUP BY u.id, u.email
            HAVING COUNT(DISTINCT ua.achievement_id) > 0
            ORDER BY achievement_count DESC
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset}).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": offset + idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],
                "achievements": row[2] or 0
            })
        
        return {
            "leaderboard": leaderboard,
            "limit": limit,
            "offset": offset
        }
    finally:
        db.close()

@router.get("/weekly/coins")
def get_weekly_coins_leaderboard(
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get weekly leaderboard - coins earned this week.
    """
    db = SessionLocal()
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        rows = db.execute(text("""
            SELECT 
                u.id,
                u.email,
                COALESCE(SUM(cl.delta), 0) as weekly_coins
            FROM users u
            LEFT JOIN coin_ledger cl ON u.id = cl.user_id AND cl.created_at >= :week_ago
            GROUP BY u.id, u.email
            HAVING COALESCE(SUM(cl.delta), 0) > 0
            ORDER BY weekly_coins DESC
            LIMIT :limit
        """), {"week_ago": week_ago, "limit": limit}).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],
                "coins_this_week": int(row[2]) if row[2] else 0
            })
        
        return {
            "leaderboard": leaderboard,
            "period": "last_7_days",
            "limit": limit
        }
    finally:
        db.close()

@router.get("/category/coding")
def get_coding_leaderboard(
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get leaderboard by coding practice success.
    Based on challenges completed successfully.
    """
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT 
                u.id,
                u.email,
                COUNT(DISTINCT cs.id) as challenges_solved,
                AVG(cs.score) as avg_score
            FROM users u
            LEFT JOIN coding_submissions cs ON u.id = cs.user_id AND cs.status = 'accepted'
            GROUP BY u.id, u.email
            HAVING COUNT(DISTINCT cs.id) > 0
            ORDER BY challenges_solved DESC, avg_score DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],
                "challenges_solved": row[2] or 0,
                "avg_score": float(row[3]) if row[3] else 0
            })
        
        return {
            "leaderboard": leaderboard,
            "category": "coding",
            "limit": limit
        }
    finally:
        db.close()

@router.get("/category/quizzes")
def get_quizzes_leaderboard(
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get leaderboard by quiz performance.
    """
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT 
                u.id,
                u.email,
                COUNT(qa.id) as quizzes_taken,
                AVG(qa.score) as avg_score,
                SUM(CASE WHEN qa.score >= 80 THEN 1 ELSE 0 END) as perfect_scores
            FROM users u
            LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
            GROUP BY u.id, u.email
            HAVING COUNT(qa.id) > 0
            ORDER BY perfect_scores DESC, avg_score DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],
                "quizzes_taken": row[2] or 0,
                "avg_score": float(row[3]) if row[3] else 0,
                "perfect_scores": row[4] or 0
            })
        
        return {
            "leaderboard": leaderboard,
            "category": "quizzes",
            "limit": limit
        }
    finally:
        db.close()

@router.get("/friends")
def get_friends_leaderboard(
    user: User = Depends(get_current_user)
):
    """
    Get leaderboard among user's friends/connections.
    """
    db = SessionLocal()
    try:
        # Get current user's friends (users being followed)
        friends = db.execute(text("""
            SELECT followed_user_id
            FROM user_follows
            WHERE follower_user_id = :uid
        """), {"uid": user.id}).fetchall()
        
        friend_ids = [f[0] for f in friends]
        
        if not friend_ids:
            return {"leaderboard": [], "message": "No friends to compare with"}
        
        # Get coins for friends
        placeholders = ','.join([str(id) for id in friend_ids])
        rows = db.execute(text(f"""
            SELECT 
                u.id,
                u.email,
                COALESCE(SUM(cl.delta), 0) as total_coins
            FROM users u
            LEFT JOIN coin_ledger cl ON u.id = cl.user_id
            WHERE u.id IN ({placeholders})
            GROUP BY u.id, u.email
            ORDER BY total_coins DESC
        """)).fetchall()
        
        leaderboard = []
        for idx, row in enumerate(rows):
            leaderboard.append({
                "rank": idx + 1,
                "user_id": row[0],
                "username": row[1].split('@')[0],
                "coins": int(row[2]) if row[2] else 0
            })
        
        return {
            "leaderboard": leaderboard,
            "scope": "friends",
            "friend_count": len(friend_ids)
        }
    finally:
        db.close()

@router.get("/user-rank/{user_id}")
def get_user_rank(user_id: int):
    """
    Get a specific user's rank on all leaderboards.
    """
    db = SessionLocal()
    try:
        user = db.execute(text("""
            SELECT id, email FROM users WHERE id = :uid
        """), {"uid": user_id}).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get coins rank
        coins_rank = db.execute(text("""
            SELECT RANK() OVER (ORDER BY COALESCE(SUM(cl.delta), 0) DESC) as rank
            FROM (
                SELECT u.id, COALESCE(SUM(cl.delta), 0) as total_coins
                FROM users u
                LEFT JOIN coin_ledger cl ON u.id = cl.user_id
                GROUP BY u.id
            ) ranked
            WHERE id = :uid
        """), {"uid": user_id}).fetchone()
        
        # Get achievements rank
        achievements_rank = db.execute(text("""
            SELECT RANK() OVER (ORDER BY COUNT(DISTINCT ua.achievement_id) DESC) as rank
            FROM (
                SELECT u.id, COUNT(DISTINCT ua.achievement_id) as achievement_count
                FROM users u
                LEFT JOIN user_achievements ua ON u.id = ua.user_id
                GROUP BY u.id
            ) ranked
            WHERE id = :uid
        """), {"uid": user_id}).fetchone()
        
        return {
            "user_id": user_id,
            "username": user[1].split('@')[0],
            "ranks": {
                "coins": coins_rank[0] if coins_rank else None,
                "achievements": achievements_rank[0] if achievements_rank else None
            }
        }
    finally:
        db.close()

@router.get("/my-rank")
def get_my_rank(user: User = Depends(get_current_user)):
    """
    Get current user's rank on leaderboards.
    """
    db = SessionLocal()
    try:
        # Get coins rank
        coins_result = db.execute(text("""
            SELECT COALESCE(SUM(delta), 0) as total_coins
            FROM coin_ledger
            WHERE user_id = :uid
        """), {"uid": user.id}).fetchone()
        
        total_coins = int(coins_result[0]) if coins_result[0] else 0
        
        # Count how many users have more coins
        better_count = db.execute(text("""
            SELECT COUNT(DISTINCT u.id)
            FROM users u
            LEFT JOIN coin_ledger cl ON u.id = cl.user_id
            GROUP BY u.id
            HAVING COALESCE(SUM(cl.delta), 0) > :coins
        """), {"coins": total_coins}).scalar() or 0
        
        return {
            "user_id": user.id,
            "coins": total_coins,
            "rank": better_count + 1,
            "percentile": "calculating..."
        }
    finally:
        db.close()
