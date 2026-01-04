#!/usr/bin/env python3
"""
Comprehensive Mentor Module Seeder
==================================
Seeds realistic mentor data with sessions, reviews, and availability
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.insert(0, '.')

from app.core.db import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.modelsx.mentor import (
    Mentor, MentorSession, MentorAvailability, MentorReview,
    MentorMessage, MentorStatus, SessionStatus
)


def seed_complete_mentors():
    """Seed comprehensive mentor data"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("MENTOR MODULE - COMPREHENSIVE SEEDING")
        print("="*80)
        
        # ============================================================
        # PART 1: CREATE MENTOR USERS
        # ============================================================
        print("\n[1/7] Creating mentor users...")
        
        mentor_data = [
            {
                "email": "mentor.python@test.com",
                "name": "Alex Johnson",
                "expertise": "python-ai,data-science,backend",
                "bio": "Senior Python developer with 10+ years in AI/ML. I specialize in teaching advanced Python, machine learning, and backend development. Passionate about helping developers build scalable systems.",
                "rate": 85.0,
            },
            {
                "email": "mentor.web@test.com",
                "name": "Sarah Chen",
                "expertise": "web-dev,frontend,react",
                "bio": "Full-stack developer with 8 years of experience. Expert in React, Next.js, and modern web development. Love mentoring junior developers and helping them master frontend skills.",
                "rate": 75.0,
            },
            {
                "email": "mentor.cloud@test.com",
                "name": "James Wilson",
                "expertise": "cloud,aws,devops",
                "bio": "AWS Solutions Architect with 12 years of cloud experience. Specialize in cloud infrastructure, DevOps practices, and system design. Dedicated to teaching best practices.",
                "rate": 95.0,
            },
            {
                "email": "mentor.mobile@test.com",
                "name": "Emma Rodriguez",
                "expertise": "mobile,react-native,ios",
                "bio": "Mobile developer with 6 years experience in iOS and React Native. Focus on teaching mobile development best practices and app architecture.",
                "rate": 65.0,
            },
            {
                "email": "mentor.data@test.com",
                "name": "David Kumar",
                "expertise": "data-science,machine-learning,python-ai",
                "bio": "Data scientist with PhD in ML. 8+ years teaching others data science and ML. Expert in Python, TensorFlow, and statistical analysis.",
                "rate": 90.0,
            },
        ]
        
        mentors = []
        mentor_users = []
        
        for data in mentor_data:
            # Create user
            user = db.query(User).filter(User.email == data["email"]).first()
            if not user:
                user = User(
                    email=data["email"],
                    password_hash=get_password_hash("password123"),
                    role=UserRole.MENTOR
                )
                db.add(user)
                db.flush()
                print(f"  ✓ Created user: {data['email']}")
            else:
                print(f"  ~ Found existing user: {data['email']}")
            
            mentor_users.append((user, data))
        
        db.commit()
        
        # ============================================================
        # PART 2: CREATE MENTOR PROFILES
        # ============================================================
        print("\n[2/7] Creating mentor profiles...")
        
        for user, data in mentor_users:
            mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
            if not mentor:
                mentor = Mentor(
                    user_id=user.id,
                    bio=data["bio"],
                    expertise=data["expertise"],
                    hourly_rate=data["rate"],
                    status=MentorStatus.APPROVED,
                    approved_at=datetime.utcnow() - timedelta(days=30),
                    total_sessions=0,
                    average_rating=0.0,
                    total_earnings=0.0,
                )
                db.add(mentor)
                db.flush()
                print(f"  ✓ Created mentor profile: {data['name']} (${data['rate']}/hr)")
            else:
                print(f"  ~ Found existing mentor: {data['name']}")
            
            mentors.append((mentor, data))
        
        db.commit()
        
        # ============================================================
        # PART 3: CREATE AVAILABILITY SLOTS
        # ============================================================
        print("\n[3/7] Creating availability slots...")
        
        for mentor, data in mentors:
            # Check if already has availability
            existing_slots = db.query(MentorAvailability).filter(
                MentorAvailability.mentor_id == mentor.id
            ).count()
            
            if existing_slots == 0:
                # Create weekly slots (Mon, Wed, Fri, Sat)
                slots = [
                    (0, "14:00", "16:00"),  # Monday 2-4pm
                    (2, "14:00", "16:00"),  # Wednesday 2-4pm
                    (4, "10:00", "12:00"),  # Friday 10am-12pm
                    (5, "15:00", "17:00"),  # Saturday 3-5pm
                ]
                
                for day_of_week, start, end in slots:
                    slot = MentorAvailability(
                        mentor_id=mentor.id,
                        day_of_week=day_of_week,
                        start_time=start,
                        end_time=end,
                        is_available=True,
                        is_booked=False,
                        timezone="UTC"
                    )
                    db.add(slot)
                
                db.flush()
                print(f"  ✓ Created availability slots for {data['name']}")
            else:
                print(f"  ~ Found existing slots for {data['name']}")
        
        db.commit()
        
        # ============================================================
        # PART 4: CREATE TEST STUDENT USERS
        # ============================================================
        print("\n[4/7] Creating test student users...")
        
        student_emails = [
            "student.alice@test.com",
            "student.bob@test.com",
            "student.charlie@test.com",
        ]
        
        students = []
        for email in student_emails:
            student = db.query(User).filter(User.email == email).first()
            if not student:
                student = User(
                    email=email,
                    password_hash=get_password_hash("password123"),
                    role=UserRole.USER
                )
                db.add(student)
                db.flush()
                print(f"  ✓ Created student: {email}")
            else:
                print(f"  ~ Found existing student: {email}")
            
            students.append(student)
        
        db.commit()
        
        # ============================================================
        # PART 5: CREATE MENTOR SESSIONS
        # ============================================================
        print("\n[5/7] Creating mentor sessions...")
        
        session_count = 0
        now = datetime.utcnow()
        
        for mentor, data in mentors:
            for i, student in enumerate(students):
                # Create past sessions (for reviews)
                for j in range(2):
                    session = MentorSession(
                        mentor_id=mentor.id,
                        student_id=student.id,
                        topic=f"{data['name'].split()[0]}'s Session {j+1}",
                        description=f"Learning session about {data['expertise'].split(',')[0]}",
                        scheduled_at=now - timedelta(days=7-j, hours=i),
                        duration_minutes=60,
                        status=SessionStatus.COMPLETED,
                        meeting_url=f"https://zoom.us/j/mentor{mentor.id}session{j}",
                        price=mentor.hourly_rate * 1.0,
                        payment_status="paid",
                        completed_at=now - timedelta(days=6-j, hours=i),
                        created_at=now - timedelta(days=8-j, hours=i),
                    )
                    db.add(session)
                    session_count += 1
                
                # Create upcoming session
                upcoming = MentorSession(
                    mentor_id=mentor.id,
                    student_id=student.id,
                    topic=f"Upcoming session with {data['name'].split()[0]}",
                    description="Scheduled mentoring session",
                    scheduled_at=now + timedelta(days=3+i, hours=14),
                    duration_minutes=60,
                    status=SessionStatus.CONFIRMED,
                    meeting_url=f"https://zoom.us/j/mentor{mentor.id}upcoming{i}",
                    price=mentor.hourly_rate * 1.0,
                    payment_status="paid",
                    created_at=now,
                )
                db.add(upcoming)
                session_count += 1
        
        db.flush()
        print(f"  ✓ Created {session_count} mentor sessions")
        db.commit()
        
        # ============================================================
        # PART 6: UPDATE MENTOR STATS & CREATE REVIEWS
        # ============================================================
        print("\n[6/7] Creating reviews and updating mentor stats...")
        
        review_count = 0
        for mentor, data in mentors:
            # Get completed sessions
            completed = db.query(MentorSession).filter(
                MentorSession.mentor_id == mentor.id,
                MentorSession.status == SessionStatus.COMPLETED
            ).all()
            
            # Create reviews
            ratings = []
            for session in completed:
                if not db.query(MentorReview).filter(
                    MentorReview.session_id == session.id
                ).first():
                    rating = 4 + (hash(session.id) % 2)  # 4 or 5 stars
                    ratings.append(rating)
                    
                    review = MentorReview(
                        mentor_id=mentor.id,
                        session_id=session.id,
                        student_id=session.student_id,
                        rating=rating,
                        review_text=f"Great session! {data['name']} is very knowledgeable and patient.",
                        tags="knowledgeable,patient,helpful",
                        created_at=session.completed_at or now
                    )
                    db.add(review)
                    review_count += 1
            
            # Update mentor stats
            if ratings:
                mentor.total_sessions = len(completed)
                mentor.average_rating = sum(ratings) / len(ratings)
                mentor.total_earnings = mentor.hourly_rate * len(completed)
            
            db.flush()
        
        db.commit()
        print(f"  ✓ Created {review_count} reviews and updated mentor stats")
        
        # ============================================================
        # PART 7: CREATE CHAT MESSAGES
        # ============================================================
        print("\n[7/7] Creating session messages...")
        
        message_count = 0
        for mentor, data in mentors:
            sessions = db.query(MentorSession).filter(
                MentorSession.mentor_id == mentor.id,
                MentorSession.status.in_([SessionStatus.CONFIRMED, SessionStatus.COMPLETED])
            ).limit(2).all()
            
            for session in sessions:
                # Create a few messages
                if not db.query(MentorMessage).filter(
                    MentorMessage.session_id == session.id
                ).first():
                    messages = [
                        ("student", f"Hi {data['name'].split()[0]}, looking forward to our session!"),
                        ("mentor", f"Hey! Me too. Let's discuss {data['expertise'].split(',')[0]}."),
                        ("student", "What should I prepare?"),
                        ("mentor", "Just bring your questions and notes!"),
                    ]
                    
                    for sender_type, text in messages:
                        sender_id = session.student_id if sender_type == "student" else mentor.user_id
                        msg = MentorMessage(
                            session_id=session.id,
                            sender_id=sender_id,
                            message=text,
                            message_type="text",
                            is_read=True,
                            created_at=now - timedelta(hours=2)
                        )
                        db.add(msg)
                        message_count += 1
        
        db.commit()
        print(f"  ✓ Created {message_count} chat messages")
        
        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        mentor_count = db.query(Mentor).count()
        session_count = db.query(MentorSession).count()
        review_count = db.query(MentorReview).count()
        availability_count = db.query(MentorAvailability).count()
        message_count = db.query(MentorMessage).count()
        
        print("\n" + "="*80)
        print("SEEDING COMPLETE - MENTOR MODULE SUMMARY")
        print("="*80)
        print(f"✓ Mentors created:           {mentor_count}")
        print(f"✓ Sessions created:          {session_count}")
        print(f"✓ Reviews created:           {review_count}")
        print(f"✓ Availability slots:        {availability_count}")
        print(f"✓ Chat messages:             {message_count}")
        print("\nTest Mentors:")
        for user, data in mentor_users:
            mentor = db.query(Mentor).filter(Mentor.user_id == user.id).first()
            if mentor:
                print(f"  • {data['name']:<20} | Email: {data['email']:<30} | Rate: ${mentor.hourly_rate:.2f}/hr")
        
        print("\nTest Login Credentials:")
        print("  • Email:    <mentor email above>")
        print("  • Password: password123")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_complete_mentors()
