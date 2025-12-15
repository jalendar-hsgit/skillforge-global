"""
Advanced Coding Practice & Simulator Models
Real-time practice environment for multiple languages, cloud platforms, and technologies
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.core.db import Base


class PracticeCategory(str, Enum):
    """Categories for coding practice"""
    ALGORITHMS = "algorithms"
    DATA_STRUCTURES = "data_structures"
    WEB_DEVELOPMENT = "web_development"
    CLOUD_AWS = "cloud_aws"
    CLOUD_AZURE = "cloud_azure"
    CLOUD_GCP = "cloud_gcp"
    DEVOPS = "devops"
    DATABASE = "database"
    SECURITY = "security"
    SYSTEM_DESIGN = "system_design"
    MACHINE_LEARNING = "machine_learning"
    MOBILE_DEVELOPMENT = "mobile_development"


class PracticeDifficulty(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class LanguageSupport(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SQL = "sql"
    BASH = "bash"
    TERRAFORM = "terraform"
    YAML = "yaml"


class SimulatorType(str, Enum):
    """Types of simulators"""
    CODE_EDITOR = "code_editor"
    CLOUD_CONSOLE = "cloud_console"
    TERMINAL = "terminal"
    DATABASE_QUERY = "database_query"
    API_PLAYGROUND = "api_playground"
    CONTAINER_LAB = "container_lab"
    KUBERNETES_CLUSTER = "kubernetes_cluster"
    NETWORK_SIMULATOR = "network_simulator"


class CodingChallenge(Base):
    """
    Coding challenges and practice problems
    """
    __tablename__ = "coding_challenges"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Categorization
    category = Column(String, nullable=False, index=True)
    difficulty = Column(String, nullable=False, index=True)
    tags = Column(JSON)  # ["arrays", "sorting", "aws", "lambda"]
    
    # Challenge details
    problem_statement = Column(Text, nullable=False)
    constraints = Column(Text)
    examples = Column(JSON)  # [{"input": "...", "output": "...", "explanation": "..."}]
    
    # Solution & Testing
    starter_code = Column(JSON)  # {"python": "def solution():", "javascript": "function solution(){}"}
    test_cases = Column(JSON)  # [{"input": ..., "expected": ..., "hidden": false}]
    solution_explanation = Column(Text)
    
    # Language support
    supported_languages = Column(JSON)  # ["python", "javascript", "java"]
    
    # Simulator configuration
    simulator_type = Column(String, default="code_editor")
    simulator_config = Column(JSON)  # Custom config for each simulator type
    
    # Environment setup
    environment_template = Column(Text)  # Docker/cloud setup if needed
    requires_cloud_access = Column(Boolean, default=False)
    cloud_provider = Column(String)  # "aws", "azure", "gcp"
    
    # Metadata
    time_limit_seconds = Column(Integer, default=30)
    memory_limit_mb = Column(Integer, default=256)
    estimated_time_minutes = Column(Integer)
    
    # Gamification
    points = Column(Integer, default=10)
    coins_reward = Column(Integer, default=5)
    is_premium = Column(Boolean, default=False)
    
    # Stats
    total_attempts = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_completion_time = Column(Integer)  # seconds
    
    # Relations
    # created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Disabled FK for now
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("CodingSubmission", back_populates="challenge", cascade="all, delete-orphan")
    hints = relationship("ChallengeHint", back_populates="challenge", cascade="all, delete-orphan")


class ChallengeHint(Base):
    """
    Progressive hints for challenges
    """
    __tablename__ = "challenge_hints"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    
    hint_text = Column(Text, nullable=False)
    hint_order = Column(Integer, default=1)
    cost_coins = Column(Integer, default=2)  # Coins to unlock hint
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship("CodingChallenge", back_populates="hints")


class CodingSubmission(Base):
    """
    User submissions for coding challenges
    """
    __tablename__ = "coding_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Submission details
    language = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    
    # Execution results
    status = Column(String, nullable=False)  # "pending", "running", "success", "failed", "error"
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    
    # Performance metrics
    execution_time_ms = Column(Integer)
    memory_used_mb = Column(Float)
    
    # Test results
    test_results = Column(JSON)  # Detailed results for each test case
    error_message = Column(Text)
    stdout = Column(Text)
    stderr = Column(Text)
    
    # Scoring
    score = Column(Float, default=0.0)
    is_optimal = Column(Boolean, default=False)
    coins_earned = Column(Integer, default=0)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    executed_at = Column(DateTime)
    
    # Relationships
    challenge = relationship("CodingChallenge", back_populates="submissions")


class SimulatorEnvironment(Base):
    """
    Pre-configured simulator environments for practice
    """
    __tablename__ = "simulator_environments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String, nullable=False)
    description = Column(Text)
    simulator_type = Column(String, nullable=False)
    
    # Environment configuration
    base_image = Column(String)  # Docker image
    environment_variables = Column(JSON)
    ports = Column(JSON)  # {"http": 8080, "ssh": 22}
    
    # Cloud configuration
    cloud_provider = Column(String)  # "aws", "azure", "gcp"
    cloud_services = Column(JSON)  # ["lambda", "s3", "dynamodb"]
    terraform_template = Column(Text)
    
    # Access control
    is_premium = Column(Boolean, default=False)
    max_session_minutes = Column(Integer, default=60)
    
    # Resource limits
    cpu_limit = Column(Float, default=1.0)
    memory_limit_mb = Column(Integer, default=512)
    disk_limit_mb = Column(Integer, default=1024)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("PracticeSession", back_populates="environment", cascade="all, delete-orphan")


class PracticeSession(Base):
    """
    Active practice sessions for real-time coding
    """
    __tablename__ = "practice_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    environment_id = Column(Integer, ForeignKey("simulator_environments.id"))
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"))
    
    # Session details
    session_token = Column(String, unique=True, index=True)
    status = Column(String, default="active")  # "active", "paused", "completed", "expired"
    
    # Container/VM info
    container_id = Column(String)
    ip_address = Column(String)
    access_url = Column(String)
    
    # Session data
    current_code = Column(Text)
    files = Column(JSON)  # {"filename": "content"}
    terminal_history = Column(JSON)
    
    # Time tracking
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    environment = relationship("SimulatorEnvironment", back_populates="sessions")


class CloudLabScenario(Base):
    """
    Hands-on cloud platform scenarios (AWS, Azure, GCP)
    """
    __tablename__ = "cloud_lab_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    
    # Cloud details
    cloud_provider = Column(String, nullable=False)  # "aws", "azure", "gcp"
    services_used = Column(JSON)  # ["lambda", "s3", "api-gateway"]
    
    # Scenario setup
    objective = Column(Text)
    instructions = Column(Text)
    architecture_diagram_url = Column(String)
    
    # Infrastructure as Code
    terraform_code = Column(Text)
    cloudformation_template = Column(Text)
    arm_template = Column(Text)
    
    # Validation
    validation_script = Column(Text)  # Script to check if scenario is completed
    success_criteria = Column(JSON)
    
    # Difficulty & rewards
    difficulty = Column(String, default="medium")
    estimated_time_minutes = Column(Integer)
    points_reward = Column(Integer, default=50)
    coins_reward = Column(Integer, default=20)
    
    # Access
    is_premium = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodingAchievement(Base):
    """
    Achievement badges for coding practice milestones
    """
    __tablename__ = "coding_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Achievement details
    key = Column(String, unique=True, index=True, nullable=False)  # e.g., "first_perfect", "streak_7"
    title = Column(String, nullable=False)
    description = Column(Text)
    icon_url = Column(String)
    badge_color = Column(String)  # color class for display
    
    # Reward details
    points = Column(Integer, default=10)
    coins = Column(Integer, default=5)
    
    # Criteria
    criteria_type = Column(String, nullable=False)  # "perfect_solutions", "streak", "challenges_solved", etc.
    criteria_value = Column(Integer)  # e.g., 1 for first, 7 for 7-day streak
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserCodingAchievement(Base):
    """
    Track which achievements each user has unlocked
    """
    __tablename__ = "user_coding_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("coding_achievements.id"), nullable=False)
    
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="coding_achievements")
    achievement = relationship("CodingAchievement")
    
    # Unique constraint - user can't unlock same achievement twice
    __table_args__ = (UniqueConstraint('user_id', 'achievement_id', name='user_achievement_unique'),)


class UserHintUnlock(Base):
    """
    Track which hints have been unlocked by each user
    """
    __tablename__ = "user_hint_unlocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hint_id = Column(Integer, ForeignKey("challenge_hints.id"), nullable=False)
    
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    coins_spent = Column(Integer, default=0)  # How many coins were spent to unlock
    
    # Relationships
    user = relationship("User", backref="hint_unlocks")
    hint = relationship("ChallengeHint")
    
    # Unique constraint - user can't unlock same hint twice
    __table_args__ = (UniqueConstraint('user_id', 'hint_id', name='user_hint_unique'),)


class DailyChallenge(Base):
    """
    Daily rotating challenge for users to solve
    """
    __tablename__ = "daily_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, unique=True, index=True, nullable=False)  # Date of the daily challenge
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    
    # Bonus rewards for solving the daily challenge
    bonus_coins = Column(Integer, default=20)
    bonus_points = Column(Integer, default=25)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship("CodingChallenge")


class UserDailyChallengeStreak(Base):
    """
    Track user's daily challenge solving streaks
    """
    __tablename__ = "user_daily_challenge_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    current_streak = Column(Integer, default=0)  # Number of consecutive days
    longest_streak = Column(Integer, default=0)  # Best streak ever
    last_solved_date = Column(DateTime)  # Last day they solved daily challenge
    total_solved = Column(Integer, default=0)  # Total daily challenges solved
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="daily_streak")
