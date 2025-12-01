"""
Quick migration to add user_id column to resume_analytics table.
Run this once to update the database schema.
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings

def migrate():
    """Add user_id column to resume_analytics if it doesn't exist."""
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(resume_analytics)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to resume_analytics table...")
            cursor.execute("""
                ALTER TABLE resume_analytics 
                ADD COLUMN user_id INTEGER
            """)
            conn.commit()
            print("✅ user_id column added successfully")
        else:
            print("✅ user_id column already exists")
        
        # Show current schema
        cursor.execute("PRAGMA table_info(resume_analytics)")
        print("\nCurrent resume_analytics schema:")
        for row in cursor.fetchall():
            print(f"  {row[1]}: {row[2]}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
