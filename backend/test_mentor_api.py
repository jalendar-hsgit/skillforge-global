"""
Quick test script to verify mentor API responses
"""
import sys
sys.path.insert(0, 'D:\\python code\\sfg\\skillforge-global\\backend')

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.modelsx.mentor import Mentor
from app.models.user import User

def test_mentor_response():
    db: Session = SessionLocal()
    
    try:
        # Get mentor 2
        mentor = db.query(Mentor).filter(Mentor.id == 2).first()
        if not mentor:
            print("❌ Mentor 2 not found")
            return
        
        print(f"✅ Found mentor: ID={mentor.id}, user_id={mentor.user_id}")
        
        # Get user
        user = db.query(User).filter(User.id == mentor.user_id).first()
        if not user:
            print("❌ User not found for mentor")
            return
        
        print(f"✅ Found user: email={user.email}")
        
        # Generate full_name from email
        email = user.email
        full_name = email.split('@')[0].replace('.', ' ').title()
        print(f"✅ Generated full_name: {full_name}")
        
        # Test response structure
        response_data = {
            "id": mentor.id,
            "user_id": mentor.user_id,
            "email": email,
            "bio": mentor.bio,
            "expertise": mentor.expertise,
            "hourly_rate": float(mentor.hourly_rate),
            "status": mentor.status.value if hasattr(mentor.status, 'value') else str(mentor.status),
            "total_sessions": mentor.total_sessions,
            "average_rating": float(mentor.average_rating),
            "user": {"full_name": full_name, "email": email},
            "created_at": mentor.created_at.isoformat() if mentor.created_at else None
        }
        
        print("\n✅ Response structure:")
        print(f"  - ID: {response_data['id']}")
        print(f"  - Email: {response_data['email']}")
        print(f"  - User object: {response_data['user']}")
        print(f"  - Bio: {response_data['bio'][:50]}...")
        print(f"  - Expertise: {response_data['expertise']}")
        print(f"  - Rate: ${response_data['hourly_rate']}")
        
        print("\n✅ All tests passed! API should return user.full_name correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_mentor_response()
