"""
Add role column to users table
"""
from sqlalchemy import text
from app.core.db import SessionLocal

def migrate():
    """Add role column to users table with default value"""
    db = SessionLocal()
    
    try:
        print("Adding 'role' column to users table...")
        
        # Check if column exists
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'role' in columns:
            print("✓ Role column already exists")
            return
        
        # Add role column with default value 'user'
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL
        """))
        
        db.commit()
        print("✓ Role column added successfully!")
        
        # Verify
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"✓ Users table has {count} existing users")
        
        if count > 0:
            print("  All existing users defaulted to 'user' role")
            print("  Use create_admin.py to promote users to admin/superadmin")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Add Role Column")
    print("="*60)
    migrate()
    print("="*60)
    print("Migration complete!")
    print("="*60)
