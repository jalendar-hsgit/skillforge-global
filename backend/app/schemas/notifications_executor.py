"""Notification and code execution schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ NOTIFICATION SCHEMAS ============

class NotificationCreate(BaseModel):
    """Create notification request."""
    user_id: int
    notification_type: str
    title: str
    message: str
    priority: str = "normal"
    actor_id: Optional[int] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    action_url: Optional[str] = None
    extra_data: Dict[str, Any] = {}


class NotificationResponse(BaseModel):
    """Notification response."""
    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    priority: str
    is_read: bool
    actor_id: Optional[int] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    action_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preferences."""
    achievement_enabled: Optional[bool] = None
    challenge_enabled: Optional[bool] = None
    contest_enabled: Optional[bool] = None
    friend_activity_enabled: Optional[bool] = None
    mention_enabled: Optional[bool] = None
    comment_reply_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preferences response."""
    user_id: int
    achievement_enabled: bool
    challenge_enabled: bool
    contest_enabled: bool
    friend_activity_enabled: bool
    mention_enabled: bool
    comment_reply_enabled: bool
    push_enabled: bool
    email_enabled: bool
    in_app_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response."""
    unread_count: int
    notifications: List[NotificationResponse]


# ============ CODE EXECUTION SCHEMAS ============

class TestCaseInput(BaseModel):
    """Test case input for execution."""
    input_data: str
    expected_output: str
    is_sample: bool = False


class CodeExecutionRequest(BaseModel):
    """Execute code request."""
    code: str = Field(..., min_length=1)
    language: str
    challenge_id: Optional[int] = None
    contest_id: Optional[int] = None
    test_cases: List[TestCaseInput] = []
    time_limit_seconds: int = 5
    memory_limit_mb: int = 256


class TestCaseResultResponse(BaseModel):
    """Test case result response."""
    test_case_number: int
    status: str
    passed: bool
    input_data: str
    expected_output: str
    actual_output: Optional[str]
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[int]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class CodeExecutionResponse(BaseModel):
    """Code execution response."""
    id: int
    user_id: int
    language: str
    status: str
    test_cases_total: int
    test_cases_passed: int
    test_cases_failed: int
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[int]
    points_earned: int
    compilation_log: Optional[str]
    error_message: Optional[str]
    stdout: Optional[str]
    stderr: Optional[str]
    test_results: List[TestCaseResultResponse] = []
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ExecutionStatusResponse(BaseModel):
    """Check execution status response."""
    execution_id: int
    status: str
    progress: int  # 0-100
    test_cases_passed: int
    test_cases_total: int
    completed: bool


class ExecutionHistoryResponse(BaseModel):
    """Execution history entry."""
    id: int
    challenge_id: Optional[int]
    language: str
    status: str
    test_cases_passed: int
    test_cases_total: int
    points_earned: int
    created_at: datetime


class ExecutionEnvironmentResponse(BaseModel):
    """Execution environment info."""
    id: int
    name: str
    language: str
    language_version: str
    default_time_limit_seconds: int
    default_memory_limit_mb: int
    
    class Config:
        from_attributes = True


class ExecutionMetricsResponse(BaseModel):
    """Execution metrics response."""
    date: datetime
    total_executions: int
    successful_executions: int
    success_rate: float
    avg_execution_time_ms: float
    avg_memory_usage_mb: float
    language_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True
