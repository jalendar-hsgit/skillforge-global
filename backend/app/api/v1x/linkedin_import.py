"""
LinkedIn Profile Import API - OAuth integration and profile import
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import httpx
import json
from urllib.parse import urlencode

from app.core.db import get_db
from app.core.config import settings
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeSkill
from app.modelsx.resume_comparison import LinkedInImport
from pydantic import BaseModel


router = APIRouter(prefix="/linkedin-import", tags=["linkedin-import"])


# Schemas
class LinkedInAuthResponse(BaseModel):
    auth_url: str
    state: str


class LinkedInProfile(BaseModel):
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    profile_url: Optional[str]
    work_experiences: List[Dict]
    education: List[Dict]
    skills: List[str]


class ImportRequest(BaseModel):
    linkedin_id: Optional[str] = None
    create_new_resume: bool = True
    resume_id: Optional[int] = None  # If updating existing resume
    field_mappings: Optional[Dict] = None


class ImportResponse(BaseModel):
    resume_id: int
    imported_fields: List[str]
    message: str


# LinkedIn OAuth Configuration
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

# Note: These should be in settings, but providing defaults
LINKEDIN_CLIENT_ID = getattr(settings, "LINKEDIN_CLIENT_ID", "your_client_id")
LINKEDIN_CLIENT_SECRET = getattr(settings, "LINKEDIN_CLIENT_SECRET", "your_client_secret")
LINKEDIN_REDIRECT_URI = getattr(settings, "LINKEDIN_REDIRECT_URI", "http://localhost:3000/api/linkedin/callback")


# Helper Functions
def generate_auth_state(user_id: int) -> str:
    """Generate unique state for OAuth flow"""
    import hashlib
    import time
    return hashlib.sha256(f"{user_id}_{time.time()}".encode()).hexdigest()


async def exchange_code_for_token(code: str) -> Dict:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINKEDIN_REDIRECT_URI,
                "client_id": LINKEDIN_CLIENT_ID,
                "client_secret": LINKEDIN_CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        return response.json()


async def fetch_linkedin_profile(access_token: str) -> Dict:
    """Fetch LinkedIn profile data using access token"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # Fetch basic profile
        profile_response = await client.get(
            f"{LINKEDIN_API_BASE}/me",
            headers=headers
        )
        
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile")
        
        profile_data = profile_response.json()
        
        # Fetch email
        email_response = await client.get(
            f"{LINKEDIN_API_BASE}/emailAddress?q=members&projection=(elements*(handle~))",
            headers=headers
        )
        
        email_data = email_response.json() if email_response.status_code == 200 else {}
        
        # Note: Full profile access requires additional API permissions
        # This is a simplified version - production would need proper LinkedIn API setup
        
        return {
            "profile": profile_data,
            "email": email_data
        }


def parse_linkedin_profile(linkedin_data: Dict) -> LinkedInProfile:
    """Parse LinkedIn API response into our profile format"""
    profile = linkedin_data.get("profile", {})
    email_data = linkedin_data.get("email", {})
    
    # Extract email
    email = None
    if email_data.get("elements"):
        email = email_data["elements"][0].get("handle~", {}).get("emailAddress")
    
    # Extract name
    first_name = profile.get("localizedFirstName", "")
    last_name = profile.get("localizedLastName", "")
    full_name = f"{first_name} {last_name}".strip()
    
    # Note: Full profile parsing requires LinkedIn API permissions
    # This is a simplified version for demonstration
    
    return LinkedInProfile(
        full_name=full_name,
        email=email,
        phone=None,  # LinkedIn doesn't provide phone via API
        location=None,  # Would need additional API call
        headline=profile.get("localizedHeadline"),
        summary=None,  # Would need additional API call
        profile_url=f"https://www.linkedin.com/in/{profile.get('vanityName', '')}",
        work_experiences=[],  # Would need additional API call
        education=[],  # Would need additional API call
        skills=[]  # Would need additional API call
    )


def create_resume_from_linkedin(profile: LinkedInProfile, user_id: int, db: Session) -> Resume:
    """Create a new resume from LinkedIn profile data"""
    # Create resume
    resume = Resume(
        user_id=user_id,
        title=f"LinkedIn Import - {datetime.now().strftime('%Y-%m-%d')}",
        template_id="modern",
        full_name=profile.full_name,
        email=profile.email,
        phone=profile.phone,
        location=profile.location,
        linkedin_url=profile.profile_url,
        summary=profile.summary or profile.headline
    )
    
    db.add(resume)
    db.flush()
    
    # Add work experiences
    for i, exp in enumerate(profile.work_experiences):
        work_exp = WorkExperience(
            resume_id=resume.id,
            company=exp.get("company", ""),
            position=exp.get("title", ""),
            location=exp.get("location", ""),
            start_date=exp.get("start_date", ""),
            end_date=exp.get("end_date", "Present"),
            is_current=exp.get("is_current", False),
            description=exp.get("description", ""),
            order_index=i
        )
        db.add(work_exp)
    
    # Add education
    for i, edu in enumerate(profile.education):
        education = Education(
            resume_id=resume.id,
            institution=edu.get("school", ""),
            degree=edu.get("degree", ""),
            field_of_study=edu.get("field_of_study", ""),
            start_date=edu.get("start_date", ""),
            end_date=edu.get("end_date", ""),
            order_index=i
        )
        db.add(education)
    
    # Add skills
    for i, skill_name in enumerate(profile.skills[:20]):  # Limit to 20 skills
        skill = ResumeSkill(
            resume_id=resume.id,
            skill_name=skill_name,
            proficiency_level="Intermediate",
            order_index=i
        )
        db.add(skill)
    
    db.commit()
    db.refresh(resume)
    
    return resume


# Endpoints
@router.get("/auth", response_model=LinkedInAuthResponse)
def initiate_linkedin_auth(
    current_user: User = Depends(get_current_user)
):
    """Initiate LinkedIn OAuth flow"""
    state = generate_auth_state(current_user.id)
    
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": "r_liteprofile r_emailaddress"  # Basic scopes
    }
    
    auth_url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.get("/callback")
async def linkedin_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Handle LinkedIn OAuth callback"""
    # Exchange code for token
    token_data = await exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    
    # Fetch profile
    linkedin_data = await fetch_linkedin_profile(access_token)
    profile = parse_linkedin_profile(linkedin_data)
    
    # Save or update LinkedIn import record
    linkedin_import = db.query(LinkedInImport).filter(
        LinkedInImport.user_id == current_user.id
    ).first()
    
    if not linkedin_import:
        linkedin_import = LinkedInImport(
            user_id=current_user.id,
            linkedin_id=linkedin_data.get("profile", {}).get("id"),
            access_token=access_token,  # Note: Should be encrypted in production
            refresh_token=refresh_token,
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            profile_url=profile.profile_url,
            profile_data=linkedin_data,
            import_count=0
        )
        db.add(linkedin_import)
    else:
        linkedin_import.access_token = access_token
        linkedin_import.refresh_token = refresh_token
        linkedin_import.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        linkedin_import.profile_data = linkedin_data
        linkedin_import.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Redirect to frontend with success
    return RedirectResponse(url=f"{settings.FRONTEND_ORIGIN}/dashboard/resume?linkedin_connected=true")


@router.post("/import", response_model=ImportResponse)
async def import_linkedin_profile(
    request: ImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import LinkedIn profile data into resume"""
    # Get LinkedIn import record
    linkedin_import = db.query(LinkedInImport).filter(
        LinkedInImport.user_id == current_user.id,
        LinkedInImport.is_active == True
    ).first()
    
    if not linkedin_import:
        raise HTTPException(
            status_code=404,
            detail="LinkedIn account not connected. Please connect first."
        )
    
    # Check token expiry
    if linkedin_import.token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="LinkedIn token expired. Please reconnect."
        )
    
    # Parse profile from stored data
    profile = parse_linkedin_profile(linkedin_import.profile_data)
    
    imported_fields = []
    
    if request.create_new_resume:
        # Create new resume from LinkedIn data
        resume = create_resume_from_linkedin(profile, current_user.id, db)
        imported_fields = ["full_name", "email", "headline", "work_experiences", "education", "skills"]
    else:
        # Update existing resume
        if not request.resume_id:
            raise HTTPException(status_code=400, detail="resume_id required when create_new_resume is False")
        
        resume = db.query(Resume).filter(
            Resume.id == request.resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Update fields based on field_mappings or default mappings
        if profile.full_name and not resume.full_name:
            resume.full_name = profile.full_name
            imported_fields.append("full_name")
        
        if profile.email and not resume.email:
            resume.email = profile.email
            imported_fields.append("email")
        
        if profile.profile_url:
            resume.linkedin_url = profile.profile_url
            imported_fields.append("linkedin_url")
        
        db.commit()
    
    # Update import statistics
    linkedin_import.import_count += 1
    linkedin_import.last_import_at = datetime.utcnow()
    db.commit()
    
    return {
        "resume_id": resume.id,
        "imported_fields": imported_fields,
        "message": f"Successfully imported LinkedIn profile. {len(imported_fields)} fields updated."
    }


@router.get("/status")
def get_linkedin_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check LinkedIn connection status"""
    linkedin_import = db.query(LinkedInImport).filter(
        LinkedInImport.user_id == current_user.id,
        LinkedInImport.is_active == True
    ).first()
    
    if not linkedin_import:
        return {
            "connected": False,
            "profile_url": None,
            "last_import": None,
            "import_count": 0
        }
    
    is_expired = linkedin_import.token_expires_at < datetime.utcnow()
    
    return {
        "connected": True,
        "expired": is_expired,
        "profile_url": linkedin_import.profile_url,
        "last_import": linkedin_import.last_import_at,
        "import_count": linkedin_import.import_count,
        "auto_sync": linkedin_import.auto_sync
    }


@router.delete("/disconnect")
def disconnect_linkedin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect LinkedIn account"""
    linkedin_import = db.query(LinkedInImport).filter(
        LinkedInImport.user_id == current_user.id
    ).first()
    
    if not linkedin_import:
        raise HTTPException(status_code=404, detail="LinkedIn account not connected")
    
    linkedin_import.is_active = False
    linkedin_import.access_token = None
    linkedin_import.refresh_token = None
    db.commit()
    
    return {"message": "LinkedIn account disconnected successfully"}


@router.post("/refresh-profile")
async def refresh_linkedin_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refresh LinkedIn profile data from API"""
    linkedin_import = db.query(LinkedInImport).filter(
        LinkedInImport.user_id == current_user.id,
        LinkedInImport.is_active == True
    ).first()
    
    if not linkedin_import:
        raise HTTPException(status_code=404, detail="LinkedIn account not connected")
    
    if linkedin_import.token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="LinkedIn token expired. Please reconnect.")
    
    # Fetch fresh profile data
    linkedin_data = await fetch_linkedin_profile(linkedin_import.access_token)
    
    # Update stored data
    linkedin_import.profile_data = linkedin_data
    linkedin_import.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "LinkedIn profile refreshed successfully"}
