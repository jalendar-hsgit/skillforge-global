"""
Pydantic schemas for Resume API
"""
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


# Work Experience Schemas
class WorkExperienceBase(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullet_points: List[str] = []


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceOut(WorkExperienceBase):
    id: int
    order_index: int
    
    class Config:
        from_attributes = True


# Education Schemas
class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = []


class EducationCreate(EducationBase):
    pass


class EducationOut(EducationBase):
    id: int
    order_index: int
    
    class Config:
        from_attributes = True


# Project Schemas
class ResumeProjectBase(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = []
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    impact_metrics: Dict[str, str] = {}


class ResumeProjectCreate(ResumeProjectBase):
    pass


class ResumeProjectOut(ResumeProjectBase):
    id: int
    is_ai_generated: bool
    order_index: int
    
    class Config:
        from_attributes = True


# Skill Schemas
class ResumeSkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[int] = None


class ResumeSkillCreate(ResumeSkillBase):
    pass


class ResumeSkillOut(ResumeSkillBase):
    id: int
    is_verified: bool
    order_index: int
    
    class Config:
        from_attributes = True


# Certificate Schemas
class ResumeCertificateBase(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class ResumeCertificateCreate(ResumeCertificateBase):
    quiz_id: Optional[int] = None
    course_id: Optional[int] = None


class ResumeCertificateOut(ResumeCertificateBase):
    id: int
    quiz_id: Optional[int]
    course_id: Optional[int]
    is_verified: bool
    verification_qr_code: Optional[str]
    order_index: int
    
    class Config:
        from_attributes = True


# Achievement Schemas
class AchievementBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None


class AchievementCreate(AchievementBase):
    pass


class AchievementOut(AchievementBase):
    id: int
    order_index: int
    
    class Config:
        from_attributes = True


# Resume Schemas
class ResumeBase(BaseModel):
    title: str
    template_id: str = "modern"
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    summary: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    template_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    summary: Optional[str] = None
    is_primary: Optional[bool] = None
    is_public: Optional[bool] = None
    # Customization fields (optional)
    font_family: Optional[str] = None
    color_theme: Optional[str] = None
    picture_style: Optional[str] = None
    layout: Optional[str] = None
    accent_color: Optional[str] = None
    text_color: Optional[str] = None
    heading_color: Optional[str] = None
    line_spacing: Optional[float] = None
    font_size: Optional[int] = None
    heading_size: Optional[int] = None
    show_icons: Optional[bool] = None


class ResumeOut(ResumeBase):
    id: int
    user_id: int
    is_primary: bool
    ats_score: float
    keywords: Optional[List[str]] = []
    views: int
    downloads: int
    shares: int
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    work_experiences: List[WorkExperienceOut] = []
    education: List[EducationOut] = []
    projects: List[ResumeProjectOut] = []
    skills: List[ResumeSkillOut] = []
    certificates: List[ResumeCertificateOut] = []
    achievements: List[AchievementOut] = []
    
    class Config:
        from_attributes = True


class ResumeListOut(BaseModel):
    id: int
    title: str
    template_id: str
    ats_score: float
    is_primary: bool
    views: int
    downloads: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# AI Assistance Schemas
class AIBulletPointRequest(BaseModel):
    position: str
    company: str
    responsibilities: List[str]
    achievements: Optional[List[str]] = []


class AIBulletPointResponse(BaseModel):
    bullet_points: List[str]
    suggestions: List[str]


class AISummaryRequest(BaseModel):
    experience_years: int
    title: str
    skills: List[str]
    target_role: Optional[str] = None


class AISummaryResponse(BaseModel):
    summary: str
    variations: List[str]


class AIProjectRequest(BaseModel):
    skills: List[str]
    experience_level: str  # "beginner", "intermediate", "advanced"
    interests: List[str] = []
    time_available_hours: Optional[int] = None


class AIProjectResponse(BaseModel):
    title: str
    description: str
    tech_stack: List[str]
    features: List[str]
    estimated_hours: int
    difficulty: str
    github_template_url: Optional[str]


# ATS Optimization Schemas
class ATSAnalysisRequest(BaseModel):
    resume_id: int
    job_description: Optional[str] = None


class ATSAnalysisResponse(BaseModel):
    score: float
    formatting_score: float
    keywords_score: float
    content_score: float
    suggestions: List[str]
    missing_keywords: List[str]
    flagged_issues: List[Dict[str, str]]
    recommendations: List[str]


# Template Schemas
class TemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    thumbnail_url: Optional[str]
    is_ats_friendly: bool
    popularity: int
    
    class Config:
        from_attributes = True


# Analytics Schemas
class ResumeAnalyticsOut(BaseModel):
    total_views: int
    total_downloads: int
    total_shares: int
    ats_score_history: List[Dict[str, Any]]
    view_trend: List[Dict[str, Any]]
    top_keywords: List[str]
    
    class Config:
        from_attributes = True
