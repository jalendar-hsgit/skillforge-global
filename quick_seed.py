#!/usr/bin/env python3
"""
Seed demo data directly - bypasses app startup issues
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.db import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Import all models first
from app.models import *
from app.modelsx import *

def seed():
    db = SessionLocal()
    
    # Create basic admin and users
    admin_users = [
        {
            "email": "superadmin@skillforge.com",
            "password": "password123",
            "name": "Super Admin",
            "role": UserRole.SUPERADMIN
        },
        {
            "email": "john.doe@example.com",
            "password": "password123",
            "name": "John Doe",
            "role": UserRole.USER
        }
    ]
    
    for user_data in admin_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"]
            )
            db.add(user)
            print(f"✓ Created {user_data['role']} user: {user_data['email']}")
    
    db.commit()
    db.close()
    print("\n✅ Demo data seeded successfully!")

if __name__ == "__main__":
    seed()
