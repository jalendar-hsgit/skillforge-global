"""
Seed demo contests data for SkillForge Global.
Creates sample programming contests with various statuses.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.core.db import SessionLocal, engine, Base
from app.modelsx.contests import (
    Contest, ContestStatus, ContestType,
    ContestChallenge, ContestParticipant, ContestPrize
)
from app.modelsx.coding_practice import CodingChallenge  # Required for relationship
from app.models.user import User


def seed_contests():
    """Seed demo contests."""
    db = SessionLocal()
    
    try:
        # Get admin user for creating contests
        admin = db.query(User).filter(User.email == "admin@skillforge.com").first()
        if not admin:
            print("❌ Admin user not found. Run seed_admin_users.py first.")
            return
        
        # Check if contests already exist
        existing = db.query(Contest).first()
        if existing:
            print("✅ Contests already seeded. Skipping.")
            return
        
        now = datetime.utcnow()
        
        contests_data = [
            # Upcoming Contest
            {
                "title": "Weekly Algorithm Challenge #42",
                "description": "Test your algorithmic skills with a set of challenging problems covering arrays, trees, and dynamic programming.",
                "rules": "1. Individual participation only\n2. No external help or AI tools\n3. Time limit: 2 hours\n4. Partial scoring enabled",
                "contest_type": ContestType.INDIVIDUAL,
                "difficulty": "medium",
                "category": "algorithms",
                "start_time": now + timedelta(days=3),
                "end_time": now + timedelta(days=3, hours=2),
                "registration_deadline": now + timedelta(days=2, hours=23),
                "status": ContestStatus.UPCOMING,
                "is_public": True,
                "is_featured": True,
                "entry_fee": 0,
                "total_prize_pool": 1000,
                "max_participants": 500,
                "min_skill_level": 0,
                "banner_image": "/images/contests/algorithm-challenge.png",
                "tags": {"topics": ["arrays", "trees", "dp"], "sponsor": "SkillForge"},
            },
            # Active Contest
            {
                "title": "Spring Code Sprint 2025",
                "description": "24-hour coding marathon! Solve as many challenges as you can and climb the leaderboard.",
                "rules": "1. Individual or team (max 3)\n2. Any programming language\n3. Multiple attempts allowed\n4. Points based on difficulty",
                "contest_type": ContestType.INDIVIDUAL,
                "difficulty": "mixed",
                "category": "general",
                "start_time": now - timedelta(hours=6),
                "end_time": now + timedelta(hours=18),
                "registration_deadline": now - timedelta(days=1),
                "status": ContestStatus.ACTIVE,
                "is_public": True,
                "is_featured": True,
                "entry_fee": 50,  # 50 coins
                "total_prize_pool": 5000,
                "max_participants": 1000,
                "min_skill_level": 10,
                "banner_image": "/images/contests/spring-sprint.png",
                "tags": {"topics": ["all"], "sponsor": "TechCorp"},
            },
            # Finished Contest
            {
                "title": "Data Structures Deep Dive",
                "description": "Master data structures through this intensive contest focusing on stacks, queues, trees, and graphs.",
                "rules": "1. Individual participation\n2. 3 hours duration\n3. No partial scoring",
                "contest_type": ContestType.INDIVIDUAL,
                "difficulty": "hard",
                "category": "data-structures",
                "start_time": now - timedelta(days=7),
                "end_time": now - timedelta(days=7) + timedelta(hours=3),
                "registration_deadline": now - timedelta(days=8),
                "status": ContestStatus.FINISHED,
                "is_public": True,
                "is_featured": False,
                "entry_fee": 0,
                "total_prize_pool": 2000,
                "max_participants": 300,
                "min_skill_level": 30,
                "total_participants": 245,
                "total_submissions": 1876,
            },
            # Team Contest - Upcoming
            {
                "title": "Team Hackathon: Build a Feature",
                "description": "Form a team and build a complete feature. Best implementations win!",
                "rules": "1. Teams of 2-4 members\n2. 48-hour duration\n3. Must use provided starter code\n4. Judged on functionality, code quality, and creativity",
                "contest_type": ContestType.TEAM,
                "difficulty": "hard",
                "category": "fullstack",
                "start_time": now + timedelta(days=10),
                "end_time": now + timedelta(days=12),
                "registration_deadline": now + timedelta(days=9),
                "status": ContestStatus.UPCOMING,
                "is_public": True,
                "is_featured": True,
                "entry_fee": 100,
                "total_prize_pool": 10000,
                "max_participants": 50,  # 50 teams
                "min_skill_level": 50,
            },
            # Draft Contest (admin only)
            {
                "title": "Expert Challenge: System Design",
                "description": "Advanced system design problems for experienced developers.",
                "rules": "TBD",
                "contest_type": ContestType.INDIVIDUAL,
                "difficulty": "expert",
                "category": "system-design",
                "start_time": now + timedelta(days=30),
                "end_time": now + timedelta(days=30, hours=4),
                "registration_deadline": now + timedelta(days=29),
                "status": ContestStatus.DRAFT,
                "is_public": False,
                "is_featured": False,
                "entry_fee": 200,
                "total_prize_pool": 15000,
            },
        ]
        
        created_contests = []
        for data in contests_data:
            contest = Contest(
                created_by_id=admin.id,
                **data
            )
            db.add(contest)
            created_contests.append(contest)
        
        db.commit()
        
        # Refresh to get IDs
        for contest in created_contests:
            db.refresh(contest)
        
        # Add prizes to contests
        prizes_data = [
            # Weekly Algorithm Challenge prizes
            (created_contests[0], [
                {"rank_min": 1, "rank_max": 1, "title": "1st Place", "coins_reward": 500, "description": "Gold trophy + 500 coins"},
                {"rank_min": 2, "rank_max": 2, "title": "2nd Place", "coins_reward": 300, "description": "Silver trophy + 300 coins"},
                {"rank_min": 3, "rank_max": 3, "title": "3rd Place", "coins_reward": 200, "description": "Bronze trophy + 200 coins"},
            ]),
            # Spring Code Sprint prizes
            (created_contests[1], [
                {"rank_min": 1, "rank_max": 1, "title": "Champion", "coins_reward": 2500, "description": "Champion badge + 2500 coins"},
                {"rank_min": 2, "rank_max": 2, "title": "Runner Up", "coins_reward": 1500, "description": "1500 coins"},
                {"rank_min": 3, "rank_max": 3, "title": "3rd Place", "coins_reward": 1000, "description": "1000 coins"},
            ]),
            # Team Hackathon prizes
            (created_contests[3], [
                {"rank_min": 1, "rank_max": 1, "title": "Winning Team", "coins_reward": 5000, "description": "5000 coins per team member"},
                {"rank_min": 2, "rank_max": 2, "title": "2nd Place Team", "coins_reward": 3000, "description": "3000 coins per team member"},
                {"rank_min": 3, "rank_max": 3, "title": "3rd Place Team", "coins_reward": 2000, "description": "2000 coins per team member"},
            ]),
        ]
        
        for contest, prizes in prizes_data:
            for prize_data in prizes:
                prize = ContestPrize(
                    contest_id=contest.id,
                    **prize_data
                )
                db.add(prize)
        
        db.commit()
        
        print(f"✅ Created {len(created_contests)} contests with prizes")
        
        # Summary
        print("\n📊 Contest Summary:")
        for contest in created_contests:
            print(f"  - [{contest.status.value.upper()}] {contest.title}")
            print(f"    Type: {contest.contest_type.value}, Difficulty: {contest.difficulty}")
            print(f"    Prize Pool: {contest.total_prize_pool} coins")
        
    except Exception as e:
        print(f"❌ Error seeding contests: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🎮 Seeding Contests Demo Data...")
    seed_contests()
    print("\n✅ Done!")
