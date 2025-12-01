"""
Migration script to add role column to existing users table.
Run this once to update your database schema.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.db import engine, SessionLocal
from app.models.user import User, UserRole


def migrate_add_user_roles():
    """Add role column to users table and set default values"""
    
    db = SessionLocal()
    
    try:
        print("Starting migration: Adding role column to users table...")
        
        # Check if role column exists
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'role' in columns:
                print("✓ Role column already exists")
            else:
                print("Adding role column...")
                # SQLite doesn't support adding ENUM columns directly
                # We'll add it as TEXT with default value
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
                ))
                conn.commit()
                print("✓ Role column added")
        
        # Update any NULL roles to 'user'
        users = db.query(User).all()
        updated = 0
        for user in users:
            if not hasattr(user, 'role') or user.role is None:
                user.role = UserRole.USER
                updated += 1
        
        if updated > 0:
            db.commit()
            print(f"✓ Updated {updated} users with default 'user' role")
        else:
            print("✓ All users already have roles assigned")
        
        # Show current user count by role
        print("\nCurrent user distribution:")
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            if count > 0:
                print(f"  {role.value}: {count}")
        
        print("\n✅ Migration completed successfully!")
        print("\nTo create your first admin user, use:")
        print("  python create_admin.py <email>")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_add_user_roles()
