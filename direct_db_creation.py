#!/usr/bin/env python
"""Direct database creation test"""
import sys
import os
sys.path.insert(0, 'backend')

# Delete old db
if os.path.exists('backend/app/data/skillforge.db'):
    os.remove('backend/app/data/skillforge.db')
    print("Old database deleted")

# Import Base and engine FIRST
from app.core.db import Base, engine

# Import ALL models to register them
print("Importing models...")
from app.modelsx.resume import ResumeAchievement
from app.models import User

# Now create all tables
print(f"Creating tables... ({len(Base.metadata.tables)} registered)")
Base.metadata.create_all(bind=engine)
print(f"✓ Tables created")

# Verify
import sqlite3
conn = sqlite3.connect('backend/app/data/skillforge.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
count = cursor.fetchone()[0]
print(f"✓ Database now has {count} tables")

for table in ['users', 'resumes', 'resume_achievements']:
    cursor.execute(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table}'")
    exists = cursor.fetchone() is not None
    print(f"  {'✓' if exists else '✗'} {table}")

conn.close()
