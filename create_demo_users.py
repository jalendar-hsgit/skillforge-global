#!/usr/bin/env python3
"""
Create demo users in database for SkillForge Global
Email: prasad.r1342@gmail.com
Username: prasadreddy147
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from sqlalchemy.orm import Session, sessionmaker
    from app.main import Base, engine
    from app.models.user import User, UserRole
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("=" * 70)
    print("  CREATING DEMO USERS FOR SKILLFORGE GLOBAL")
    print("  Email: prasad.r1342@gmail.com")
    print("  Username: prasadreddy147")
    print("=" * 70)
    print()
    
    # Demo users data
    demo_users_data = [
        {
            "email": "prasad.r1342@gmail.com",
            "password": "Prasad@123456",
            "name": "Prasad Reddy",
            "role": UserRole.SUPERADMIN,
            "bio": "Founder & Admin",
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "admin@skillforge.com",
            "password": "Admin@123456",
            "name": "Admin User",
            "role": UserRole.ADMIN,
            "bio": "System Administrator",
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "mentor@skillforge.com",
            "password": "Mentor@123456",
            "name": "Expert Mentor",
            "role": UserRole.MENTOR,
            "bio": "Python & Web Development Specialist",
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "student@skillforge.com",
            "password": "Student@123456",
            "name": "Student User",
            "role": UserRole.USER,
            "bio": "Learning Full Stack Development",
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "john.doe@skillforge.com",
            "password": "John@123456",
            "name": "John Doe",
            "role": UserRole.USER,
            "bio": "Web Developer & Tech Enthusiast",
            "is_verified": True,
            "is_active": True,
        },
    ]
    
    # Create users
    created_count = 0
    for user_data in demo_users_data:
        # Check if exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing:
            print(f"⏭️  Skip: {user_data['email']} (already exists)")
            continue
        
        # Create user
        user = User(
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            bio=user_data["bio"],
            is_verified=user_data["is_verified"],
            is_active=user_data["is_active"],
        )
        user.set_password(user_data["password"])
        
        db.add(user)
        db.flush()
        
        created_count += 1
        print(f"✅ Created: {user_data['name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Role: {user_data['role'].value}")
        print()
    
    # Commit
    db.commit()
    
    print("=" * 70)
    print(f"✅ SUCCESSFULLY CREATED {created_count} DEMO USERS")
    print("=" * 70)
    print()
    
    # Display credentials table
    print("📋 DEMO USER CREDENTIALS:")
    print()
    print(f"{'Email':<35} | {'Password':<20} | {'Role':<12}")
    print("-" * 70)
    for user_data in demo_users_data:
        print(f"{user_data['email']:<35} | {user_data['password']:<20} | {user_data['role'].value:<12}")
    
    print()
    print("=" * 70)
    print("🚀 READY FOR DEPLOYMENT!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Follow COMPLETE_DEPLOYMENT_CHECKLIST.md")
    print("  2. Create Vercel account: https://vercel.com/signup")
    print("  3. Create Railway account: https://railway.app/login")
    print("  4. Add GitLab CI/CD variables")
    print("  5. Push to main: git push origin main")
    print()
    print("Your app will be live at:")
    print("  🌍 Frontend: https://prasadreddy147.vercel.app")
    print("  🔧 Backend: https://prasadreddy147-backend.up.railway.app")
    print()
    
    db.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
