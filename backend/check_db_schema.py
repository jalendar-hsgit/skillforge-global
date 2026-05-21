#!/usr/bin/env python
"""Payment System Test - Check actual schema first"""

import sqlite3

DATABASE = "app/data/skillforge.db"
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cur.fetchall()]

print("ALL TABLES IN DATABASE:")
for t in tables:
    print(f"  - {t}")

# Check mentors table specifically
print("\n\nMENTORS TABLE SCHEMA:")
cur.execute("PRAGMA table_info(mentors)")
for row in cur.fetchall():
    print(f"  {row}")

# Check users table
print("\n\nUSERS TABLE SCHEMA:")
cur.execute("PRAGMA table_info(users)")
for row in cur.fetchall():
    print(f"  {row}")

# Check mentor_sessions
print("\n\nMENTOR_SESSIONS TABLE SCHEMA:")
cur.execute("PRAGMA table_info(mentor_sessions)")
for row in cur.fetchall():
    print(f"  {row}")

conn.close()
