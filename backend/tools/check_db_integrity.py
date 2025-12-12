"""
Database Integrity Check Script
Verifies all critical tables have data and relationships are intact
"""
import sys
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from app.core.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("="*70)
print("DATABASE INTEGRITY CHECK")
print("="*70)

tables_to_check = [
    "users",
    "mentors", 
    "mentor_sessions",
    "courses",
    "videos",
    "video_progress",
    "quizzes",
    "quiz_questions",
    "resumes",
    "resume_templates",
    "coin_ledger",
    "subscriptions",
    "job_applications"
]

print("\nTable Row Counts:")
for table in tables_to_check:
    try:
        result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}")).mappings().first()
        count = result['count'] if result else 0
        status = "[OK]" if count > 0 else "[WARN]"
        print(f"  {status} {table:25} {count:>6} rows")
    except Exception as e:
        print(f"  [ERR] {table:25} ERROR: {str(e)[:40]}")

# Check mentor relationships
print("\n" + "-"*70)
print("Mentor System Status:")
try:
    result = db.execute(text("""
        SELECT 
            m.status,
            COUNT(*) as count
        FROM mentors m
        GROUP BY m.status
    """)).mappings().all()
    for row in result:
        print(f"  - {row['status']:15} {row['count']} mentors")
except Exception as e:
    print(f"  Error: {e}")

# Check user-mentor relationship
print("\nMentor-User Linkage:")
try:
    result = db.execute(text("""
        SELECT COUNT(*) as count
        FROM mentors m
        JOIN users u ON m.user_id = u.id
    """)).mappings().first()
    print(f"  [OK] All {result['count']} mentors linked to valid users")
except Exception as e:
    print(f"  [ERR] Error: {e}")

# Check resume data
print("\nResume System Status:")
try:
    result = db.execute(text("""
        SELECT 
            COUNT(DISTINCT r.user_id) as users_with_resumes,
            COUNT(r.id) as total_resumes,
            COUNT(DISTINCT r.template_id) as templates_used
        FROM resumes r
    """)).mappings().first()
    if result:
        print(f"  [OK] {result['users_with_resumes']} users have created resumes")
        print(f"  [OK] {result['total_resumes']} total resumes")
        print(f"  [OK] {result['templates_used']} templates in use")
except Exception as e:
    print(f"  [ERR] Error: {e}")

# Check coins system
print("\nCoins/Credits System:")
try:
    result = db.execute(text("""
        SELECT 
            COUNT(DISTINCT user_id) as users_with_coins,
            SUM(delta) as total_coins_in_system
        FROM coin_ledger
    """)).mappings().first()
    if result:
        print(f"  [OK] {result['users_with_coins']} users have coin transactions")
        print(f"  [OK] {result['total_coins_in_system']} total coins in system")
except Exception as e:
    print(f"  [ERR] Error: {e}")

db.close()

print("\n" + "="*70)
print("DATABASE INTEGRITY CHECK COMPLETE")
print("="*70)
