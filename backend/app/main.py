from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.admin_log import AdminLog
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
# import resume models
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, Achievement, ResumeTemplate, AIProjectTemplate, ResumeAnalytics, ATSReport
# Ensure versioning/comparison tables are registered before create_all
from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
# import hiring models
# import job application tracking
from app.modelsx.job_application import JobApplication as JobApplicationTracker
# import marketplace models
from app.modelsx.order import Order, Coupon, CartItem
# import platform settings
from app.modelsx.platform_settings import PlatformSetting

# v1 routers (existing)
from app.api.v1 import auth, courses, progress, quizzes, chat, subscribe, quiz_status, paths, achievements, dashboard, credits

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
    from app.api.v1x.courses_db import router as courses_db
except Exception as e:
    print(f"Failed to import courses_db: {e}")

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

admin_mentors = None  # Deprecated router; replaced by unified app.api.v1x.admin

try:
    from app.api.v1x.admin import router as admin_router
except Exception as e:
    admin_router = None
    print(f"Failed to import admin router: {e}")

try:
    from app.api.v1x.payments_stub import router as payments
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
    from app.api.v1x.subscriptions_stub import router as subscriptions
except Exception as e:
    print(f"Failed to import subscriptions: {e}")

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
    from app.api.v1x.job_applications_stub import router as job_applications
except Exception as e:
    print(f"Failed to import job_applications: {e}")

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

try:
    from app.api.v1x.resume_templates import router as resume_templates
except Exception as e:
    print(f"Failed to import resume_templates: {e}")

try:
    from app.api.v1x.resume_analytics_events import router as resume_analytics_events
except Exception as e:
    print(f"Failed to import resume_analytics_events: {e}")

# App
app = FastAPI(title=getattr(settings, "APP_NAME", "SkillForge Global"))

# Configure error logging and exception handlers
from app.core.logging_middleware import setup_logging
from app.core.settings_middleware import MaintenanceModeMiddleware
setup_logging(app)

# Create tables
Base.metadata.create_all(bind=engine)

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

# Admin routers
try:
    from app.api.v1.admin_quizzes import router as admin_quizzes
    app.include_router(admin_quizzes, prefix="/api/v1")
    print("Admin quizzes router mounted")
except Exception as e:
    print(f"Failed to mount admin_quizzes: {e}")

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
for _export in (courses_db, progress_db, quizzes_db, youtube_sync, coins_db, mentors, payments, chat_files, payouts, subscriptions, connect, student_dashboard, mentor_portal, recordings, resumes, resume_ai, cover_letter, resume_comparison, linkedin_import, hiring, resume_import, marketplace, job_applications, job_notifications, job_calendar, resume_export, resume_templates, resume_analytics_events, admin_router):
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


