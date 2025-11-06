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
# import hiring models - alias JobApplication to avoid conflict with job tracker
from app.modelsx.hiring import Company, CompanyTeamMember, JobPosting, JobApplication as HiringJobApplication, Interview, TechnicalAssessment, BackgroundCheck, EducationVerification, EmploymentVerification, ReferenceCheck, JobOffer, HiringMetrics
# import job application tracking
from app.modelsx.job_application import JobApplication as JobApplicationTracker
