#!/usr/bin/env python
"""Check if database tables exist"""
import sqlite3

db_path = "backend/app/data/skillforge.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"Database exists: {len(tables)} tables found")
    
    # Check for resume tables specifically
    table_names = [t[0] for t in tables]
    print(f"\nResume-related tables:")
    for name in sorted(table_names):
        if 'resume' in name.lower():
            print(f"  ✓ {name}")
    
    if 'resume_achievements' in table_names:
        print("\n✓ resume_achievements table EXISTS")
    else:
        print("\n✗ resume_achievements table MISSING")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
