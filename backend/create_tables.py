from app.core.db import Base, engine
from app.models import User, Progress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress
from app.modelsx.coins import CoinLedger
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, ResumeAchievement, ResumeTemplate, AIProjectTemplate, ResumeAnalytics, ATSReport
from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
from app.modelsx.job_application import JobApplication
from app.modelsx.order import Order, Coupon, CartItem

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# Check the correct database path from settings
from app.core.config import settings
db_path = settings.DATABASE_URL.replace('sqlite:///', '')
print(f"\nDatabase path: {db_path}")

import sqlite3
import os
if not os.path.exists(db_path):
    print(f"Database file not found at: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\nTotal tables: {len(tables)}")
    print("Tables:", tables[:10], "..." if len(tables) > 10 else "")

    if 'mentor_sessions' in tables:
        cursor.execute('PRAGMA table_info(mentor_sessions)')
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\nmentor_sessions has {len(columns)} columns")
        print("Columns:", columns)
    conn.close()
