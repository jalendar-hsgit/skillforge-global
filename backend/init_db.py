"""
Database Initialization Script
Handles fresh database creation with proper order of table creation
Run this script to initialize a fresh database with all tables and basic seed data
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text, inspect
from app.core.db import Base, engine
from app.core.config import settings

# Import all models to register them with Base before create_all
# This must happen before any create_all() calls
try:
    from app.models import User, Progress as LegacyProgress, QuizAttempt, CreditLedger, Subscriber
    from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress, coins
    from app.modelsx.coins import CoinLedger
    from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
    from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview, SessionFeedback
    from app.modelsx.mentor_documents import MentorDocument, MentorApproval
    from app.modelsx.mentor_verification import MentorVerification
    from app.modelsx.payout import MentorPayout, MentorEarning
    from app.modelsx.admin_log import AdminLog
    from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
    from app.modelsx.stripe_connect import MentorStripeAccount
    from app.modelsx.chat_file import MentorChatFile
    from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, ResumeAchievement, ResumeTemplate, AIProjectTemplate, ATSReport
    from app.modelsx.resume_analytics import ResumeAnalytics
    from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
    from app.modelsx.job_application import JobApplication as JobApplicationTracker
    # Import marketplace BEFORE order since order.py has foreign keys to digital_products
    from app.modelsx.marketplace import (
        DigitalProduct, ProductPurchase, SellerAccount,
        ProductBundle, SellerPayout, MarketplaceAnalytics, SellerEarning
    )
    from app.modelsx.order import Order, Coupon, CartItem, OrderItem
    from app.modelsx.platform_settings import PlatformSetting
    from app.modelsx.coding_practice import CodingChallenge, CodingSubmission, SimulatorEnvironment, PracticeSession, CloudLabScenario, ChallengeHint
    from app.modelsx.code_snippets import CodeSnippet, SnippetVote, SnippetCopy
    from app.modelsx.solution_sharing import ChallengeSolution, SolutionVote, SolutionComment, SolutionBookmark
    from app.modelsx.user_profiles import UserProfile, UserActivity, UserPreferences, UserStatistics
    from app.modelsx.social import UserFollow, Conversation, Message, SocialFeedItem
    from app.modelsx.learning_paths import LearningPath, PathChallenge, UserPathProgress, Certificate, SkillValidation, PathRecommendation
    from app.modelsx.premium_tiers import SubscriptionTier, FeatureBenefit, UserSubscription, SubscriptionHistory, PromoCode
    from app.modelsx.github_integration import GitHubAccount, GitHubRepository, GitHubContribution, GitHubStats
    from app.modelsx.advanced_dashboard import DashboardWidget, UserDashboardWidget, DashboardLayout, DashboardMetric, UserAnalytics, DashboardInsight
    from app.modelsx.ai_hints import AIHint, AIHintUsage, HintFeedback, HintTemplate, UserHintQuota
    from app.modelsx.pwa import ServiceWorkerConfig, OfflineSyncQueue, OfflineCache, PWANotificationPreference, PWAAnalytics
    from app.modelsx.badges import Badge, UserBadge, BadgeProgress, Leaderboard, Achievement as BadgeAchievement, UserAchievement
    from app.modelsx.phase_2_3_models import (
        MentorVerificationDocument, AnalyticsMetric, MentorAnalyticsSummary,
        SessionPayment, VideoSession, SessionRecording, SessionChatMessage
    )
except ImportError as e:
    print(f"[Init] Warning: Could not import some models: {e}")
    print(f"[Init] Proceeding with available models...")

def init_database():
    """Initialize the database with all tables"""
    print(f"[Init] Starting database initialization...")
    print(f"[Init] Database URL: {settings.DATABASE_URL}")
    
    try:
        # Get inspector to check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"[Init] Found {len(existing_tables)} existing tables")
            print(f"[Init] Skipping table creation (database already initialized)")
            return True
        
        print(f"[Init] No existing tables found. Creating new database schema...")
        
        # For SQLite, disable foreign key constraints during table creation
        if "sqlite" in str(engine.url).lower():
            print(f"[Init] Using SQLite - temporarily disabling foreign key constraints")
            with engine.begin() as conn:
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                print(f"[Init] Creating tables from Base metadata...")
                Base.metadata.create_all(bind=conn)
                conn.execute(text("PRAGMA foreign_keys=ON"))
        else:
            print(f"[Init] Using non-SQLite database - creating tables normally")
            Base.metadata.create_all(bind=engine)
        
        # Verify table creation
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        print(f"[Init] ✅ Successfully created {len(created_tables)} tables")
        
        return True
        
    except Exception as e:
        print(f"[Init] ❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_basic_data():
    """Seed basic data (optional - modify as needed)"""
    from app.core.db import SessionLocal
    
    print(f"[Init] Seeding basic data...")
    try:
        db = SessionLocal()
        # Add basic seed data here if needed
        db.close()
        print(f"[Init] ✅ Basic data seeded successfully")
        return True
    except Exception as e:
        print(f"[Init] ⚠️  Could not seed data: {e}")
        return False

if __name__ == "__main__":
    print(f"=" * 70)
    print(f"Database Initialization Script")
    print(f"=" * 70)
    
    # Initialize database
    if init_database():
        print(f"[Init] ✅ Database initialization complete!")
        
        # Optionally seed data
        seed_basic_data()
        
        print(f"[Init] Ready to run: uvicorn app.main:app --reload")
    else:
        print(f"[Init] ❌ Database initialization failed!")
        sys.exit(1)
