#!/usr/bin/env python
"""Test that tables are created when main.py is imported"""
import sys
import os
sys.path.insert(0, 'backend')

print("[1] Importing main...")
try:
    from app.main import app
    print("[1] ✓ main.py imported successfully")
except Exception as e:
    print(f"[1] ✗ Error importing main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[2] Checking if database was created...")
db_path = "backend/app/data/skillforge.db"
if os.path.exists(db_path):
    print(f"[2] ✓ Database file exists at {db_path}")
else:
    print(f"[2] ✗ Database file does not exist")
    sys.exit(1)

print("\n[3] Checking tables...")
import sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]
print(f"[3] Total tables: {table_count}")

for table in ['users', 'resumes', 'resume_achievements']:
    cursor.execute(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table}'")
    exists = cursor.fetchone() is not None
    status = "✓" if exists else "✗"
    print(f"    {status} {table}")

conn.close()
