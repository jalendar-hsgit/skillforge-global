"""
Create or promote a user to admin/superadmin role.
Usage:
    python create_admin.py <email> [role]
    
Examples:
    python create_admin.py admin@example.com superadmin
    python create_admin.py support@example.com admin
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.db import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole


def create_or_promote_admin(email: str, role: str = "admin"):
    """Create a new admin user or promote existing user to admin"""
    
    db = SessionLocal()
    
    try:
        # Validate role
        try:
            user_role = UserRole(role)
        except ValueError:
            print(f"❌ Invalid role: {role}")
            print(f"Valid roles: {', '.join([r.value for r in UserRole])}")
            return
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Promote existing user
            old_role = user.role
            user.role = user_role
            db.commit()
            print(f"✅ User {email} promoted from {old_role} to {user_role}")
        else:
            # Create new user
            print(f"User {email} not found. Creating new user...")
            password = input("Enter password for new admin: ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters")
                return
            
            user = User(
                email=email,
                password_hash=get_password_hash(password),
                role=user_role
            )
            db.add(user)
            db.commit()
            print(f"✅ New {user_role} user created: {email}")
        
        # Show user info
        print(f"\nUser Details:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Created: {user.created_at}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py <email> [role]")
        print("Roles: user, mentor, admin, superadmin (default: admin)")
        sys.exit(1)
    
    email = sys.argv[1]
    role = sys.argv[2] if len(sys.argv) > 2 else "admin"
    
    create_or_promote_admin(email, role)
