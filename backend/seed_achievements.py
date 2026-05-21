"""
Seed default coding practice achievements
"""
from app.core.db import SessionLocal, Base, engine
# Import User to ensure relationships are set up
from app.models.user import User
from app.modelsx.coding_practice import CodingAchievement

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Define default achievements
achievements = [
    {
        "key": "first_perfect",
        "title": "First Victory",
        "description": "Successfully solve your first challenge with a perfect score",
        "badge_color": "text-green-400",
        "points": 10,
        "coins": 5,
        "criteria_type": "first_perfect",
        "criteria_value": 1
    },
    {
        "key": "perfect_10",
        "title": "Perfectionist",
        "description": "Solve 10 challenges with perfect scores",
        "badge_color": "text-blue-400",
        "points": 50,
        "coins": 25,
        "criteria_type": "perfect_solutions",
        "criteria_value": 10
    },
    {
        "key": "perfect_25",
        "title": "Master Solver",
        "description": "Solve 25 challenges with perfect scores",
        "badge_color": "text-purple-400",
        "points": 150,
        "coins": 75,
        "criteria_type": "perfect_solutions",
        "criteria_value": 25
    },
    {
        "key": "perfect_50",
        "title": "Elite Coder",
        "description": "Solve 50 challenges with perfect scores",
        "badge_color": "text-yellow-400",
        "points": 300,
        "coins": 150,
        "criteria_type": "perfect_solutions",
        "criteria_value": 50
    },
    {
        "key": "challenges_5",
        "title": "Getting Started",
        "description": "Complete 5 challenges",
        "badge_color": "text-indigo-400",
        "points": 25,
        "coins": 10,
        "criteria_type": "challenges_solved",
        "criteria_value": 5
    },
    {
        "key": "challenges_25",
        "title": "Challenge Hunter",
        "description": "Complete 25 challenges",
        "badge_color": "text-cyan-400",
        "points": 100,
        "coins": 50,
        "criteria_type": "challenges_solved",
        "criteria_value": 25
    },
    {
        "key": "challenges_50",
        "title": "Challenge Master",
        "description": "Complete 50 challenges",
        "badge_color": "text-pink-400",
        "points": 250,
        "coins": 125,
        "criteria_type": "challenges_solved",
        "criteria_value": 50
    },
    {
        "key": "submissions_20",
        "title": "Persistent Learner",
        "description": "Make 20 submissions",
        "badge_color": "text-orange-400",
        "points": 50,
        "coins": 25,
        "criteria_type": "submissions",
        "criteria_value": 20
    },
    {
        "key": "submissions_100",
        "title": "Dedicated Practitioner",
        "description": "Make 100 submissions",
        "badge_color": "text-red-400",
        "points": 200,
        "coins": 100,
        "criteria_type": "submissions",
        "criteria_value": 100
    }
]

# Check if achievements already exist
existing = db.query(CodingAchievement).count()
if existing > 0:
    print(f"Achievements already seeded: {existing} achievements exist")
    db.close()
    exit()

# Seed achievements
for ach in achievements:
    achievement = CodingAchievement(**ach)
    db.add(achievement)

db.commit()
print(f"✓ Seeded {len(achievements)} achievements")
db.close()
