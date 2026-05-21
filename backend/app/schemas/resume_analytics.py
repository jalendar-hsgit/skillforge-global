from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ATSScore(BaseModel):
    score: int
    date: datetime

class ResumeAnalyticsBase(BaseModel):
    resume_id: UUID
    user_id: UUID
    views: int = 0
    downloads: int = 0
    shares: int = 0
    template_id: Optional[str] = None
    ats_scores: List[ATSScore] = []
    last_viewed: Optional[datetime] = None
    last_downloaded: Optional[datetime] = None
    last_shared: Optional[datetime] = None

class ResumeAnalyticsCreate(ResumeAnalyticsBase):
    pass

class ResumeAnalyticsUpdate(ResumeAnalyticsBase):
    pass

class ResumeAnalyticsOut(ResumeAnalyticsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
