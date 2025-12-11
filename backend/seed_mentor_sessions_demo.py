"""Seed demo mentor sessions if table is empty (non-destructive)."""
from app.core.db import SessionLocal
from app.models.user import User
from app.modelsx.mentor import MentorSession, SessionStatus
from datetime import datetime, timedelta

def seed_mentor_sessions():
    db = SessionLocal()
    try:
        count = db.query(MentorSession).count()
        if count > 0:
            print(f"✓ Mentor sessions table already has {count} rows, skipping seed")
            return
        
        print("⚡ Mentor sessions table is empty, seeding demo sessions...")
        
        mentor_user = db.query(User).filter(User.email == 'mentor@skillforge.com').first()
        student_user = db.query(User).filter(User.email == 'user@skillforge.com').first()
        
        if not mentor_user or not student_user:
            print("⚠ Mentor or student user not found, skipping session seed")
            return
        
        # Check if mentor exists in mentors table
        from app.modelsx.mentor import Mentor
        mentor = db.query(Mentor).filter(Mentor.user_id == mentor_user.id).first()
        
        if not mentor:
            print("⚠ Mentor profile not found for mentor user, skipping session seed")
            return
        
        sessions_data = [
            {
                "mentor_id": mentor.id,
                "student_id": student_user.id,
                "topic": "Career Guidance Session",
                "description": "Discussion on career growth in tech",
                "scheduled_at": datetime.now() + timedelta(days=2),
                "duration_minutes": 60,
                "status": SessionStatus.PENDING,
                "meeting_url": "https://zoom.us/meeting/123456"
            },
            {
                "mentor_id": mentor.id,
                "student_id": student_user.id,
                "topic": "Resume Review",
                "description": "Detailed review of resume and suggestions",
                "scheduled_at": datetime.now() + timedelta(days=5),
                "duration_minutes": 30,
                "status": SessionStatus.PENDING,
                "meeting_url": "https://zoom.us/meeting/789012"
            }
        ]
        
        for session_data in sessions_data:
            session = MentorSession(**session_data)
            db.add(session)
        
        db.commit()
        print(f"✓ Created {len(sessions_data)} demo mentor sessions")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_mentor_sessions()
