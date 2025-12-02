"""
Create test mentor data and verify mentor portal endpoints
"""
import sys
sys.path.insert(0, 'D:\\python code\\sfg\\skillforge-global\\backend')

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorStatus, MentorSession, SessionStatus, MentorReview
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

def create_test_mentor():
    """Create a test mentor with sessions and reviews"""
    db: Session = SessionLocal()
    
    try:
        # Check if test user exists
        test_email = "mentor@test.com"
        user = db.query(User).filter(User.email == test_email).first()
        
        if not user:
            print(f"Creating test user: {test_email}")
            user = User(
                email=test_email,
                password_hash=get_password_hash("password123"),
                role=UserRole.USER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f" Created user with ID: {user.id}")
        else:
            print(f" User already exists with ID: {user.id}")
        
        # Check if mentor profile exists
        mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
        
        if not mentor:
            print("Creating mentor profile...")
            mentor = Mentor(
                user_id=user.id,
                bio="Experienced full-stack developer with 10+ years in web development. Specializing in Python, JavaScript, and cloud architecture.",
                expertise="Python,FastAPI,React,Next.js,AWS,Docker",
                hourly_rate=75.00,
                status=MentorStatus.APPROVED,
                total_sessions=0,
                total_earnings=0.0,
                average_rating=0.0
            )
            db.add(mentor)
            db.commit()
            db.refresh(mentor)
            print(f" Created mentor with ID: {mentor.id}")
        else:
            print(f" Mentor already exists with ID: {mentor.id}")
            # Update to approved if not
            if mentor.status != MentorStatus.APPROVED:
                mentor.status = MentorStatus.APPROVED
                db.commit()
                print(" Updated mentor status to APPROVED")
        
        # Create test students
        students = []
        for i in range(3):
            student_email = f"student{i+1}@test.com"
            student = db.query(User).filter(User.email == student_email).first()
            
            if not student:
                student = User(
                    email=student_email,
                    password_hash=get_password_hash("password123"),
                    role=UserRole.USER
                )
                db.add(student)
                db.commit()
                db.refresh(student)
                print(f" Created student: {student_email} (ID: {student.id})")
            students.append(student)
        
        # Create test sessions
        now = datetime.utcnow()
        session_count = db.query(MentorSession).filter(MentorSession.mentor_id == mentor.id).count()
        
        if session_count == 0:
            print("\nCreating test sessions...")
            
            # Completed sessions (past)
            for i in range(5):
                student = random.choice(students)
                session = MentorSession(
                    mentor_id=mentor.id,
                    student_id=student.id,
                    topic=f"Learning {random.choice(['Python Basics', 'React Hooks', 'API Design', 'Database Optimization', 'System Architecture'])}",
                    description="1-on-1 mentoring session",
                    scheduled_at=now - timedelta(days=random.randint(10, 60)),
                    duration_minutes=60,
                    price=75.00,
                    payment_status="paid",
                    status=SessionStatus.COMPLETED,
                    completed_at=now - timedelta(days=random.randint(10, 60))
                )
                db.add(session)
            
            # Confirmed sessions (upcoming)
            for i in range(2):
                student = random.choice(students)
                session = MentorSession(
                    mentor_id=mentor.id,
                    student_id=student.id,
                    topic=f"Advanced {random.choice(['TypeScript', 'Cloud Deployment', 'Performance Tuning'])}",
                    description="Scheduled mentoring session",
                    scheduled_at=now + timedelta(days=random.randint(1, 7)),
                    duration_minutes=60,
                    price=75.00,
                    payment_status="paid",
                    status=SessionStatus.CONFIRMED,
                    meeting_url="https://zoom.us/j/test123"
                )
                db.add(session)
            
            # Pending sessions
            for i in range(2):
                student = random.choice(students)
                session = MentorSession(
                    mentor_id=mentor.id,
                    student_id=student.id,
                    topic="New Topic Discussion",
                    description="Awaiting confirmation",
                    scheduled_at=now + timedelta(days=random.randint(8, 14)),
                    duration_minutes=60,
                    price=75.00,
                    payment_status="pending",
                    status=SessionStatus.PENDING
                )
                db.add(session)
            
            db.commit()
            print(f" Created 9 test sessions")
        else:
            print(f" {session_count} sessions already exist")
        
        # Create test reviews
        review_count = db.query(MentorReview).filter(MentorReview.mentor_id == mentor.id).count()
        
        if review_count == 0:
            print("\nCreating test reviews...")
            
            completed_sessions = db.query(MentorSession).filter(
                MentorSession.mentor_id == mentor.id,
                MentorSession.status == SessionStatus.COMPLETED
            ).all()
            
            reviews_data = [
                (5, "Excellent mentor! Very knowledgeable and patient."),
                (5, "Helped me understand complex concepts easily."),
                (4, "Great session, learned a lot about best practices."),
                (5, "Highly recommend! Clear explanations and practical examples."),
                (4, "Very helpful and responsive to questions.")
            ]
            
            for i, (rating, comment) in enumerate(reviews_data[:len(completed_sessions)]):
                session = completed_sessions[i]
                review = MentorReview(
                    mentor_id=mentor.id,
                    student_id=session.student_id,
                    session_id=session.id,
                    rating=rating,
                    review_text=comment
                )
                db.add(review)
            
            db.commit()
            print(f" Created {len(reviews_data)} test reviews")
        else:
            print(f" {review_count} reviews already exist")
        
        # Update mentor stats
        total_sessions = db.query(MentorSession).filter(MentorSession.mentor_id == mentor.id).count()
        completed = db.query(MentorSession).filter(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        ).all()
        
        total_earnings = sum(s.price for s in completed if s.price)
        
        avg_rating_result = db.query(MentorReview).filter(MentorReview.mentor_id == mentor.id).all()
        avg_rating = sum(r.rating for r in avg_rating_result) / len(avg_rating_result) if avg_rating_result else 0.0
        
        mentor.total_sessions = total_sessions
        mentor.total_earnings = total_earnings
        mentor.average_rating = avg_rating
        db.commit()
        
        print(f"\n{'='*60}")
        print(f" TEST DATA CREATED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Mentor Email: {test_email}")
        print(f"Password: password123")
        print(f"Mentor ID: {mentor.id}")
        print(f"Status: {mentor.status}")
        print(f"Total Sessions: {mentor.total_sessions}")
        print(f"Total Earnings: ${mentor.total_earnings:.2f}")
        print(f"Average Rating: {mentor.average_rating:.1f}")
        print(f"{'='*60}")
        print(f"\n You can now:")
        print(f"1. Login with: mentor@test.com / password123")
        print(f"2. Visit: http://localhost:3000/mentors/dashboard")
        print(f"3. Run: python backend/test_mentor_api.py")
        print(f"{'='*60}\n")
        
        return mentor, user
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_mentor()
