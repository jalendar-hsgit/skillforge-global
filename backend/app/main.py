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
# import mentor models
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
# import resume models
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate, Achievement, ResumeTemplate, AIProjectTemplate, ResumeAnalytics, ATSReport
# import hiring models
from app.modelsx.hiring import Company, CompanyTeamMember, JobPosting, JobApplication, Interview, TechnicalAssessment, BackgroundCheck, EducationVerification, EmploymentVerification, ReferenceCheck, JobOffer, HiringMetrics

# v1 routers (existing)
from app.api.v1 import auth, courses, chat, quizzes, progress, subscribe, quiz_status, paths

# Try to import optional v1x routers directly (bypass v1x __init__.py)
courses_db = None
progress_db = None
quizzes_db = None
youtube_sync = None
coins_db = None
mentors = None
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
    from app.api.v1x.progress_db import router as progress_db
except Exception as e:
    print(f"Failed to import progress_db: {e}")

try:
    from app.api.v1x.quizzes_db import router as quizzes_db
except Exception as e:
    print(f"Failed to import quizzes_db: {e}")

try:
    from app.api.v1x.youtube_sync import router as youtube_sync
except Exception as e:
    print(f"Failed to import youtube_sync: {e}")

try:
    from app.api.v1x.coins_db import router as coins_db
except Exception as e:
    print(f"Failed to import coins_db: {e}")

try:
    from app.api.v1x.mentors import router as mentors
except Exception as e:
    print(f"Failed to import mentors: {e}")

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

try:
    from app.api.v1x.connect import router as connect
except Exception as e:
    print(f"Failed to import connect: {e}")

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
    from app.api.v1x.hiring import router as hiring
except Exception as e:
    print(f"Failed to import hiring: {e}")

# App
app = FastAPI(title=getattr(settings, "APP_NAME", "SkillForge Global"))

# Create tables
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000"],
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
app.include_router(subscribe.router,  prefix="/api/v1")
app.include_router(quiz_status.router,prefix="/api/v1")
app.include_router(paths.router,      prefix="/api/v1")

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
for _export in (courses_db, progress_db, quizzes_db, youtube_sync, coins_db, mentors, payments, chat_files, payouts, subscriptions, connect, recordings, resumes, resume_ai, hiring):
    _mount_v1x_export(_export)

# Mount WebSocket server
try:
    from app.api.websocket.chat import socket_app
    app.mount("/ws", socket_app)
    print("WebSocket server mounted at /ws")
except Exception as e:
    print(f"Failed to mount WebSocket server: {e}")



