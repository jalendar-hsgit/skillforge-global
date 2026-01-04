#!/usr/bin/env python
import sqlite3

db_path = "app/data/skillforge.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("ERROR: users table does not exist!")
        exit(1)
    
    # Get all columns
    cursor.execute("PRAGMA table_info(users)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    print("USER TABLE COLUMNS:")
    for name, dtype in sorted(columns.items()):
        print(f"  ✓ {name}: {dtype}")
    
    # Check for required columns
    required = ["id", "email", "password_hash", "name", "bio", "avatar_url", "phone", "location", "skills"]
    missing = [c for c in required if c not in columns]
    
    print(f"\nTotal columns: {len(columns)}")
    if missing:
        print(f"MISSING COLUMNS: {missing}")
        exit(1)
    else:
        print("✓ All required columns present!")
    
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
