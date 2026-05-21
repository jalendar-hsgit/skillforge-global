"""Seed admin and mentor users for development/testing."""
from app.core.db import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def seed_admin_users():
    db = SessionLocal()
    try:
        # Create superadmin user if not exists
        superadmin = db.query(User).filter(User.email == "superadmin@skillforge.com").first()
        if not superadmin:
            superadmin = User(
                email="superadmin@skillforge.com",
                password_hash=get_password_hash("super123"),
                role=UserRole.SUPERADMIN
            )
            db.add(superadmin)
            print("✓ Created superadmin user: superadmin@skillforge.com / super123")
        else:
            # Update existing to ensure role is correct
            superadmin.role = UserRole.SUPERADMIN
            print("✓ Superadmin user already exists (role updated)")
        
        # Create admin user if not exists
        admin = db.query(User).filter(User.email == "admin@skillforge.com").first()
        if not admin:
            admin = User(
                email="admin@skillforge.com",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin)
            print("✓ Created admin user: admin@skillforge.com / admin123")
        else:
            # Update existing to ensure role is correct
            admin.role = UserRole.ADMIN
            print("✓ Admin user already exists (role updated)")
        
        # Create mentor user if not exists
        mentor = db.query(User).filter(User.email == "mentor@skillforge.com").first()
        if not mentor:
            mentor = User(
                email="mentor@skillforge.com",
                password_hash=get_password_hash("mentor123"),
                role=UserRole.MENTOR
            )
            db.add(mentor)
            print("✓ Created mentor user: mentor@skillforge.com / mentor123")
        else:
            # Update existing to ensure role is correct
            mentor.role = UserRole.MENTOR
            print("✓ Mentor user already exists (role updated)")
        
        # Create regular user if not exists
        user = db.query(User).filter(User.email == "user@skillforge.com").first()
        if not user:
            user = User(
                email="user@skillforge.com",
                password_hash=get_password_hash("user123"),
                role=UserRole.USER
            )
            db.add(user)
            print("✓ Created regular user: user@skillforge.com / user123")
        else:
            # Update existing to ensure role is correct
            user.role = UserRole.USER
            print("✓ Regular user already exists (role updated)")
        
        db.commit()
        print("\n✅ All user types ready for login:")
        print("   - Superadmin: superadmin@skillforge.com / super123")
        print("   - Admin: admin@skillforge.com / admin123")
        print("   - Mentor: mentor@skillforge.com / mentor123")
        print("   - User: user@skillforge.com / user123")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_users()
