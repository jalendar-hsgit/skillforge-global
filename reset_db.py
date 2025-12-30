#!/usr/bin/env python
"""Reinitialize database"""
import shutil
import os

db_path = "backend/app/data/skillforge.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Removed {db_path}")
else:
    print(f"Database doesn't exist at {db_path}")

print("Restart the backend server to recreate the database")
