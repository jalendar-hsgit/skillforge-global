"""
Database Initialization Script
Handles fresh database creation with proper order of table creation
Run this script to initialize a fresh database with all tables and basic seed data
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text, inspect
from app.core.db import Base, engine
from app.core.config import settings

def init_database():
    """Initialize the database with all tables"""
    print(f"[Init] Starting database initialization...")
    print(f"[Init] Database URL: {settings.DATABASE_URL}")
    
    try:
        # Get inspector to check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"[Init] Found {len(existing_tables)} existing tables")
            print(f"[Init] Skipping table creation (database already initialized)")
            return True
        
        print(f"[Init] No existing tables found. Creating new database schema...")
        
        # For SQLite, disable foreign key constraints during table creation
        if "sqlite" in str(engine.url).lower():
            print(f"[Init] Using SQLite - temporarily disabling foreign key constraints")
            with engine.begin() as conn:
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                print(f"[Init] Creating tables from Base metadata...")
                Base.metadata.create_all(bind=conn)
                conn.execute(text("PRAGMA foreign_keys=ON"))
        else:
            print(f"[Init] Using non-SQLite database - creating tables normally")
            Base.metadata.create_all(bind=engine)
        
        # Verify table creation
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        print(f"[Init] ✅ Successfully created {len(created_tables)} tables")
        
        return True
        
    except Exception as e:
        print(f"[Init] ❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_basic_data():
    """Seed basic data (optional - modify as needed)"""
    from app.core.db import SessionLocal
    
    print(f"[Init] Seeding basic data...")
    try:
        db = SessionLocal()
        # Add basic seed data here if needed
        db.close()
        print(f"[Init] ✅ Basic data seeded successfully")
        return True
    except Exception as e:
        print(f"[Init] ⚠️  Could not seed data: {e}")
        return False

if __name__ == "__main__":
    print(f"=" * 70)
    print(f"Database Initialization Script")
    print(f"=" * 70)
    
    # Initialize database
    if init_database():
        print(f"[Init] ✅ Database initialization complete!")
        
        # Optionally seed data
        seed_basic_data()
        
        print(f"[Init] Ready to run: uvicorn app.main:app --reload")
    else:
        print(f"[Init] ❌ Database initialization failed!")
        sys.exit(1)
