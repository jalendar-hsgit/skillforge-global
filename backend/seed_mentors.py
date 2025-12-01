"""
Seed script for mentors module demo data.
Creates test users, mentor profiles, availability, sessions, and reviews.
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.db import SessionLocal, engine, Base
from app.models.user import User
from app.modelsx.mentor import (
    Mentor, MentorSession, MentorAvailability, 
    MentorReview, MentorStatus, SessionStatus
)
# import models so tables are registered on Base
from app.models import User, Progress as LegacyProgress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress, coins
from app.modelsx.coins import CoinLedger
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
from app.modelsx.mentor import (
    Mentor, MentorSession, MentorAvailability, 
    MentorReview, MentorStatus, SessionStatus
)
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, Achievement, ResumeTemplate, AIProjectTemplate, ResumeAnalytics, ATSReport
from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
from app.modelsx.job_application import JobApplication as JobApplicationTracker
from app.modelsx.order import Order, Coupon, CartItem

from app.core.security import get_password_hash


def seed_mentors():
    """Seed mentor demo data"""
    db = SessionLocal()
    
    try:
        print("Starting mentor module seed...")
        
        # Create test users
        print("\n1. Creating test users...")
        
        # Students
        student1 = db.query(User).filter(User.email == "student1@test.com").first()
        if not student1:
            student1 = User(
                email="student1@test.com",
                password_hash=get_password_hash("password123")
            )
            db.add(student1)
            db.flush()
            print(f"  + Created student: {student1.email}")
        else:
            print(f"  + Found existing student: {student1.email}")
        
        student2 = db.query(User).filter(User.email == "student2@test.com").first()
        if not student2:
            student2 = User(
                email="student2@test.com",
                password_hash=get_password_hash("password123")
            )
            db.add(student2)
            db.flush()
            print(f"  + Created student: {student2.email}")
        else:
            print(f"  + Found existing student: {student2.email}")
        
        # Mentor users
        mentor_user1 = db.query(User).filter(User.email == "mentor1@test.com").first()
        if not mentor_user1:
            mentor_user1 = User(
                email="mentor1@test.com",
                password_hash=get_password_hash("password123")
            )
            db.add(mentor_user1)
            db.flush()
            print(f"  + Created mentor user: {mentor_user1.email}")
        else:
            print(f"  + Found existing mentor user: {mentor_user1.email}")
        
        mentor_user2 = db.query(User).filter(User.email == "mentor2@test.com").first()
        if not mentor_user2:
            mentor_user2 = User(
                email="mentor2@test.com",
                password_hash=get_password_hash("password123")
            )
            db.add(mentor_user2)
            db.flush()
            print(f"  + Created mentor user: {mentor_user2.email}")
        else:
            print(f"  + Found existing mentor user: {mentor_user2.email}")
        
        mentor_user3 = db.query(User).filter(User.email == "mentor3@test.com").first()
        if not mentor_user3:
            mentor_user3 = User(
                email="mentor3@test.com",
                password_hash=get_password_hash("password123")
            )
            db.add(mentor_user3)
            db.flush()
            print(f"  + Created mentor user: {mentor_user3.email}")
        else:
            print(f"  + Found existing mentor user: {mentor_user3.email}")
        
        db.commit()
        
        # Create mentor profiles
        print("\n2. Creating mentor profiles...")
        
        mentor1 = db.query(Mentor).filter(Mentor.user_id == mentor_user1.id).first()
        if not mentor1:
            mentor1 = Mentor(
                user_id=mentor_user1.id,
                bio="Senior Python developer with 8+ years of experience in AI/ML. I specialize in teaching data science, machine learning, and backend development. Passionate about helping students build real-world projects.",
                expertise="python-ai,data-science,backend",
                hourly_rate=75.0,
                status=MentorStatus.APPROVED,
                approved_at=datetime.utcnow() - timedelta(days=30),
                total_sessions=24,
                average_rating=4.8,
                total_earnings=1800.0
            )
            db.add(mentor1)
            db.flush()
            print(f"  + Created mentor profile: {mentor_user1.email}")
        else:
            print(f"  + Found existing mentor: {mentor_user1.email}")
        
        mentor2 = db.query(Mentor).filter(Mentor.user_id == mentor_user2.id).first()
        if not mentor2:
            mentor2 = Mentor(
                user_id=mentor_user2.id,
                bio="Full-stack engineer specializing in React, Node.js, and cloud architecture. I've built 20+ production apps and love teaching web development fundamentals and advanced patterns.",
                expertise="fullstack,react,nodejs,cloud",
                hourly_rate=85.0,
                status=MentorStatus.APPROVED,
                approved_at=datetime.utcnow() - timedelta(days=45),
                total_sessions=18,
                average_rating=4.9,
                total_earnings=1530.0
            )
            db.add(mentor2)
            db.flush()
            print(f"  + Created mentor profile: {mentor_user2.email}")
        else:
            print(f"  + Found existing mentor: {mentor_user2.email}")
        
        mentor3 = db.query(Mentor).filter(Mentor.user_id == mentor_user3.id).first()
        if not mentor3:
            mentor3 = Mentor(
                user_id=mentor_user3.id,
                bio="DevOps engineer and cybersecurity specialist. I help students master Docker, Kubernetes, CI/CD pipelines, and security best practices. Available for project reviews and career guidance.",
                expertise="devops,security,cloud,docker",
                hourly_rate=90.0,
                status=MentorStatus.APPROVED,
                approved_at=datetime.utcnow() - timedelta(days=60),
                total_sessions=15,
                average_rating=4.7,
                total_earnings=1350.0
            )
            db.add(mentor3)
            db.flush()
            print(f"  + Created mentor profile: {mentor_user3.email}")
        else:
            print(f"  + Found existing mentor: {mentor_user3.email}")
        
        db.commit()
        
        # Create availability slots
        print("\n3. Creating availability slots...")
        
        # Mentor 1 - Recurring weekday mornings
        availability_count = db.query(MentorAvailability).filter(
            MentorAvailability.mentor_id == mentor1.id
        ).count()
        
        if availability_count == 0:
            # Monday to Friday 9am-12pm
            for day in range(5):  # 0=Monday, 4=Friday
                slot = MentorAvailability(
                    mentor_id=mentor1.id,
                    day_of_week=day,
                    start_time="09:00",
                    end_time="12:00"
                )
                db.add(slot)
            
            # Specific date slots for next week
            today = datetime.utcnow()
            for offset in [7, 9, 11]:  # Next Mon, Wed, Fri
                specific_date = today + timedelta(days=offset)
                slot = MentorAvailability(
                    mentor_id=mentor1.id,
                    date=specific_date,
                    start_time="14:00",
                    end_time="17:00"
                )
                db.add(slot)
            
            print(f"  + Created availability for mentor1@test.com")
        else:
            print(f"  + Found existing availability for mentor1@test.com")
        
        # Mentor 2 - Afternoon and evening slots
        availability_count2 = db.query(MentorAvailability).filter(
            MentorAvailability.mentor_id == mentor2.id
        ).count()
        
        if availability_count2 == 0:
            # Tuesday, Thursday 2pm-6pm
            for day in [1, 3]:
                slot = MentorAvailability(
                    mentor_id=mentor2.id,
                    day_of_week=day,
                    start_time="14:00",
                    end_time="18:00"
                )
                db.add(slot)
            
            # Saturday mornings
            slot = MentorAvailability(
                mentor_id=mentor2.id,
                day_of_week=5,
                start_time="10:00",
                end_time="13:00"
            )
            db.add(slot)
            
            print(f"  + Created availability for mentor2@test.com")
        else:
            print(f"  + Found existing availability for mentor2@test.com")
        
        # Mentor 3 - Flexible schedule
        availability_count3 = db.query(MentorAvailability).filter(
            MentorAvailability.mentor_id == mentor3.id
        ).count()
        
        if availability_count3 == 0:
            # Wednesday and Friday afternoons
            for day in [2, 4]:
                slot = MentorAvailability(
                    mentor_id=mentor3.id,
                    day_of_week=day,
                    start_time="13:00",
                    end_time="17:00"
                )
                db.add(slot)
            
            print(f"  + Created availability for mentor3@test.com")
        else:
            print(f"  + Found existing availability for mentor3@test.com")
        
        db.commit()
        
        # Create sample sessions
        print("\n4. Creating sample sessions...")
        
        session_count = db.query(MentorSession).count()
        
        if session_count == 0:
            # Past completed sessions
            session1 = MentorSession(
                mentor_id=mentor1.id,
                student_id=student1.id,
                topic="Python Data Analysis with Pandas",
                description="Help with data cleaning and visualization for final project",
                scheduled_at=datetime.utcnow() - timedelta(days=5),
                duration_minutes=60,
                status=SessionStatus.COMPLETED,
                meeting_url="https://meet.google.com/abc-defg-hij",
                price=75.0,
                payment_status="captured",
                completed_at=datetime.utcnow() - timedelta(days=5)
            )
            db.add(session1)
            
            session2 = MentorSession(
                mentor_id=mentor2.id,
                student_id=student2.id,
                topic="React Hooks Deep Dive",
                description="Understanding useEffect and custom hooks",
                scheduled_at=datetime.utcnow() - timedelta(days=3),
                duration_minutes=60,
                status=SessionStatus.COMPLETED,
                meeting_url="https://zoom.us/j/123456789",
                price=85.0,
                payment_status="captured",
                completed_at=datetime.utcnow() - timedelta(days=3)
            )
            db.add(session2)
            
            # Upcoming confirmed session
            session3 = MentorSession(
                mentor_id=mentor1.id,
                student_id=student2.id,
                topic="Machine Learning Model Deployment",
                description="Deploying ML models to production with FastAPI",
                scheduled_at=datetime.utcnow() + timedelta(days=2),
                duration_minutes=90,
                status=SessionStatus.CONFIRMED,
                meeting_url="https://meet.google.com/xyz-uvwx-yz",
                price=112.5,
                payment_status="paid"
            )
            db.add(session3)
            
            # Pending session (needs confirmation)
            session4 = MentorSession(
                mentor_id=mentor3.id,
                student_id=student1.id,
                topic="Docker & Kubernetes Basics",
                description="Getting started with containerization",
                scheduled_at=datetime.utcnow() + timedelta(days=4),
                duration_minutes=60,
                status=SessionStatus.PENDING,
                price=90.0,
                payment_status="paid"
            )
            db.add(session4)
            
            # Free session
            session5 = MentorSession(
                mentor_id=mentor2.id,
                student_id=student1.id,
                topic="Career Guidance - Frontend Development",
                description="Career path discussion and portfolio review",
                scheduled_at=datetime.utcnow() + timedelta(days=7),
                duration_minutes=30,
                status=SessionStatus.CONFIRMED,
                meeting_url="https://zoom.us/j/987654321",
                price=0.0,
                payment_status="paid"
            )
            db.add(session5)
            
            db.flush()
            print(f"  + Created 5 sample sessions")
            
            # Create reviews for completed sessions
            print("\n5. Creating reviews...")
            
            review1 = MentorReview(
                session_id=session1.id,
                mentor_id=mentor1.id,
                student_id=student1.id,
                rating=5,
                review_text="Sarah was incredibly helpful! She explained complex pandas operations clearly and helped me debug my data pipeline. Highly recommend!"
            )
            db.add(review1)
            
            review2 = MentorReview(
                session_id=session2.id,
                mentor_id=mentor2.id,
                student_id=student2.id,
                rating=5,
                review_text="David really knows his stuff. The session on React hooks was exactly what I needed. Great examples and patient explanations."
            )
            db.add(review2)
            
            print(f"  + Created 2 reviews")
        else:
            print(f"  + Created {session_count} existing sessions")
        
        db.commit()
        
        # Summary
        print("\n" + "="*60)
        print("SEED COMPLETE - Demo Data Summary")
        print("="*60)
        
        total_users = db.query(User).count()
        total_mentors = db.query(Mentor).filter(Mentor.status == MentorStatus.APPROVED).count()
        total_sessions = db.query(MentorSession).count()
        total_reviews = db.query(MentorReview).count()
        total_availability = db.query(MentorAvailability).count()
        
        print(f"\nStatistics:")
        print(f"  - Total Users: {total_users}")
        print(f"  - Approved Mentors: {total_mentors}")
        print(f"  - Total Sessions: {total_sessions}")
        print(f"  - Reviews: {total_reviews}")
        print(f"  - Availability Slots: {total_availability}")
        
        print(f"\nTest Accounts:")
        print(f"  Students:")
        print(f"    - student1@test.com / password123 (Alice Johnson)")
        print(f"    - student2@test.com / password123 (Bob Smith)")
        print(f"\n  Mentors:")
        print(f"    - mentor1@test.com / password123 (Sarah Chen - Python/AI)")
        print(f"    - mentor2@test.com / password123 (David Kumar - Fullstack)")
        print(f"    - mentor3@test.com / password123 (Emma Rodriguez - DevOps)")
        
        print(f"\nTest URLs:")
        print(f"  - Browse Mentors: http://localhost:3000/mentors")
        print(f"  - Mentor Dashboard: http://localhost:3000/mentors/dashboard")
        print(f"  - Book Session: http://localhost:3000/mentors/[id]/book")
        print(f"  - Admin Panel: http://localhost:3000/admin/mentors")
        
        print(f"\n[SUCCESS] Seed completed successfully!\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Mentors Module Demo Data Seeder")
    print("=" * 60)
    seed_mentors()
