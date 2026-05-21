#!/usr/bin/env python3
"""
Resume Builder Database & Detailed Testing
"""

import sys
sys.path.insert(0, r'd:\python code\sfg\skillforge-global\backend')

from app.core.db import Base, engine
from sqlalchemy import inspect, text

print("="*80)
print("RESUME BUILDER DATABASE ANALYSIS")
print("="*80)

# Get inspector
inspector = inspect(engine)

# Get all tables
all_tables = inspector.get_table_names()
print(f"\nTotal tables in database: {len(all_tables)}")

# Check resume-related tables
print("\nResume-related tables:")
resume_tables = [t for t in all_tables if 'resume' in t.lower() or 'achievement' in t.lower()]
for table in sorted(resume_tables):
    columns = inspector.get_columns(table)
    print(f"\n{table}:")
    for col in columns:
        col_type = str(col['type'])
        nullable = "nullable" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']:<30} {col_type:<20} {nullable}")

# Check if tables exist
print("\n" + "="*80)
print("TABLE EXISTENCE CHECK")
print("="*80)

critical_tables = [
    'resumes',
    'resume_achievements', 
    'work_experiences',
    'education',
    'resume_projects',
    'resume_skills',
    'resume_certificates'
]

for table in critical_tables:
    exists = table in all_tables
    status = "OK" if exists else "MISSING"
    print(f"{status:<10} {table}")

# Try to query resume count
print("\n" + "="*80)
print("DATABASE OPERATIONS TEST")
print("="*80)

try:
    with engine.connect() as conn:
        # Count resumes
        result = conn.execute(text("SELECT COUNT(*) as cnt FROM resumes"))
        count = result.scalar()
        print(f"Resumes in database: {count}")
        
        # Check achievements table structure
        result = conn.execute(text("PRAGMA table_info(resume_achievements)"))
        cols = result.fetchall()
        print(f"\nresume_achievements columns: {len(cols)}")
        for col in cols:
            print(f"  - {col[1]:<20} {col[2]}")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("DONE")
print("="*80)
