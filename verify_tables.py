#!/usr/bin/env python
"""Check database tables"""
import sqlite3

db_path = "backend/app/data/skillforge.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check key tables
tables_to_check = ['users', 'resumes', 'resume_achievements']

for table in tables_to_check:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    result = cursor.fetchone()
    if result:
        print(f"✓ {table} exists")
    else:
        print(f"✗ {table} MISSING")

conn.close()
