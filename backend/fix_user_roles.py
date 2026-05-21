"""
Direct SQL migration to update user roles from lowercase to uppercase.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    print("Migrating user roles from lowercase to uppercase...")
    
    with engine.connect() as conn:
        # Check current state
        result = conn.execute(text("SELECT COUNT(*), role FROM users GROUP BY role"))
        print("\nCurrent role distribution:")
        for count, role in result:
            print(f"  {role}: {count} users")
        
        # Update roles
        print("\nUpdating roles...")
        
        # Update each role
        for old, new in [('user', 'USER'), ('mentor', 'MENTOR'), ('admin', 'ADMIN'), ('superadmin', 'SUPERADMIN')]:
            result = conn.execute(
                text("UPDATE users SET role = :new WHERE role = :old"),
                {"old": old, "new": new}
            )
            if result.rowcount > 0:
                print(f"  ✅ {old} → {new}: {result.rowcount} users")
        
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT COUNT(*), role FROM users GROUP BY role"))
        print("\nRole distribution after migration:")
        for count, role in result:
            print(f"  {role}: {count} users")
        
        print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate()
