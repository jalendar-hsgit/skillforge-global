from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine

# import ALL models BEFORE create_all
from app.models import User, Progress, QuizAttempt, CreditLedger, Subscriber

# import routers
from app.api.v1 import auth, courses, chat, quizzes, progress, subscribe, quiz_status

app = FastAPI(title=settings.APP_NAME)

# create tables on boot
Base.metadata.create_all(bind=engine)

# CORS for local dev
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

# mount routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(quizzes.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(subscribe.router, prefix="/api/v1")
app.include_router(quiz_status.router, prefix="/api/v1")
