"""
Resume Comparison API - Compare versions, track history, identify best performing version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import difflib
import json

from app.core.db import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeSkill, ResumeProject
from app.modelsx.resume_comparison import ResumeVersion, ResumeComparison
from pydantic import BaseModel


router = APIRouter(prefix="/resume-comparison", tags=["resume-comparison"])


# Schemas
class CreateVersionRequest(BaseModel):
    resume_id: int
    version_name: Optional[str] = None
    description: Optional[str] = None


class VersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    version_name: Optional[str]
    description: Optional[str]
    ats_score: Optional[float]
    word_count: Optional[int]
    skill_count: Optional[int]
    applications_sent: int
    responses_received: int
    interviews_secured: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ComparisonRequest(BaseModel):
    base_version_id: int
    compared_version_id: int


class ComparisonResponse(BaseModel):
    id: int
    base_version: VersionResponse
    compared_version: VersionResponse
    differences: dict
    score_change: float
    metrics_change: dict
    recommendations: List[str]
    better_version: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreHistoryResponse(BaseModel):
    version_id: int
    version_name: Optional[str]
    ats_score: Optional[float]
    created_at: datetime


# Helper Functions
def calculate_resume_metrics(resume_data: dict) -> dict:
    """Calculate metrics from resume data"""
    word_count = 0
    if resume_data.get("summary"):
        word_count += len(resume_data["summary"].split())
    
    for exp in resume_data.get("work_experiences", []):
        if exp.get("description"):
            word_count += len(exp["description"].split())
        for bullet in exp.get("bullet_points", []):
            word_count += len(bullet.split())
    
    skill_count = len(resume_data.get("skills", []))
    section_count = sum([
        1 if resume_data.get("summary") else 0,
        1 if resume_data.get("work_experiences") else 0,
        1 if resume_data.get("education") else 0,
        1 if resume_data.get("skills") else 0,
        1 if resume_data.get("projects") else 0,
        1 if resume_data.get("certificates") else 0,
    ])
    
    # Calculate years of experience
    experience_years = 0.0
    for exp in resume_data.get("work_experiences", []):
        # Simplified calculation - could be enhanced
        experience_years += 1.0
    
    return {
        "word_count": word_count,
        "skill_count": skill_count,
        "section_count": section_count,
        "experience_years": experience_years
    }


def generate_diff(base_data: dict, compared_data: dict) -> dict:
    """Generate detailed differences between two resume versions"""
    differences = {
        "added": [],
        "removed": [],
        "modified": []
    }
    
    # Compare summary
    if base_data.get("summary") != compared_data.get("summary"):
        differences["modified"].append({
            "section": "summary",
            "field": "professional_summary",
            "old_value": base_data.get("summary", ""),
            "new_value": compared_data.get("summary", "")
        })
    
    # Compare work experiences
    base_exp_count = len(base_data.get("work_experiences", []))
    compared_exp_count = len(compared_data.get("work_experiences", []))
    
    if compared_exp_count > base_exp_count:
        differences["added"].append({
            "section": "work_experience",
            "count": compared_exp_count - base_exp_count
        })
    elif compared_exp_count < base_exp_count:
        differences["removed"].append({
            "section": "work_experience",
            "count": base_exp_count - compared_exp_count
        })
    
    # Compare skills
    base_skills = set([s.get("name", "") for s in base_data.get("skills", [])])
    compared_skills = set([s.get("name", "") for s in compared_data.get("skills", [])])
    
    new_skills = compared_skills - base_skills
    removed_skills = base_skills - compared_skills
    
    if new_skills:
        differences["added"].append({
            "section": "skills",
            "items": list(new_skills)
        })
    if removed_skills:
        differences["removed"].append({
            "section": "skills",
            "items": list(removed_skills)
        })
    
    return differences


def generate_recommendations(base_version: ResumeVersion, compared_version: ResumeVersion) -> List[str]:
    """Generate AI recommendations based on comparison"""
    recommendations = []
    
    # Score comparison
    score_diff = (compared_version.ats_score or 0) - (base_version.ats_score or 0)
    if score_diff > 0:
        recommendations.append(f"✅ ATS score improved by {score_diff:.1f} points - great progress!")
    elif score_diff < 0:
        recommendations.append(f"⚠️ ATS score decreased by {abs(score_diff):.1f} points - review recent changes")
    
    # Word count comparison
    if compared_version.word_count and base_version.word_count:
        word_diff = compared_version.word_count - base_version.word_count
        if word_diff > 100:
            recommendations.append("📝 Resume became longer - ensure content stays concise")
        elif word_diff < -100:
            recommendations.append("✂️ Resume became shorter - verify no critical info was lost")
    
    # Skills comparison
    if compared_version.skill_count and base_version.skill_count:
        skill_diff = compared_version.skill_count - base_version.skill_count
        if skill_diff > 0:
            recommendations.append(f"⚡ Added {skill_diff} new skills - good for ATS keyword matching")
        elif skill_diff < 0:
            recommendations.append(f"⚠️ Removed {abs(skill_diff)} skills - ensure they weren't relevant")
    
    # Performance metrics
    if compared_version.interviews_secured > base_version.interviews_secured:
        recommendations.append("🎯 This version is securing more interviews - keep using it!")
    
    return recommendations


# Endpoints
@router.post("/versions", response_model=VersionResponse)
def create_version(
    request: CreateVersionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a snapshot of current resume as a version"""
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get latest version number
    latest_version = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == request.resume_id
    ).order_by(desc(ResumeVersion.version_number)).first()
    
    next_version_number = (latest_version.version_number + 1) if latest_version else 1
    
    # Collect resume data
    resume_data = {
        "id": resume.id,
        "title": resume.title,
        "full_name": resume.full_name,
        "email": resume.email,
        "phone": resume.phone,
        "location": resume.location,
        "linkedin_url": resume.linkedin_url,
        "summary": resume.summary,
        "work_experiences": [
            {
                "company": exp.company,
                "position": exp.position,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description,
                "bullet_points": exp.bullet_points or []
            }
            for exp in resume.work_experiences
        ],
        "education": [
            {
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date,
                "end_date": edu.end_date
            }
            for edu in resume.education
        ],
        "skills": [
            {"name": skill.skill_name, "level": skill.proficiency_level}
            for skill in resume.skills
        ],
        "projects": [
            {
                "name": proj.project_name,
                "description": proj.description,
                "technologies": proj.technologies
            }
            for proj in resume.projects
        ]
    }
    
    # Calculate metrics
    metrics = calculate_resume_metrics(resume_data)
    
    # Create version
    version = ResumeVersion(
        resume_id=request.resume_id,
        user_id=current_user.id,
        version_number=next_version_number,
        version_name=request.version_name or f"Version {next_version_number}",
        description=request.description,
        snapshot_data=resume_data,
        ats_score=resume.ats_score,
        word_count=metrics["word_count"],
        section_count=metrics["section_count"],
        skill_count=metrics["skill_count"],
        experience_years=metrics["experience_years"]
    )
    
    db.add(version)
    db.commit()
    db.refresh(version)
    
    return version


@router.get("/versions/{resume_id}", response_model=List[VersionResponse])
def list_versions(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all versions of a resume"""
    # Verify ownership
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    versions = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id
    ).order_by(desc(ResumeVersion.created_at)).all()
    
    return versions


@router.post("/compare", response_model=ComparisonResponse)
def compare_versions(
    request: ComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare two resume versions"""
    # Get both versions
    base_version = db.query(ResumeVersion).filter(
        ResumeVersion.id == request.base_version_id,
        ResumeVersion.user_id == current_user.id
    ).first()
    
    compared_version = db.query(ResumeVersion).filter(
        ResumeVersion.id == request.compared_version_id,
        ResumeVersion.user_id == current_user.id
    ).first()
    
    if not base_version or not compared_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    if base_version.resume_id != compared_version.resume_id:
        raise HTTPException(status_code=400, detail="Versions must be from the same resume")
    
    # Generate differences
    differences = generate_diff(base_version.snapshot_data, compared_version.snapshot_data)
    
    # Calculate metrics change
    metrics_change = {
        "word_count_change": (compared_version.word_count or 0) - (base_version.word_count or 0),
        "skill_count_change": (compared_version.skill_count or 0) - (base_version.skill_count or 0),
        "ats_score_change": (compared_version.ats_score or 0) - (base_version.ats_score or 0)
    }
    
    # Determine better version
    score_diff = (compared_version.ats_score or 0) - (base_version.ats_score or 0)
    better_version = "compared" if score_diff > 0 else "base" if score_diff < 0 else "equal"
    
    # Generate recommendations
    recommendations = generate_recommendations(base_version, compared_version)
    
    # Save comparison
    comparison = ResumeComparison(
        user_id=current_user.id,
        resume_id=base_version.resume_id,
        base_version_id=request.base_version_id,
        compared_version_id=request.compared_version_id,
        differences=differences,
        score_change=metrics_change["ats_score_change"],
        metrics_change=metrics_change,
        recommendations=recommendations,
        better_version=better_version
    )
    
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    
    return {
        "id": comparison.id,
        "base_version": base_version,
        "compared_version": compared_version,
        "differences": differences,
        "score_change": comparison.score_change,
        "metrics_change": metrics_change,
        "recommendations": recommendations,
        "better_version": better_version,
        "created_at": comparison.created_at
    }


@router.get("/score-history/{resume_id}", response_model=List[ScoreHistoryResponse])
def get_score_history(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ATS score history for a resume"""
    # Verify ownership
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    versions = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id
    ).order_by(ResumeVersion.created_at).all()
    
    return [
        {
            "version_id": v.id,
            "version_name": v.version_name,
            "ats_score": v.ats_score,
            "created_at": v.created_at
        }
        for v in versions
    ]


@router.get("/best-version/{resume_id}", response_model=VersionResponse)
def get_best_version(
    resume_id: int,
    metric: str = "ats_score",  # ats_score, interviews_secured, responses_received
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Identify the best performing version based on selected metric"""
    # Verify ownership
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get versions ordered by metric
    query = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id)
    
    if metric == "ats_score":
        query = query.order_by(desc(ResumeVersion.ats_score))
    elif metric == "interviews_secured":
        query = query.order_by(desc(ResumeVersion.interviews_secured))
    elif metric == "responses_received":
        query = query.order_by(desc(ResumeVersion.responses_received))
    else:
        raise HTTPException(status_code=400, detail="Invalid metric")
    
    best_version = query.first()
    
    if not best_version:
        raise HTTPException(status_code=404, detail="No versions found")
    
    return best_version


@router.delete("/versions/{version_id}")
def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume version"""
    version = db.query(ResumeVersion).filter(
        ResumeVersion.id == version_id,
        ResumeVersion.user_id == current_user.id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    db.delete(version)
    db.commit()
    
    return {"message": "Version deleted successfully"}
