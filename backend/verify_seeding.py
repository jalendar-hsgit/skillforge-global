#!/usr/bin/env python3
"""Verify all database tables are seeded."""
from app.core.db import SessionLocal
from sqlalchemy import text, inspect

db = SessionLocal()
engine = db.get_bind()

print("=== DATABASE SEED VERIFICATION ===\n")

inspector = inspect(engine)
core_tables = {
    'users': 'Users',
    'courses': 'Courses', 
    'quizzes': 'Quizzes',
    'resumes': 'Resumes',
    'mentors': 'Mentors',
    'mentor_sessions': 'Mentor Sessions',
    'mentor_availability': 'Mentor Availability',
    'coin_ledger': 'Coin Ledger',
}

for table_name, label in core_tables.items():
    try:
        count = db.execute(text(f"SELECT COUNT(*) FROM [{table_name}]")).scalar()
        status = "✓" if count > 0 else "⚠"
        print(f"{status} {label:30} {count:5} rows")
    except Exception as e:
        print(f"✗ {label:30} Table missing or error")

print("\n✓ Database seed verification complete!")
db.close()
