from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.db import Base, engine

# import models so tables are registered on Base
from app.models import User, Progress as LegacyProgress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress, coins
# ensure CoinLedger table is registered (modelsx.coins defines CoinLedger)
from app.modelsx.coins import CoinLedger
# import quiz template models for AI-generated quizzes
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
# import mentor models
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview, SessionFeedback
from app.modelsx.mentor_verification import MentorVerification
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.admin_log import AdminLog
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
# import resume models
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, ResumeAchievement, ResumeTemplate, AIProjectTemplate, ATSReport
from app.modelsx.resume_analytics import ResumeAnalytics
# Ensure versioning/comparison tables are registered before create_all
from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
# import hiring models
# import job application tracking
from app.modelsx.job_application import JobApplication as JobApplicationTracker
# import marketplace models
from app.modelsx.order import Order, Coupon, CartItem
# import platform settings
from app.modelsx.platform_settings import PlatformSetting
# import coding practice models
from app.modelsx.coding_practice import CodingChallenge, CodingSubmission, SimulatorEnvironment, PracticeSession, CloudLabScenario, ChallengeHint
# import code snippets models
from app.modelsx.code_snippets import CodeSnippet, SnippetVote, SnippetCopy
# import solution sharing models
from app.modelsx.solution_sharing import ChallengeSolution, SolutionVote, SolutionComment, SolutionBookmark
# import user profile models
from app.modelsx.user_profiles import UserProfile, UserActivity, UserPreferences, UserStatistics
# import social/follow system models and Phase 3.3 features
from app.modelsx.social import UserFollow, Conversation, Message, SocialFeedItem
# import learning paths models
from app.modelsx.learning_paths import LearningPath, PathChallenge, UserPathProgress, Certificate, SkillValidation, PathRecommendation
# import premium tiers models
from app.modelsx.premium_tiers import SubscriptionTier, FeatureBenefit, UserSubscription, SubscriptionHistory, PromoCode
# import github integration models
from app.modelsx.github_integration import GitHubAccount, GitHubRepository, GitHubContribution, GitHubStats
# import advanced dashboard models
from app.modelsx.advanced_dashboard import DashboardWidget, UserDashboardWidget, DashboardLayout, DashboardMetric, UserAnalytics, DashboardInsight
# import AI hints models
from app.modelsx.ai_hints import AIHint, AIHintUsage, HintFeedback, HintTemplate, UserHintQuota
# import PWA models
from app.modelsx.pwa import ServiceWorkerConfig, OfflineSyncQueue, OfflineCache, PWANotificationPreference, PWAAnalytics
# import Badge and Gamification models (MUST be before contests which references badges)
from app.modelsx.badges import Badge, UserBadge, BadgeProgress, Leaderboard, Achievement as BadgeAchievement, UserAchievement
# import Contest models
from app.modelsx.contests import Contest, ContestChallenge, ContestParticipant, ContestSubmission, ContestLeaderboard, ContestPrize, ContestTeam, ContestRound
# import Notification models
from app.modelsx.notifications import Notification, NotificationPreference, NotificationLog, NotificationTemplate
# import Code Execution models
from app.modelsx.code_executor import CodeExecution, TestCaseResult, ExecutionEnvironment, ExecutionMetrics
# import Activity and Feed models
from app.modelsx.activity import Activity, ActivityLike, ActivityComment, FeedSettings, Trending, Timeline
# import Forum and Discussion models
from app.modelsx.forums import (
    ForumCategory, ForumThread, ForumReply, ForumThreadVote, ForumReplyVote,
    ForumBookmark, ModeratorAction
)
# import Recommendation models
from app.modelsx.recommendations import (
    UserPreferences, ChallengeInteraction, Recommendation,
    SimilarityMatrix, RecommendationFeedback, RecommendationQueue
)
# import Team models
from app.modelsx.teams import (
    Team, TeamMember, TeamInvitation, TeamChallenge,
    TeamStatistics, TeamContest, TeamAnnouncement
)
# import Search models
from app.modelsx.search import (
    SearchQuery, SearchResult, SearchFilter, TrendingSearch,
    SearchAnalytics, SearchIndex, SavedSearch
)
# import Interview models
from app.modelsx.interview import (
    QuestionCategory, InterviewQuestion, MockInterview, InterviewAnswer,
    InterviewSchedule, InterviewPerformance, InterviewFeedback
)
# import Referral models
from app.modelsx.referral import (
    ReferralCode, Referral, ReferralReward, ReferralCampaign, ReferralStatistics
)
# import Marketplace models
from app.modelsx.marketplace import (
    DigitalProduct, ProductPurchase, ProductReview, SellerAccount,
    ProductBundle, SellerPayout, MarketplaceAnalytics
)
# import Security audit models
from app.modelsx.security_audit import LoginHistory, AuditLog, SessionRevocation

# ============================================================
# PHASE 2.3 MODELS - IMPORT ALL 10 MODELS
# ============================================================
from app.modelsx.phase_2_3_models import (
    MentorVerificationDocument,
    AnalyticsMetric,
    MentorAnalyticsSummary,
    SessionPayment,
    VideoSession,
    SessionRecording,
    SessionChatMessage
)
# Note: Message model is imported from social.py above

# Forum models (already imported above from forums.py)


# ============================================================
# PAYMENT & EMAIL SERVICES
# ============================================================
from app.services.stripe_service import StripeService
from app.services.email_service import email_service

# v1 routers (existing)
from app.api.v1 import auth, courses, progress, quizzes, chat, subscribe, quiz_status, paths, achievements, dashboard, credits

# Phase 3.3 routers
from app.api.v1 import forum, messages, notifications, feed, profiles

# Phase 3.4 routers (import as separate names to avoid conflicts with v1x)
from app.api.v1 import learning_paths as v1_learning_paths
from app.api.v1 import certificates, skills
from app.api.v1 import recommendations as v1_recommendations

# Phase 3.5 routers
from app.api.v1 import websocket

# Security routers
security_router = None
try:
    from app.api.v1x.security import router as security_router
except Exception as e:
    security_router = None
    print(f"Failed to import security router: {e}")

# Try to import optional v1x routers directly (bypass v1x __init__.py)
courses_db = None
progress_db = None
quizzes_db = None
youtube_sync = None
coins_db = None
mentors = None
admin_mentors = None
payments = None
chat_files = None
payouts = None
subscriptions = None
connect = None

try:
    from app.api.v1x.courses_db import router as courses_db, courses_router
except Exception as e:
    print(f"Failed to import courses_db: {e}")
    courses_router = None

try:
    from app.api.v1x.progress_db_stub import router as progress_db
except Exception as e:
    print(f"Failed to import progress_db: {e}")

try:
    from app.api.v1x.quizzes_db_stub import router as quizzes_db
except Exception as e:
    print(f"Failed to import quizzes_db: {e}")

try:
    from app.api.v1x.youtube_sync_stub import router as youtube_sync
except Exception as e:
    print(f"Failed to import youtube_sync: {e}")

try:
    from app.api.v1x.coins_stub import router as coins_db
except Exception as e:
    print(f"Failed to import coins_db: {e}")

try:
    from app.api.v1x.mentors import router as mentors
except Exception as e:
    print(f"Failed to import mentors: {e}")

try:
    from app.api.v1x.mentor_verification import router as mentor_verification
except Exception as e:
    mentor_verification = None
    print(f"Failed to import mentor_verification: {e}")

try:
    from app.api.v1x.account import router as account
except Exception as e:
    account = None
    print(f"Failed to import account: {e}")

admin_mentors = None  # Deprecated router; replaced by unified app.api.v1x.admin

try:
    from app.api.v1x.admin import router as admin_router
except Exception as e:
    admin_router = None
    print(f"Failed to import admin router: {e}")

try:
    from app.api.v1x.payments import router as payments
except Exception as e:
    print(f"Failed to import payments: {e}")

try:
    from app.api.v1x.chat_files import router as chat_files
except Exception as e:
    print(f"Failed to import chat_files: {e}")

try:
    from app.api.v1x.payouts import router as payouts
except Exception as e:
    print(f"Failed to import payouts: {e}")

try:
    from app.api.v1x.subscriptions import router as subscriptions
except Exception as e:
    print(f"Failed to import subscriptions: {e}")
    subscriptions = None

try:
    from app.api.v1x.connect import router as connect
except Exception as e:
    print(f"Failed to import connect: {e}")

try:
    from app.api.v1x.student_dashboard import router as student_dashboard
except Exception as e:
    student_dashboard = None
    print(f"Failed to import student_dashboard: {e}")

try:
    from app.api.v1x.mentor_portal import router as mentor_portal
except Exception as e:
    mentor_portal = None
    print(f"Failed to import mentor_portal: {e}")

try:
    from app.api.v1x.recordings import router as recordings
except Exception as e:
    print(f"Failed to import recordings: {e}")

try:
    from app.api.v1x.session import router as session
except Exception as e:
    session = None
    print(f"Failed to import session: {e}")

try:
    from app.api.v1x.resumes import router as resumes
except Exception as e:
    print(f"Failed to import resumes: {e}")

try:
    from app.api.v1x.resume_ai import router as resume_ai
except Exception as e:
    print(f"Failed to import resume_ai: {e}")

try:
    from app.api.v1x.cover_letters import router as cover_letter
except Exception as e:
    print(f"Failed to import cover_letter: {e}")

try:
    from app.api.v1x.resume_comparison import router as resume_comparison
except Exception as e:
    print(f"Failed to import resume_comparison: {e}")

try:
    from app.api.v1x.linkedin_import import router as linkedin_import
except Exception as e:
    print(f"Failed to import linkedin_import: {e}")

try:
    from app.api.v1x.hiring import router as hiring
except Exception as e:
    print(f"Failed to import hiring: {e}")

try:
    from app.api.v1x.resume_import import router as resume_import
except Exception as e:
    print(f"Failed to import resume_import: {e}")

try:
    from app.api.v1x.marketplace import router as marketplace
except Exception as e:
    print(f"Failed to import marketplace: {e}")

try:
    from app.api.v1x.job_applications import router as job_applications
except Exception as e:
    print(f"Failed to import job_applications: {e}")
    job_applications = None

try:
    from app.api.v1x.job_application_notifications import router as job_notifications
except Exception as e:
    print(f"Failed to import job_notifications: {e}")

try:
    from app.api.v1x.job_application_calendar import router as job_calendar
except Exception as e:
    print(f"Failed to import job_calendar: {e}")

try:
    from app.api.v1x.resume_export import router as resume_export
except Exception as e:
    print(f"Failed to import resume_export: {e}")
    resume_export = None

try:
    from app.api.v1x.resume_templates import router as resume_templates
except Exception as e:
    print(f"Failed to import resume_templates: {e}")

try:
    from app.api.v1x.resume_analytics_events import router as resume_analytics_events
except Exception as e:
    print(f"Failed to import resume_analytics_events: {e}")

try:
    from app.api.v1x.resume_scoring import router as resume_scoring
except Exception as e:
    print(f"Failed to import resume_scoring: {e}")
    resume_scoring = None

try:
    from app.api.v1x.leaderboard import router as leaderboard
except Exception as e:
    print(f"Failed to import leaderboard: {e}")
    leaderboard = None

try:
    from app.api.v1x.admin_metrics import router as admin_metrics
except Exception as e:
    print(f"Failed to import admin_metrics: {e}")
    admin_metrics = None

try:
    from app.api.v1x.admin_analytics import router as admin_analytics
except Exception as e:
    print(f"Failed to import admin_analytics: {e}")
    admin_analytics = None

try:
    from app.api.v1x.coding_practice import router as coding_practice
except Exception as e:
    print(f"Failed to import coding_practice: {e}")

try:
    from app.api.v1x.code_snippets import router as code_snippets
except Exception as e:
    print(f"Failed to import code_snippets: {e}")

try:
    from app.api.v1x.solution_sharing import router as solution_sharing
except Exception as e:
    print(f"Failed to import solution_sharing: {e}")

try:
    from app.api.v1x.user_profiles import router as user_profiles
except Exception as e:
    print(f"Failed to import user_profiles: {e}")

try:
    from app.api.v1x.solution_comments import router as solution_comments
except Exception as e:
    print(f"Failed to import solution_comments: {e}")

try:
    from app.api.v1x.social import router as social
except Exception as e:
    print(f"Failed to import social: {e}")

try:
    from app.api.v1x.learning_paths import router as learning_paths
except Exception as e:
    print(f"Failed to import learning_paths: {e}")

try:
    from app.api.v1x.premium_tiers import router as premium_tiers
except Exception as e:
    print(f"Failed to import premium_tiers: {e}")

try:
    from app.api.v1x.github_integration import router as github_integration
except Exception as e:
    print(f"Failed to import github_integration: {e}")

try:
    from app.api.v1x.advanced_dashboard import router as advanced_dashboard
except Exception as e:
    print(f"Failed to import advanced_dashboard: {e}")

try:
    from app.api.v1x.ai_hints import router as ai_hints
except Exception as e:
    print(f"Failed to import ai_hints: {e}")

try:
    from app.api.v1x.pwa import router as pwa
except Exception as e:
    print(f"Failed to import pwa: {e}")

# import contests router
contests = None
try:
    from app.api.v1x.contests import router as contests_router
    contests = contests_router
except Exception as e:
    print(f"Failed to import contests: {e}")

# import notifications router (v1x)
notifications_v1x = None
try:
    from app.api.v1x.notifications import router as notifications_v1x_router
    notifications_v1x = notifications_v1x_router
except Exception as e:
    print(f"Failed to import notifications v1x: {e}")

# import code executor router
code_executor = None
try:
    from app.api.v1x.code_executor import router as code_executor_router
    code_executor = code_executor_router
except Exception as e:
    print(f"Failed to import code_executor: {e}")

# import activity and feed router
activity = None
try:
    from app.api.v1x.activity import router as activity_router
    activity = activity_router
except Exception as e:
    print(f"Failed to import activity: {e}")

# import badges and gamification router
badges = None
try:
    from app.api.v1x.badges import router as badges_router
    badges = badges_router
except Exception as e:
    print(f"Failed to import badges: {e}")

# import forums and discussion router
forums = None
try:
    from app.api.v1x.forums import router as forums_router
    forums = forums_router
except Exception as e:
    print(f"Failed to import forums: {e}")

# import recommendations router
recommendations = None
try:
    from app.api.v1x.recommendations import router as recommendations_router
    recommendations = recommendations_router
except Exception as e:
    print(f"Failed to import recommendations: {e}")

# import teams router
teams = None
try:
    from app.api.v1x.teams import router as teams_router
    teams = teams_router
except Exception as e:
    print(f"Failed to import teams: {e}")

# import search router
search = None
try:
    from app.api.v1x.search import router as search_router
    search = search_router
except Exception as e:
    print(f"Failed to import search: {e}")

# import interview router
interview = None
try:
    from app.api.v1x.interview import router as interview_router
    interview = interview_router
except Exception as e:
    print(f"Failed to import interview: {e}")

# import referral router
referral = None
try:
    from app.api.v1x.referral import router as referral_router
    referral = referral_router
except Exception as e:
    print(f"Failed to import referral: {e}")

# import marketplace router
marketplace = None
try:
    from app.api.v1x.marketplace import router as marketplace_router
    marketplace = marketplace_router
except Exception as e:
    print(f"Failed to import marketplace: {e}")

# import notifications websocket router
notifications_websocket = None
try:
    from app.api.v1x.notifications_websocket import router as notifications_websocket_router
    notifications_websocket = notifications_websocket_router
except Exception as e:
    print(f"Failed to import notifications_websocket: {e}")

# ============================================================
# PHASE 2.3 ROUTERS - IMPORT ALL 6 ROUTERS + STRIPE
# ============================================================
verification_router = None
try:
    from app.api.v1x.phase_2_3_endpoints import verification_router
except Exception as e:
    print(f"Failed to import verification_router: {e}")

analytics_router = None
try:
    from app.api.v1x.phase_2_3_endpoints import analytics_router
except Exception as e:
    print(f"Failed to import analytics_router: {e}")

payments_router_phase23 = None
try:
    from app.api.v1x.phase_2_3_endpoints import payments_router as payments_router_phase23
except Exception as e:
    print(f"Failed to import payments_router (Phase 2.3): {e}")

video_router = None
try:
    from app.api.v1x.phase_2_3_endpoints import video_router
except Exception as e:
    print(f"Failed to import video_router: {e}")

messaging_router = None
try:
    from app.api.v1x.phase_2_3_endpoints import messaging_router
except Exception as e:
    print(f"Failed to import messaging_router: {e}")

forum_router = None
try:
    from app.api.v1x.phase_2_3_endpoints import forum_router
except Exception as e:
    print(f"Failed to import forum_router: {e}")

# NEW: Stripe-integrated payment router
payments_integrated_router = None
try:
    from app.api.v1x.payments_integrated import payments_router as payments_integrated_router
except Exception as e:
    print(f"Failed to import payments_integrated_router: {e}")

# ============================================================
# CREATE ALL DATABASE TABLES - MUST BE AFTER ALL MODEL IMPORTS
# ============================================================
print(f"[Init] Creating database tables...")
print(f"[Init] Models registered: {len(Base.metadata.tables)}")

try:
    # For SQLite, we can disable foreign key constraints temporarily
    if "sqlite" in str(engine.url).lower():
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            Base.metadata.create_all(bind=conn)
            conn.execute(text("PRAGMA foreign_keys=ON"))
    else:
        # For other databases, just create normally
        Base.metadata.create_all(bind=engine)
    
    print(f"[Init] OK Database initialized with {len(Base.metadata.tables)} tables")
except Exception as e:
    print(f"[Init] ERROR creating tables: {e}")
    import traceback
    traceback.print_exc()

# Configure error logging and exception handlers
from app.core.logging_middleware import setup_logging
from app.core.settings_middleware import MaintenanceModeMiddleware

app = FastAPI(title=getattr(settings, "APP_NAME", "SkillForge Global"))

# Setup logging after app is created
setup_logging(app)

# Add maintenance mode middleware (before CORS)
app.add_middleware(MaintenanceModeMiddleware)

# CORS - Allow multiple frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Mount v1 routers
app.include_router(auth.router,       prefix="/api/v1")
app.include_router(courses.router,    prefix="/api/v1")
app.include_router(chat.router,       prefix="/api/v1")
app.include_router(quizzes.router,    prefix="/api/v1")
app.include_router(progress.router,   prefix="/api/v1")
app.include_router(credits.router,    prefix="/api/v1")
app.include_router(subscribe.router,  prefix="/api/v1")
app.include_router(quiz_status.router,prefix="/api/v1")
app.include_router(paths.router,      prefix="/api/v1")
app.include_router(achievements.router, prefix="/api/v1")
app.include_router(dashboard.router,  prefix="/api/v1")

# Phase 3.3 Social Features routers
app.include_router(forum.router,      prefix="/api/v1")
app.include_router(messages.router,   prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(feed.router,       prefix="/api/v1")
app.include_router(profiles.router,   prefix="/api/v1")

# Phase 3.4 Learning Paths routers
app.include_router(v1_learning_paths.router, prefix="/api/v1")
app.include_router(certificates.router,   prefix="/api/v1")
app.include_router(skills.router,         prefix="/api/v1")
app.include_router(v1_recommendations.router, prefix="/api/v1")

# Phase 3.5 WebSocket routers
app.include_router(websocket.router, prefix="/api/v1")

# Admin routers
try:
    from app.api.v1.admin_quizzes import router as admin_quizzes
    app.include_router(admin_quizzes, prefix="/api/v1")
    print("Admin quizzes router mounted")
except Exception as e:
    print(f"Failed to mount admin_quizzes: {e}")

try:
    from app.api.v1x.session import router as session
except Exception as e:
    session = None
    print(f"Failed to import session: {e}")

# Mount session router for /api/session endpoints
try:
    if session:  # session was imported at the top
        app.include_router(session, prefix="/api")
        print("Session router mounted at /api/session")
except Exception as e:
    print(f"Failed to mount session router at /api/session: {e}")

from fastapi import APIRouter


def _mount_v1x_export(obj):
    """Mount a v1x export which may be either:
    - a module-like object exposing a `.router` attribute (common in this repo), or
    - an APIRouter instance exported directly (some v1x modules export the router)
    """
    if obj is None:
        return
    # prefer .router attribute when present
    router = getattr(obj, "router", obj)
    if isinstance(router, APIRouter):
        try:
            app.include_router(router, prefix="/api/v1x")
            print(f"Mounted v1x router: {getattr(router, 'tags', None)}")
        except Exception as e:
            print(f"Failed to mount router {router}: {e}")
    else:
        print(f"Skipping v1x export that is not a router: {obj}")


# Mount all v1x exports (modules or routers)
# Filter out None values to handle failed imports gracefully
# Note: session is mounted separately at /api/session, not included here
_exports = [x for x in (security_router, courses_db, courses_router, progress_db, quizzes_db, youtube_sync, coins_db, mentors, mentor_verification, account, payments, chat_files, payouts, subscriptions, connect, student_dashboard, mentor_portal, recordings, resumes, resume_ai, cover_letter, resume_comparison, linkedin_import, hiring, resume_import, marketplace, job_applications, job_notifications, job_calendar, resume_export, resume_templates, resume_analytics_events, resume_scoring, leaderboard, admin_metrics, admin_analytics, coding_practice, code_snippets, solution_sharing, user_profiles, solution_comments, social, learning_paths, premium_tiers, github_integration, advanced_dashboard, ai_hints, pwa, contests, notifications_v1x, code_executor, activity, badges, forums, recommendations, teams, search, interview, referral, admin_router, verification_router, analytics_router, payments_router_phase23, video_router, messaging_router, forum_router, payments_integrated_router, notifications_websocket) if x is not None]
for _export in _exports:
    _mount_v1x_export(_export)

# Mount WebSocket server
try:
    from app.api.websocket.chat import socket_app
    app.mount("/ws", socket_app)
    print("WebSocket server mounted at /ws")
except Exception as e:
    print(f"Failed to mount WebSocket server: {e}")

# Mount Collaboration WebSocket server
try:
    from app.api.websocket.collaboration import collab_socket_app
    app.mount("/collab", collab_socket_app)
    print("Collaboration WebSocket server mounted at /collab")
except Exception as e:
    print(f"Failed to mount Collaboration WebSocket server: {e}")


# Background scheduler for reminders
try:
    from app.services.scheduler import start_scheduler, shutdown_scheduler

    @app.on_event("startup")
    async def _start_scheduler():
        start_scheduler()

    @app.on_event("shutdown")
    async def _stop_scheduler():
        shutdown_scheduler()
    print("Scheduler lifecycle hooks registered")
except Exception as e:
    print(f"Failed to register scheduler: {e}")


