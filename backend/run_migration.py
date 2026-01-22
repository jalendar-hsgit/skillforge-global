#!/usr/bin/env python3
"""
Simple migration runner for Resume enhancements
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# Get database path
db_path = Path(__file__).parent / "app" / "data" / "skillforge.db"

if not db_path.exists():
    print(f"ERROR: Database not found at {db_path}")
    sys.exit(1)

print(f"Database: {db_path}")
print(f"Database exists\n")

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(resumes)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    print(f"Current columns: {len(existing_cols)}\n")
    
    # Migration 1: Add extra_content
    if 'extra_content' not in existing_cols:
        print("  Adding extra_content...")
        cursor.execute("ALTER TABLE resumes ADD COLUMN extra_content TEXT")
        print("  ADDED extra_content\n")
    else:
        print("  SKIP: extra_content already exists\n")
    
    # Migration 2: Add style_settings_updated_at
    if 'style_settings_updated_at' not in existing_cols:
        print("  Adding style_settings_updated_at...")
        cursor.execute("ALTER TABLE resumes ADD COLUMN style_settings_updated_at DATETIME")
        print("  ADDED style_settings_updated_at\n")
    else:
        print("  SKIP: style_settings_updated_at already exists\n")
    
    # Migration 3: Add style_settings_history
    if 'style_settings_history' not in existing_cols:
        print("  Adding style_settings_history...")
        cursor.execute("ALTER TABLE resumes ADD COLUMN style_settings_history JSON")
        print("  ADDED style_settings_history\n")
    else:
        print("  SKIP: style_settings_history already exists\n")
    
    conn.commit()
    print("Migration completed successfully!\n")
    
    # Verify
    cursor.execute("PRAGMA table_info(resumes)")
    final_cols = {row[1] for row in cursor.fetchall()}
    print(f"Final column count: {len(final_cols)}")
    print(f"New columns: {final_cols - existing_cols}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
