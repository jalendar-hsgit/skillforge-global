from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ User Management ============

class UserListItem(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRole(BaseModel):
    role: str  # user, mentor, admin, superadmin


class UserSuspend(BaseModel):
    reason: Optional[str] = None


# ============ Dashboard Stats ============

class AdminDashboardStats(BaseModel):
    total_users: int
    total_mentors: int
    pending_mentor_applications: int
    total_sessions: int
    scheduled_sessions: int
    completed_sessions: int
    total_revenue: float
    active_users_30d: int


# ============ Audit Logs ============

class AdminLogResponse(BaseModel):
    id: int
    admin_user_id: Optional[int]
    admin_email: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminLogListResponse(BaseModel):
    logs: List[AdminLogResponse]
    total: int


# ============ Platform Settings ============

class PlatformSettings(BaseModel):
    platform_name: str = "SkillForge Global"
    support_email: str = "support@skillforge.com"
    allow_new_registrations: bool = True
    mentor_approval_required: bool = True
    maintenance_mode: bool = False
    featured_courses: List[str] = []
