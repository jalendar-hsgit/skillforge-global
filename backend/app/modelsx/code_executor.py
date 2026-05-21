"""Code execution and testing framework."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base


class ExecutionLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GOLANG = "golang"
    RUST = "rust"
    RUBY = "ruby"


class ExecutionStatus(str, Enum):
    """Code execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ERROR = "error"
    MEMORY_EXCEEDED = "memory_exceeded"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"


class TestCaseStatus(str, Enum):
    """Individual test case result."""
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class CodeExecution(Base):
    """Record of code execution and testing."""
    __tablename__ = "code_executions"

    id = Column(Integer, primary_key=True)
    
    # Submission info
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=True)
    
    # Code
    code = Column(Text, nullable=False)
    language = Column(SQLEnum(ExecutionLanguage), nullable=False)
    
    # Execution settings
    time_limit_seconds = Column(Integer, default=5)
    memory_limit_mb = Column(Integer, default=256)
    
    # Execution results
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    
    # Test results
    test_cases_total = Column(Integer, default=0)
    test_cases_passed = Column(Integer, default=0)
    test_cases_failed = Column(Integer, default=0)
    
    # Compilation
    compiled = Column(Boolean, default=False)
    compilation_log = Column(Text, nullable=True)
    
    # Execution metrics
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Integer, nullable=True)
    cpu_time_ms = Column(Integer, nullable=True)
    
    # Output
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Score
    points_earned = Column(Integer, default=0)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="code_executions")
    challenge = relationship("CodingChallenge", backref="executions")
    test_results = relationship("TestCaseResult", backref="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CodeExecution(user_id={self.user_id}, status={self.status}, passed={self.test_cases_passed}/{self.test_cases_total})>"


class TestCaseResult(Base):
    """Individual test case execution result."""
    __tablename__ = "test_case_results"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("code_executions.id"), nullable=False, index=True)
    
    # Test case info
    test_case_number = Column(Integer, nullable=False)
    is_sample = Column(Boolean, default=False)  # Sample vs hidden
    
    # Input/Expected output
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    
    # Actual output
    actual_output = Column(Text, nullable=True)
    
    # Result
    status = Column(SQLEnum(TestCaseStatus), nullable=False)
    passed = Column(Boolean, default=False)
    
    # Metrics
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Integer, nullable=True)
    
    # Error info
    error_message = Column(Text, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TestCaseResult(execution_id={self.execution_id}, test_case={self.test_case_number}, passed={self.passed})>"


class ExecutionEnvironment(Base):
    """Execution environment configurations."""
    __tablename__ = "execution_environments"

    id = Column(Integer, primary_key=True)
    
    # Environment info
    name = Column(String(100), unique=True, nullable=False)
    language = Column(SQLEnum(ExecutionLanguage), unique=True, nullable=False)
    
    # Versions
    language_version = Column(String(50), nullable=False)
    runtime_version = Column(String(50), nullable=False)
    
    # Limits
    default_time_limit_seconds = Column(Integer, default=5)
    default_memory_limit_mb = Column(Integer, default=256)
    max_time_limit_seconds = Column(Integer, default=30)
    max_memory_limit_mb = Column(Integer, default=1024)
    
    # Commands
    compile_command = Column(Text, nullable=True)
    run_command = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionEnvironment(name={self.name}, language={self.language})>"


class ExecutionMetrics(Base):
    """Aggregate metrics for tracking execution system performance."""
    __tablename__ = "execution_metrics"

    id = Column(Integer, primary_key=True)
    
    # Daily metrics
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Counts
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    timeout_executions = Column(Integer, default=0)
    
    # Performance
    avg_execution_time_ms = Column(Float, default=0.0)
    avg_memory_usage_mb = Column(Float, default=0.0)
    
    # Languages
    language_breakdown = Column(JSON, default={})  # {language: count}
    
    # Success rate
    success_rate = Column(Float, default=0.0)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionMetrics(date={self.date}, total={self.total_executions}, success_rate={self.success_rate}%)>"
