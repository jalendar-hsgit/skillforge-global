from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your app's Base and models
from app.core.db import Base
from app.core.config import settings

# Import all models so they're registered with Base.metadata
from app.models import User, Progress, QuizAttempt, CreditLedger, Subscriber
from app.modelsx import Course, Video, Quiz, QuizQuestion, VideoProgress
from app.modelsx.coins import CoinLedger
from app.modelsx.mentor import Mentor, MentorSession, MentorAvailability, MentorMessage, MentorReview
from app.modelsx.payout import MentorPayout, MentorEarning
from app.modelsx.subscription import Subscription, PlanFeature, SubscriptionEvent
from app.modelsx.stripe_connect import MentorStripeAccount
from app.modelsx.chat_file import MentorChatFile
from app.modelsx.resume import (
    Resume, WorkExperience, Education, ResumeProject, ResumeSkill, 
    ResumeCertificate, ResumeAchievement, ResumeTemplate, AIProjectTemplate, 
    ResumeAnalytics, ATSReport
)
from app.modelsx.job_application import JobApplication
from app.modelsx.hiring import (
    Company, CompanyTeamMember, JobPosting, HiringJobApplication, Interview,
    TechnicalAssessment, BackgroundCheck, EducationVerification, EmploymentVerification,
    ReferenceCheck, JobOffer, HiringMetrics
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with DATABASE_URL from settings or environment
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
