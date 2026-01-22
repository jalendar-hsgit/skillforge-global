#!/usr/bin/env python3
"""
Hard reset script - deletes database and recreates with correct schema
Run this AFTER stopping the backend (Ctrl+C in backend terminal)
"""
import os
import sys
import subprocess

db_path = "backend/app/data/skillforge.db"

print("=" * 60)
print("HARD DATABASE RESET")
print("=" * 60)
print()

# Step 1: Delete database
print("[1/3] Deleting old database...")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✓ Deleted {db_path}")
    except Exception as e:
        print(f"✗ Error deleting database: {e}")
        sys.exit(1)
else:
    print(f"✓ Database doesn't exist (already clean)")

print()

# Step 2: Recreate database
print("[2/3] Recreating database with init_db.py...")
os.chdir("backend")
result = subprocess.run([sys.executable, "init_db.py"], capture_output=True, text=True)
if result.returncode == 0:
    print("✓ Database created successfully")
else:
    print(f"✗ Error creating database: {result.stderr}")
    sys.exit(1)

print()

# Step 3: Seed demo data
print("[3/3] Seeding demo data...")
result = subprocess.run([sys.executable, "seed_all_demo_data.py"], capture_output=True, text=True)
if result.returncode == 0:
    print("✓ Demo data seeded successfully")
else:
    print(f"✗ Error seeding data: {result.stderr}")
    sys.exit(1)

print()
print("=" * 60)
print("✓ RESET COMPLETE!")
print("=" * 60)
print()
print("Next: Start backend with:")
print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
print()
