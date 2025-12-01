"""
Interactive First-Time Setup for SkillForge Admin System
This script helps you create your organization's first superadmin account.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.db import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
import getpass

def print_banner():
    print("="*70)
    print(" SkillForge Global - First-Time Admin Setup")
    print("="*70)
    print()
    print("This wizard will create your organization's first SUPERADMIN account.")
    print("You only need to run this once during initial setup.")
    print()
    print("After creating the superadmin, you can:")
    print("  • Login to the admin panel")
    print("  • Promote regular users to admin/superadmin")
    print("  • Manage all users from the web interface")
    print()
    print("="*70)
    print()

def check_existing_superadmins(db):
    """Check if any superadmins already exist"""
    count = db.query(User).filter(User.role == UserRole.SUPERADMIN).count()
    return count

def create_first_superadmin():
    """Interactive superadmin creation"""
    print_banner()
    
    db = SessionLocal()
    
    try:
        # Check if superadmins already exist
        existing_count = check_existing_superadmins(db)
        
        if existing_count > 0:
            print(f"⚠️  WARNING: {existing_count} superadmin(s) already exist in the system.")
            print()
            
            # List existing superadmins
            superadmins = db.query(User).filter(User.role == UserRole.SUPERADMIN).all()
            print("Existing superadmin accounts:")
            for sa in superadmins:
                print(f"  • {sa.email} (ID: {sa.id}, Created: {sa.created_at})")
            print()
            
            response = input("Do you want to create another superadmin anyway? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("\n✓ Setup cancelled. Use existing superadmin to manage users.")
                return
            print()
        
        # Get email
        while True:
            email = input("Enter superadmin email address: ").strip()
            if not email or '@' not in email:
                print("❌ Please enter a valid email address")
                continue
            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"❌ User with email {email} already exists (Role: {existing_user.role})")
                response = input("Would you like to promote this user to superadmin? (yes/no): ").strip().lower()
                if response in ['yes', 'y']:
                    existing_user.role = UserRole.SUPERADMIN
                    db.commit()
                    print(f"\n✅ User {email} promoted to superadmin!")
                    print(f"   ID: {existing_user.id}")
                    print(f"   Email: {existing_user.email}")
                    print(f"   Role: {existing_user.role}")
                    print(f"\n✓ You can now login at: http://localhost:3000/login")
                    return
                continue
            break
        
        # Get password
        while True:
            password = getpass.getpass("Enter password (min 8 characters, hidden): ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters")
                continue
            
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("❌ Passwords do not match")
                continue
            break
        
        # Get optional full name
        full_name = input("Enter full name (optional, press Enter to skip): ").strip() or None
        
        print()
        print("Creating superadmin account...")
        
        # Create user
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.SUPERADMIN
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print()
        print("="*70)
        print("✅ SUPERADMIN ACCOUNT CREATED SUCCESSFULLY!")
        print("="*70)
        print()
        print(f"Account Details:")
        print(f"  ID:      {user.id}")
        print(f"  Email:   {user.email}")
        print(f"  Role:    {user.role}")
        print(f"  Created: {user.created_at}")
        print()
        print("="*70)
        print()
        print("Next Steps:")
        print()
        print("1. Start the backend server:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
        print()
        print("2. Start the frontend:")
        print("   npm run dev")
        print()
        print("3. Login at:")
        print("   http://localhost:3000/login")
        print()
        print("4. Access admin panel:")
        print("   http://localhost:3000/admin")
        print()
        print("5. To promote other users to admin:")
        print("   • Have them signup normally at /signup")
        print("   • Login to admin panel → Users")
        print("   • Find their account and change role")
        print()
        print("="*70)
        print()
        print("🔐 Security Reminder:")
        print("  • Keep this password secure (use a password manager)")
        print("  • Only promote trusted users to admin/superadmin")
        print("  • Monitor audit logs regularly (/admin/logs)")
        print("  • All admin actions are logged for security")
        print()
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        create_first_superadmin()
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
