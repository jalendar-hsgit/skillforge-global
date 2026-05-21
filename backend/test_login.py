#!/usr/bin/env python3
"""
Test login functionality directly
"""
from app.core.db import SessionLocal
from app.models.user import User
from app.core.security import verify_password, create_access_token

def test_login(email: str, password: str):
    """Test login with given credentials"""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"✅ User found: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Role: {user.role}")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            print(f"❌ Password verification failed")
            return False
        
        print(f"✅ Password verified")
        
        # Create token
        token = create_access_token(user.id)
        print(f"✅ Token created: {token[:50]}...")
        
        return True
        
    finally:
        db.close()

if __name__ == "__main__":
    print("="*70)
    print("Testing Login Functionality")
    print("="*70)
    print()
    
    # Test the new superadmin
    print("Test 1: test.super@skillforge.com")
    print("-" * 70)
    success = test_login("test.super@skillforge.com", "123456789")
    print()
    
    if success:
        print("🎉 LOGIN TEST PASSED!")
    else:
        print("❌ LOGIN TEST FAILED!")
    
    print()
    print("="*70)
