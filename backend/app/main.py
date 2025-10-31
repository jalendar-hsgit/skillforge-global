from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine

# import models so tables are registered on Base
from app.models import User, Progress as LegacyProgress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress, coins
# ensure CoinLedger table is registered (modelsx.coins defines CoinLedger)
from app.modelsx.coins import CoinLedger
# import mentor models
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview

# v1 routers (existing)
from app.api.v1 import auth, courses, chat, quizzes, progress, subscribe, quiz_status, paths

# Try to import optional v1x routers
try:
    from app.api.v1x import courses_db, progress_db, quizzes_db, youtube_sync, coins_db, mentors
except Exception as e:
    print(f"Error importing v1x modules: {e}")
    courses_db = None
    progress_db = None
    quizzes_db = None
    youtube_sync = None
    coins_db = None
    mentors = None

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
for _export in (courses_db, progress_db, quizzes_db, youtube_sync, coins_db, mentors):
    _mount_v1x_export(_export)



