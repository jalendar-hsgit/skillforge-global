#!/usr/bin/env python
"""Create database with all tables"""
import sys
import os
sys.path.insert(0, 'backend')
os.chdir('backend')

# Remove old database
if os.path.exists('app/data/skillforge.db'):
    os.remove('app/data/skillforge.db')
    print("✓ Old database removed")

# Import ALL models
print("Importing all models...")
from app.core.db import Base, engine
from app.modelsx.resume import ResumeAchievement
from app.main import app  # This will trigger all imports in main

# Create tables
print(f"Creating tables... ({len(Base.metadata.tables)} registered)")
Base.metadata.create_all(bind=engine)
print("✓ Tables created")

# Verify
import sqlite3
conn = sqlite3.connect('app/data/skillforge.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resume_achievements'")
result = cursor.fetchone()
if result:
    print("✓✓✓ resume_achievements table EXISTS!")
else:
    print("✗✗✗ resume_achievements table MISSING!")
    # List all resume tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%resume%'")
    tables = cursor.fetchall()
    print(f"Found {len(tables)} resume tables: {[t[0] for t in tables]}")
conn.close()
