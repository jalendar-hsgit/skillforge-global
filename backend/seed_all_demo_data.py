#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Demo Data Seeding Script
Seeds all demo data for: Users, Mentors, Courses, Jobs, Marketplace, Admin/SuperAdmin
Also generates insights on what's pending
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.db import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorReview, MentorStatus, SessionStatus
from app.modelsx.mentor_documents import MentorDocument, MentorApproval, DocumentType, DocumentStatus
from app.modelsx.course import Course
from app.modelsx.job_application import JobApplication, ApplicationStatus, JobType
from app.modelsx.marketplace import DigitalProduct, ProductStatus, DigitalProductType
from app.modelsx.order import Order

# Import all models to ensure tables are created
from app.models import User, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, VideoProgress
from app.modelsx.coins import CoinLedger
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.resume import Resume, ResumeTemplate
from app.modelsx.admin_log import AdminLog
from app.modelsx.coding_practice import CodingChallenge


class DemoDataSeeder:
    def __init__(self):
        self.db = SessionLocal()
        self.stats = {
            "users": {"created": 0, "existing": 0},
            "mentors": {"created": 0, "existing": 0},
            "courses": {"created": 0, "existing": 0},
            "jobs": {"created": 0, "existing": 0},
            "marketplace": {"created": 0, "existing": 0},
            "orders": {"created": 0, "existing": 0},
            "mentor_sessions": {"created": 0, "existing": 0},
            "mentor_availability": {"created": 0, "existing": 0},
            "mentor_documents": {"created": 0, "existing": 0},
            "coding_challenges": {"created": 0, "existing": 0},
        }

    def seed_admin_and_roles(self):
        """Create admin and superadmin users"""
        print("\n" + "="*60)
        print("SEEDING: ADMIN & SUPERADMIN USERS")
        print("="*60)
        
        admin_users = [
            ("superadmin@skillforge.com", "super123", UserRole.SUPERADMIN, "System SuperAdmin"),
            ("admin@skillforge.com", "admin123", UserRole.ADMIN, "System Admin"),
        ]
        
        for email, password, role, name in admin_users:
            existing = self.db.query(User).filter(User.email == email).first()
            if existing:
                existing.role = role
                self.stats["users"]["existing"] += 1
                print(f"  [OK] Existing: {email} ({role.value})")
            else:
                user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    role=role,
                    name=name
                )
                self.db.add(user)
                self.stats["users"]["created"] += 1
                print(f"  [OK] Created: {email} ({role.value}) - pwd: {password}")
        
        self.db.commit()

    def seed_regular_users(self):
        """Create regular users"""
        print("\n" + "="*60)
        print("SEEDING: REGULAR USERS")
        print("="*60)
        
        users_data = [
            ("john.doe@example.com", "john123", "John Doe", "Software Engineer", ["Python", "JavaScript"]),
            ("jane.smith@example.com", "jane123", "Jane Smith", "Data Scientist", ["Python", "SQL"]),
            ("bob.wilson@example.com", "bob123", "Bob Wilson", "Web Developer", ["React", "Node.js"]),
            ("alice.johnson@example.com", "alice123", "Alice Johnson", "DevOps Engineer", ["Docker", "Kubernetes"]),
            ("charlie.brown@example.com", "charlie123", "Charlie Brown", "Full Stack Dev", ["Python", "React", "AWS"]),
        ]
        
        for email, password, name, bio, skills in users_data:
            existing = self.db.query(User).filter(User.email == email).first()
            if existing:
                self.stats["users"]["existing"] += 1
                print(f"  [OK] Existing: {email}")
            else:
                user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    name=name,
                    bio=bio,
                    skills=skills,
                    role=UserRole.USER
                )
                self.db.add(user)
                self.stats["users"]["created"] += 1
                print(f"  [OK] Created: {name} ({email})")
        
        self.db.commit()

    def seed_mentor_users(self):
        """Create mentor users"""
        print("\n" + "="*60)
        print("SEEDING: MENTOR USERS")
        print("="*60)
        
        mentors_data = [
            ("mentor.sarah@skillforge.com", "mentor123", "Sarah Chen", "Senior Python Dev, 10+ years experience", "python-ai,web-dev", 75.0),
            ("mentor.david@skillforge.com", "mentor123", "David Kumar", "React Expert, Frontend specialist", "web-dev,javascript", 65.0),
            ("mentor.emily@skillforge.com", "mentor123", "Emily Rodriguez", "ML Engineer, Data Science enthusiast", "python-ai,data-science", 85.0),
            ("mentor.james@skillforge.com", "mentor123", "James Patterson", "DevOps Pro, Cloud architect", "devops,cloud-computing", 70.0),
        ]
        
        for email, password, name, bio, expertise, hourly_rate in mentors_data:
            user = self.db.query(User).filter(User.email == email).first()
            
            if not user:
                user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    name=name,
                    bio=bio,
                    role=UserRole.MENTOR
                )
                self.db.add(user)
                self.db.flush()
                self.stats["users"]["created"] += 1
                print(f"  [OK] Created mentor user: {name}")
            else:
                user.role = UserRole.MENTOR
                print(f"  [OK] Updated existing: {name}")
            
            # Check if mentor profile exists
            existing_mentor = self.db.query(Mentor).filter(Mentor.user_id == user.id).first()
            if not existing_mentor:
                mentor = Mentor(
                    user_id=user.id,
                    bio=bio,
                    hourly_rate=hourly_rate,
                    expertise=expertise,
                    status=MentorStatus.APPROVED,
                    average_rating=4.5
                )
                self.db.add(mentor)
                self.stats["mentors"]["created"] += 1
                print(f"    -> Created mentor profile: ${hourly_rate}/hr - {expertise}")
            else:
                self.stats["mentors"]["existing"] += 1
                print(f"    -> Existing mentor profile")
        
        self.db.commit()

    def seed_mentor_availability(self):
        """Create mentor availability"""
        print("\n" + "="*60)
        print("SEEDING: MENTOR AVAILABILITY")
        print("="*60)
        
        mentors = self.db.query(Mentor).limit(4).all()
        
        # Create availability for Mon-Fri (0-4) with 1-hour slots from 9am-5pm
        for mentor in mentors:
            mentor_user = self.db.query(User).filter(User.id == mentor.user_id).first()
            
            # Check if already seeded
            existing_count = self.db.query(MentorAvailability).filter(
                MentorAvailability.mentor_id == mentor.id
            ).count()
            
            if existing_count > 0:
                self.stats["mentor_availability"]["existing"] += existing_count
                print(f"  [OK] Already exists for: {mentor_user.name if mentor_user else 'Unknown'} ({existing_count} slots)")
                continue
            
            # Create slots for Mon-Fri, 9am-5pm (8 one-hour slots per day = 40 slots)
            for day_of_week in range(5):  # 0=Monday, 4=Friday
                for hour in range(9, 17):  # 9am to 5pm
                    start_time = f"{hour:02d}:00"
                    end_time = f"{hour + 1:02d}:00"
                    
                    avail = MentorAvailability(
                        mentor_id=mentor.id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True,
                        timezone="UTC"
                    )
                    self.db.add(avail)
                    self.stats["mentor_availability"]["created"] += 1
            
            print(f"  [OK] Created 40 slots for: {mentor_user.name if mentor_user else 'Unknown'} (Mon-Fri 9am-5pm)")
        
        self.db.commit()

    def seed_mentor_documents(self):
        """Create mentor verification documents for demo"""
        print("\n" + "="*60)
        print("SEEDING: MENTOR DOCUMENTS")
        print("="*60)
        
        mentors = self.db.query(Mentor).limit(4).all()
        
        document_types = [
            DocumentType.CERTIFICATION,
            DocumentType.ID_VERIFICATION,
            DocumentType.DEGREE,
            DocumentType.EXPERIENCE,
        ]
        
        for mentor in mentors:
            # Create 2 documents per mentor
            for i, doc_type in enumerate(document_types[:2]):
                existing = self.db.query(MentorDocument).filter(
                    MentorDocument.mentor_id == mentor.id,
                    MentorDocument.document_type == doc_type
                ).first()
                
                if not existing:
                    doc = MentorDocument(
                        mentor_id=mentor.id,
                        document_type=doc_type,
                        filename=f"{doc_type.value}_document_{mentor.id}.pdf",
                        filepath=f"mentor_documents/{mentor.id}/{doc_type.value}_document.pdf",
                        file_size=1024 * 100 + (i * 50),  # 100KB to 100KB
                        mime_type="application/pdf",
                        status=DocumentStatus.PENDING,
                        uploaded_at=datetime.utcnow() - timedelta(days=2),
                    )
                    self.db.add(doc)
                    self.stats["mentor_documents"]["created"] += 1
                else:
                    self.stats["mentor_documents"]["existing"] += 1
            
            mentor_user = self.db.query(User).filter(User.id == mentor.user_id).first()
            print(f"  [OK] Created documents for: {mentor_user.name if mentor_user else 'Unknown'}")
        
        self.db.commit()

    def seed_mentor_sessions(self):
        """Create mentor sessions with various statuses"""
        print("\n" + "="*60)
        print("SEEDING: MENTOR SESSIONS")
        print("="*60)
        
        from app.modelsx.mentor import SessionFeedback
        
        mentors = self.db.query(Mentor).limit(4).all()
        students = self.db.query(User).filter(User.role == UserRole.USER).limit(5).all()
        
        session_topics = [
            "Python Fundamentals",
            "Web Development with React",
            "Database Design",
            "Cloud Deployment with AWS",
            "API Development",
            "Data Structures",
            "System Design",
        ]
        
        now = datetime.utcnow()
        session_count = 0
        
        for mentor_idx, mentor in enumerate(mentors):
            mentor_user = self.db.query(User).filter(User.id == mentor.user_id).first()
            
            # Create 3-4 sessions per mentor with mixed statuses
            for student_idx, student in enumerate(students[:3]):
                # Session 1: Completed (past) with feedback
                if student_idx == 0:
                    session = MentorSession(
                        mentor_id=mentor.id,
                        student_id=student.id,
                        topic=session_topics[mentor_idx % len(session_topics)],
                        description="Discussion on fundamentals and best practices",
                        scheduled_at=now - timedelta(days=7, hours=2),
                        status=SessionStatus.COMPLETED,
                        duration_minutes=60,
                        price=mentor.hourly_rate,
                        meeting_url="https://zoom.us/j/completed_session_1",
                        completed_at=now - timedelta(days=7),
                        mentor_notes="Great progress! Student grasped core concepts quickly."
                    )
                    self.db.add(session)
                    self.db.flush()
                    
                    # Add feedback for completed session
                    feedback = SessionFeedback(
                        session_id=session.id,
                        mentor_feedback="Excellent session. Student is quick learner with good grasp of concepts.",
                        student_notes="Very helpful! Learned a lot about best practices and optimization.",
                        session_quality_rating=5,
                        key_topics="fundamentals, optimization, design patterns",
                        follow_up_required=False
                    )
                    self.db.add(feedback)
                    
                    # Add review
                    review = MentorReview(
                        mentor_id=mentor.id,
                        session_id=session.id,
                        student_id=student.id,
                        rating=5,
                        review_text="Excellent mentor! Very knowledgeable and patient.",
                        tags="knowledgeable,patient,helpful"
                    )
                    self.db.add(review)
                    
                    session_count += 1
                    self.stats["mentor_sessions"]["created"] += 1
                    print(f"  [OK] Session {session_count}: COMPLETED (5-star) - {session_topics[mentor_idx % len(session_topics)]}")
                
                # Session 2: Confirmed (upcoming)
                elif student_idx == 1:
                    session = MentorSession(
                        mentor_id=mentor.id,
                        student_id=student.id,
                        topic=session_topics[(mentor_idx + 1) % len(session_topics)],
                        description="Advanced topics and Q&A",
                        scheduled_at=now + timedelta(days=3, hours=2),
                        status=SessionStatus.CONFIRMED,
                        duration_minutes=60,
                        price=mentor.hourly_rate,
                        meeting_url="https://zoom.us/j/confirmed_session_2"
                    )
                    self.db.add(session)
                    session_count += 1
                    self.stats["mentor_sessions"]["created"] += 1
                    print(f"  [OK] Session {session_count}: CONFIRMED - {session_topics[(mentor_idx + 1) % len(session_topics)]}")
                
                # Session 3: Pending (awaiting mentor confirmation)
                else:
                    session = MentorSession(
                        mentor_id=mentor.id,
                        student_id=student.id,
                        topic=session_topics[(mentor_idx + 2) % len(session_topics)],
                        description="Introductory session",
                        scheduled_at=now + timedelta(days=5, hours=3),
                        status=SessionStatus.PENDING,
                        duration_minutes=60,
                        price=mentor.hourly_rate
                    )
                    self.db.add(session)
                    session_count += 1
                    self.stats["mentor_sessions"]["created"] += 1
                    print(f"  [OK] Session {session_count}: PENDING - {session_topics[(mentor_idx + 2) % len(session_topics)]}")
            
            print(f"    Total for {mentor_user.name if mentor_user else 'Unknown'}: 3 sessions")
        
        self.db.commit()
        print(f"\n  Total Sessions Created: {session_count}")

    def seed_courses(self):
        """Create demo courses"""
        print("\n" + "="*60)
        print("SEEDING: COURSES")
        print("="*60)
        
        courses_data = [
            ("python-fundamentals", "Python Fundamentals", "Learn Python basics", 49.99, "beginner"),
            ("web-dev-bootcamp", "Web Development Bootcamp", "Master HTML, CSS, JavaScript", 99.99, "intermediate"),
            ("react-nextjs", "Advanced React & Next.js", "Build modern web applications", 149.99, "advanced"),
            ("ml-masterclass", "Machine Learning Masterclass", "ML with Python & TensorFlow", 199.99, "advanced"),
            ("devops-essentials", "DevOps Essentials", "Docker, Kubernetes & Cloud", 129.99, "intermediate"),
        ]
        
        for path, title, desc, price, level in courses_data:
            existing = self.db.query(Course).filter(Course.path == path).first()
            
            if not existing:
                course = Course(
                    path=path,
                    title=title,
                    description=desc,
                    price=price,
                    difficulty=level,
                    category="Programming",
                    is_paid=True
                )
                self.db.add(course)
                self.stats["courses"]["created"] += 1
                print(f"  [OK] Created: {title} (${price})")
            else:
                self.stats["courses"]["existing"] += 1
                print(f"  [OK] Existing: {title}")
        
        self.db.commit()

    def seed_job_applications(self):
        """Create job applications"""
        print("\n" + "="*60)
        print("SEEDING: JOB APPLICATIONS")
        print("="*60)
        
        users = self.db.query(User).filter(User.role == UserRole.USER).limit(5).all()
        
        jobs_data = [
            ("Google", "Senior Software Engineer", "remote", "https://google.com/careers", "Full-time opportunity"),
            ("Microsoft", "Python Developer", "hybrid", "https://microsoft.com/careers", "Work with Azure cloud"),
            ("Amazon", "ML Engineer", "onsite", "https://amazon.com/careers", "EC2 and ML services"),
            ("Meta", "React Developer", "remote", "https://meta.com/careers", "Social platform development"),
            ("Apple", "Systems Engineer", "onsite", "https://apple.com/careers", "Hardware/Software integration"),
        ]
        
        for user in users:
            job = jobs_data[users.index(user) % len(jobs_data)]
            company, position, location, url, desc = job
            
            existing = self.db.query(JobApplication).filter(
                JobApplication.user_id == user.id,
                JobApplication.company_name == company
            ).first()
            
            if not existing:
                application = JobApplication(
                    user_id=user.id,
                    company_name=company,
                    position_title=position,
                    job_type=JobType.FULL_TIME,
                    location=location,
                    work_mode="remote",
                    job_url=url,
                    description=desc,
                    status=ApplicationStatus.APPLIED
                )
                self.db.add(application)
                self.stats["jobs"]["created"] += 1
                print(f"  [OK] Created: {user.name} -> {company} ({position})")
            else:
                self.stats["jobs"]["existing"] += 1
        
        self.db.commit()

    def seed_marketplace_products(self):
        """Create marketplace products"""
        print("\n" + "="*60)
        print("SEEDING: MARKETPLACE PRODUCTS")
        print("="*60)
        
        sellers = self.db.query(User).filter(User.role == UserRole.MENTOR).limit(3).all()
        
        products_data = [
            ("Python Cheat Sheet", "Quick reference for Python syntax", 9.99),
            ("Resume Template Pack", "5 professional resume templates", 19.99),
            ("Interview Prep Guide", "Comprehensive interview preparation", 29.99),
            ("Code Review Checklist", "Best practices for code reviews", 14.99),
            ("AWS Certification Bundle", "All resources for AWS certification", 49.99),
        ]
        
        for i, seller in enumerate(sellers):
            product = products_data[i % len(products_data)]
            name, desc, price = product
            
            existing = self.db.query(DigitalProduct).filter(
                DigitalProduct.seller_id == seller.id,
                DigitalProduct.name == name
            ).first()
            
            if not existing:
                digital_product = DigitalProduct(
                    seller_id=seller.id,
                    name=name,
                    slug=name.lower().replace(" ", "-"),
                    description=desc,
                    product_type=DigitalProductType.RESOURCE,
                    category="Development",
                    price=price,
                    currency="USD",
                    status=ProductStatus.PUBLISHED,
                    is_featured=True
                )
                self.db.add(digital_product)
                self.stats["marketplace"]["created"] += 1
                print(f"  [OK] Created: {name} by {seller.name} (${price})")
            else:
                self.stats["marketplace"]["existing"] += 1
        
        self.db.commit()

    def seed_coding_challenges(self):
        """Create coding challenges for practice"""
        print("\n" + "="*60)
        print("SEEDING: CODING CHALLENGES")
        print("="*60)
        
        challenges_data = [
            # Easy challenges
            {
                "title": "Sum Two Numbers",
                "slug": "sum-two-numbers",
                "description": "Write a function that adds two numbers",
                "category": "Basics",
                "difficulty": "Easy",
                "tags": ["math", "fundamentals"],
                "problem_statement": "Given two integers a and b, return their sum.",
                "examples": [
                    {"input": "a=1, b=2", "output": "3", "explanation": "1 + 2 = 3"},
                    {"input": "a=-1, b=-2", "output": "-3", "explanation": "-1 + -2 = -3"}
                ],
                "starter_code": {
                    "python": "def sum_two_numbers(a, b):\n    pass",
                    "javascript": "function sumTwoNumbers(a, b) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "1,2", "expected": 3, "hidden": False},
                    {"input": "-1,-2", "expected": -3, "hidden": False},
                    {"input": "0,0", "expected": 0, "hidden": True}
                ],
                "supported_languages": ["python", "javascript", "java"],
                "points": 5,
                "coins_reward": 2,
                "estimated_time_minutes": 5
            },
            {
                "title": "Find Maximum",
                "slug": "find-maximum",
                "description": "Find the maximum element in an array",
                "category": "Arrays",
                "difficulty": "Easy",
                "tags": ["arrays", "searching"],
                "problem_statement": "Given an array of integers, return the maximum value.",
                "examples": [
                    {"input": "[1,2,3]", "output": "3", "explanation": "3 is the largest"},
                    {"input": "[-5,-1,-10]", "output": "-1", "explanation": "-1 is the largest"}
                ],
                "starter_code": {
                    "python": "def find_maximum(arr):\n    pass",
                    "javascript": "function findMaximum(arr) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "[1,2,3]", "expected": 3, "hidden": False},
                    {"input": "[-5,-1,-10]", "expected": -1, "hidden": False},
                    {"input": "[100]", "expected": 100, "hidden": True}
                ],
                "supported_languages": ["python", "javascript", "java"],
                "points": 8,
                "coins_reward": 3,
                "estimated_time_minutes": 10
            },
            # Medium challenges
            {
                "title": "Reverse String",
                "slug": "reverse-string",
                "description": "Reverse a string without using built-in functions",
                "category": "Strings",
                "difficulty": "Medium",
                "tags": ["strings", "manipulation"],
                "problem_statement": "Write a function to reverse a string. Do not use string slicing or reverse().",
                "examples": [
                    {"input": "'hello'", "output": "'olleh'", "explanation": "String reversed"},
                    {"input": "'a'", "output": "'a'", "explanation": "Single char stays same"}
                ],
                "starter_code": {
                    "python": "def reverse_string(s):\n    pass",
                    "javascript": "function reverseString(s) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "hello", "expected": "olleh", "hidden": False},
                    {"input": "a", "expected": "a", "hidden": False},
                    {"input": "Python", "expected": "nohtyP", "hidden": True}
                ],
                "supported_languages": ["python", "javascript"],
                "points": 15,
                "coins_reward": 5,
                "estimated_time_minutes": 15
            },
            {
                "title": "Two Sum",
                "slug": "two-sum",
                "description": "Find two numbers that sum to target",
                "category": "Arrays",
                "difficulty": "Medium",
                "tags": ["arrays", "hashing", "algorithms"],
                "problem_statement": "Given an array and a target sum, find two numbers that add up to the target. Return their indices.",
                "examples": [
                    {"input": "arr=[2,7,11,15], target=9", "output": "[0,1]", "explanation": "arr[0] + arr[1] = 2 + 7 = 9"},
                    {"input": "arr=[3,2,4], target=6", "output": "[1,2]", "explanation": "arr[1] + arr[2] = 2 + 4 = 6"}
                ],
                "starter_code": {
                    "python": "def two_sum(arr, target):\n    pass",
                    "javascript": "function twoSum(arr, target) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "[2,7,11,15],9", "expected": [0,1], "hidden": False},
                    {"input": "[3,2,4],6", "expected": [1,2], "hidden": False},
                    {"input": "[1,2,3,4],7", "expected": [2,3], "hidden": True}
                ],
                "supported_languages": ["python", "javascript", "java"],
                "points": 20,
                "coins_reward": 8,
                "estimated_time_minutes": 20
            },
            # Hard challenges
            {
                "title": "Merge Sorted Arrays",
                "slug": "merge-sorted-arrays",
                "description": "Merge two sorted arrays into one",
                "category": "Arrays",
                "difficulty": "Hard",
                "tags": ["arrays", "sorting", "merge"],
                "problem_statement": "Given two sorted arrays, merge them into a single sorted array in-place.",
                "examples": [
                    {"input": "arr1=[1,2,3], arr2=[2,5,6]", "output": "[1,2,2,3,5,6]", "explanation": "Merged and sorted"},
                    {"input": "arr1=[0], arr2=[0]", "output": "[0,0]", "explanation": "Same elements"}
                ],
                "starter_code": {
                    "python": "def merge_sorted(arr1, arr2):\n    pass",
                    "javascript": "function mergeSorted(arr1, arr2) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "[1,2,3],[2,5,6]", "expected": [1,2,2,3,5,6], "hidden": False},
                    {"input": "[0],[0]", "expected": [0,0], "hidden": False},
                    {"input": "[], [1,2,3]", "expected": [1,2,3], "hidden": True}
                ],
                "supported_languages": ["python", "javascript"],
                "points": 30,
                "coins_reward": 12,
                "estimated_time_minutes": 25
            },
            {
                "title": "Longest Substring",
                "slug": "longest-substring",
                "description": "Find longest substring without repeating characters",
                "category": "Strings",
                "difficulty": "Hard",
                "tags": ["strings", "sliding-window", "optimization"],
                "problem_statement": "Given a string, find the length of the longest substring without repeating characters.",
                "examples": [
                    {"input": "'abcabcbb'", "output": "3", "explanation": "'abc' is the longest"},
                    {"input": "'bbbbb'", "output": "1", "explanation": "'b' is the longest"}
                ],
                "starter_code": {
                    "python": "def longest_substring(s):\n    pass",
                    "javascript": "function longestSubstring(s) {\n    // Your code here\n}"
                },
                "test_cases": [
                    {"input": "abcabcbb", "expected": 3, "hidden": False},
                    {"input": "bbbbb", "expected": 1, "hidden": False},
                    {"input": "pwwkew", "expected": 3, "hidden": True}
                ],
                "supported_languages": ["python", "javascript"],
                "points": 40,
                "coins_reward": 15,
                "estimated_time_minutes": 30
            },
        ]
        
        for challenge_data in challenges_data:
            existing = self.db.query(CodingChallenge).filter(
                CodingChallenge.slug == challenge_data["slug"]
            ).first()
            
            if not existing:
                challenge = CodingChallenge(
                    title=challenge_data["title"],
                    slug=challenge_data["slug"],
                    description=challenge_data["description"],
                    category=challenge_data["category"],
                    difficulty=challenge_data["difficulty"],
                    tags=challenge_data.get("tags", []),
                    problem_statement=challenge_data["problem_statement"],
                    examples=challenge_data.get("examples", []),
                    starter_code=challenge_data.get("starter_code", {}),
                    test_cases=challenge_data.get("test_cases", []),
                    supported_languages=challenge_data.get("supported_languages", []),
                    points=challenge_data.get("points", 10),
                    coins_reward=challenge_data.get("coins_reward", 5),
                    estimated_time_minutes=challenge_data.get("estimated_time_minutes", 15),
                    simulator_type="code_editor"
                )
                self.db.add(challenge)
                self.stats["coding_challenges"]["created"] += 1
                print(f"  [OK] Created: {challenge_data['title']} ({challenge_data['difficulty']})")
            else:
                self.stats["coding_challenges"]["existing"] += 1
        
        self.db.commit()

    def seed_orders(self):
        """Create marketplace orders"""
        print("\n" + "="*60)
        print("SEEDING: MARKETPLACE ORDERS")
        print("="*60)
        
        users = self.db.query(User).filter(User.role == UserRole.USER).limit(5).all()
        courses = self.db.query(Course).limit(5).all()
        
        for i, user in enumerate(users):
            if courses:
                course = courses[i % len(courses)]
                
                existing = self.db.query(Order).filter(
                    Order.user_id == user.id,
                    Order.course_id == course.id
                ).first()
                
                if not existing:
                    order = Order(
                        user_id=user.id,
                        course_id=course.id,
                        order_number=f"ORD-{user.id}-{course.id}",
                        amount=course.price if hasattr(course, 'price') else 49.99,
                        subtotal=course.price if hasattr(course, 'price') else 49.99,
                        status="completed",
                        payment_method="stripe",
                        created_at=datetime.utcnow() - timedelta(days=i)
                    )
                    self.db.add(order)
                    self.stats["orders"]["created"] += 1
                    print(f"  [OK] Created: {user.name} purchased {course.title}")
                else:
                    self.stats["orders"]["existing"] += 1
        
        self.db.commit()

    def show_pending_items(self):
        """Show what's pending"""
        print("\n" + "="*60)
        print("PENDING ITEMS REPORT")
        print("="*60)
        
        # Pending mentor approvals
        pending_mentors = self.db.query(Mentor).filter(
            Mentor.status != MentorStatus.APPROVED
        ).count()
        print(f"\n[INFO] Mentor Approvals Pending: {pending_mentors}")
        
        # Pending job applications
        pending_jobs = self.db.query(JobApplication).filter(
            JobApplication.status.in_([
                ApplicationStatus.APPLIED,
                ApplicationStatus.SCREENING,
                ApplicationStatus.INTERVIEW
            ])
        ).count()
        print(f"[INFO] Job Applications Pending: {pending_jobs}")
        
        # Show next scheduled mentor sessions
        upcoming_sessions = self.db.query(MentorSession).filter(
            MentorSession.scheduled_at > datetime.utcnow(),
            MentorSession.status.in_([SessionStatus.PENDING, SessionStatus.CONFIRMED])
        ).order_by(MentorSession.scheduled_at).limit(5).all()
        
        print(f"\n[NEXT] Scheduled Mentor Sessions:")
        for session in upcoming_sessions:
            mentor = self.db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
            mentor_user = self.db.query(User).filter(User.id == mentor.user_id).first() if mentor else None
            student = self.db.query(User).filter(User.id == session.student_id).first()
            mentor_name = mentor_user.name if mentor_user else "Unknown"
            student_name = student.name if student else "Unknown"
            print(f"   - {session.scheduled_at.strftime('%Y-%m-%d %H:%M')} | {mentor_name} with {student_name} ({session.topic})")
        
        if not upcoming_sessions:
            print("   (None scheduled)")
        
        # Show pending course reviews
        pending_reviews = self.db.query(MentorReview).filter(
            MentorReview.rating == None
        ).count()
        print(f"\n[INFO] Pending Reviews: {pending_reviews}")

    def show_summary(self):
        """Show final summary"""
        print("\n" + "="*60)
        print("SEEDING SUMMARY")
        print("="*60)
        
        total_created = sum(v["created"] for v in self.stats.values())
        total_existing = sum(v["existing"] for v in self.stats.values())
        
        for key, value in self.stats.items():
            created = value["created"]
            existing = value["existing"]
            total = created + existing
            print(f"\n{key.upper()}")
            print(f"  Created: {created}")
            print(f"  Existing: {existing}")
            print(f"  Total: {total}")
        
        print("\n" + "="*60)
        print(f"TOTALS - Created: {total_created} | Existing: {total_existing} | Total: {total_created + total_existing}")
        print("="*60)

    def run(self):
        """Run all seeders"""
        try:
            print("\n[STARTING] COMPREHENSIVE DEMO DATA SEEDING...\n")
            
            self.seed_admin_and_roles()
            self.seed_regular_users()
            self.seed_mentor_users()
            self.seed_mentor_availability()
            self.seed_mentor_documents()
            self.seed_mentor_sessions()
            self.seed_courses()
            self.seed_job_applications()
            self.seed_marketplace_products()
            self.seed_coding_challenges()
            # self.seed_orders()  # DISABLED: Allow test users to add courses to cart
            # Previously this pre-purchased courses, preventing cart tests
            
            self.show_summary()
            self.show_pending_items()
            
            print("\n[SUCCESS] DEMO DATA SEEDING COMPLETE!\n")
            
        except Exception as e:
            print(f"\n[ERROR] during seeding: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.db.close()


if __name__ == "__main__":
    seeder = DemoDataSeeder()
    seeder.run()
