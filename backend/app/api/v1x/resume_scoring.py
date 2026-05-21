"""
Resume ATS Scoring API
Endpoints for calculating resume ATS scores and getting improvement suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import json

from app.core.db import SessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.services.ats_scorer import ats_scorer

router = APIRouter(prefix="/resume-scoring", tags=["Resume Scoring"])

class ResumeTextIn(BaseModel):
    """Input: resume content as text"""
    content: str

class ATSScoreOut(BaseModel):
    """ATS score response"""
    overall_score: int
    breakdown: list
    suggestions: list
    ats_friendly: bool

@router.post("/score")
def score_resume(
    data: ResumeTextIn,
    user: User = Depends(get_current_user)
) -> dict:
    """
    Calculate ATS score for a resume.
    
    Takes resume content as plain text and returns:
    - Overall score (0-100)
    - Breakdown by criteria
    - Actionable suggestions
    """
    if not data.content or len(data.content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Resume content must be at least 50 characters"
        )
    
    # Calculate ATS score
    result = ats_scorer.calculate_score(data.content)
    
    # Store scoring event (for analytics)
    db = SessionLocal()
    try:
        db.execute("""
            INSERT INTO resume_analytics_events (
                user_id, event_type, resume_content, score_value, created_at
            ) VALUES (:user_id, 'ats_score', :content, :score, NOW())
        """, {
            "user_id": user.id,
            "content": data.content[:1000],  # Store first 1000 chars for reference
            "score": result["overall_score"]
        })
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()
    
    return result

@router.post("/score-by-resume/{resume_id}")
def score_resume_by_id(
    resume_id: int,
    user: User = Depends(get_current_user)
) -> dict:
    """
    Calculate ATS score for an existing resume from resume_builder table.
    """
    db = SessionLocal()
    try:
        # Get resume content
        resume = db.execute("""
            SELECT id, user_id, full_name, professional_summary,
                   work_experiences, education, skills, certifications
            FROM resumes
            WHERE id = :rid AND user_id = :uid
        """, {"rid": resume_id, "uid": user.id}).fetchone()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Reconstruct resume text from components
        text_parts = [
            resume.full_name or "Resume",
            resume.professional_summary or "",
        ]
        
        # Add work experience
        if resume.work_experiences:
            try:
                exp = json.loads(resume.work_experiences) if isinstance(resume.work_experiences, str) else resume.work_experiences
                for item in exp:
                    text_parts.append(f"{item.get('job_title', '')} at {item.get('company', '')}")
                    text_parts.append(item.get('description', ''))
            except:
                pass
        
        # Add education
        if resume.education:
            try:
                edu = json.loads(resume.education) if isinstance(resume.education, str) else resume.education
                for item in edu:
                    text_parts.append(f"{item.get('degree', '')} from {item.get('school', '')}")
            except:
                pass
        
        # Add skills
        if resume.skills:
            text_parts.append(str(resume.skills))
        
        # Add certifications
        if resume.certifications:
            text_parts.append(str(resume.certifications))
        
        resume_text = "\n".join(filter(None, text_parts))
        
        if not resume_text or len(resume_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume content is too short to score"
            )
        
        # Calculate score
        result = ats_scorer.calculate_score(resume_text)
        
        # Store scoring event
        try:
            db.execute("""
                INSERT INTO resume_analytics_events (
                    user_id, event_type, resume_id, score_value, created_at
                ) VALUES (:user_id, 'ats_score', :resume_id, :score, NOW())
            """, {
                "user_id": user.id,
                "resume_id": resume_id,
                "score": result["overall_score"]
            })
            db.commit()
        except:
            db.rollback()
        
        return result
    finally:
        db.close()

@router.get("/score-history")
def get_score_history(user: User = Depends(get_current_user)):
    """
    Get user's resume scoring history.
    Shows all ATS scores calculated for the user.
    """
    db = SessionLocal()
    try:
        events = db.execute("""
            SELECT id, event_type, resume_id, score_value, created_at
            FROM resume_analytics_events
            WHERE user_id = :uid AND event_type = 'ats_score'
            ORDER BY created_at DESC
            LIMIT 20
        """, {"uid": user.id}).fetchall()
        
        history = [
            {
                "id": e.id,
                "resume_id": e.resume_id,
                "score": e.score_value,
                "created_at": str(e.created_at)
            }
            for e in events
        ]
        
        return {"history": history}
    finally:
        db.close()

@router.get("/improvements/{resume_id}")
def get_improvement_tips(
    resume_id: int,
    user: User = Depends(get_current_user)
) -> dict:
    """
    Get detailed improvement suggestions for a specific resume.
    """
    db = SessionLocal()
    try:
        # Get resume
        resume = db.execute("""
            SELECT id, user_id, full_name, professional_summary
            FROM resumes
            WHERE id = :rid AND user_id = :uid
        """, {"rid": resume_id, "uid": user.id}).fetchone()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Reconstruct and score (simplified)
        text = f"{resume.full_name}\n{resume.professional_summary}"
        result = ats_scorer.calculate_score(text)
        
        return {
            "resume_id": resume_id,
            "score": result["overall_score"],
            "suggestions": result["suggestions"],
            "detailed_breakdown": result["breakdown"]
        }
    finally:
        db.close()

@router.post("/compare")
def compare_resumes(
    resumes: list[dict],
    user: User = Depends(get_current_user)
) -> dict:
    """
    Compare ATS scores across multiple resumes.
    Useful for A/B testing resume content.
    
    Input: [{"content": "resume text 1"}, {"content": "resume text 2"}]
    """
    if not resumes or len(resumes) > 5:
        raise HTTPException(
            status_code=400,
            detail="Provide 1-5 resumes to compare"
        )
    
    results = []
    for idx, resume in enumerate(resumes):
        content = resume.get("content", "")
        if content:
            score_result = ats_scorer.calculate_score(content)
            results.append({
                "index": idx,
                "score": score_result["overall_score"],
                "ats_friendly": score_result["ats_friendly"]
            })
    
    if not results:
        raise HTTPException(
            status_code=400,
            detail="At least one resume content required"
        )
    
    # Rank by score
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    best_idx = ranked[0]["index"]
    
    return {
        "results": ranked,
        "best_version": best_idx,
        "recommendation": f"Version {best_idx + 1} has the best ATS score"
    }
