"""
Skills Validation API Router - Phase 3.4
User skill validation and endorsements
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.learning_paths import SkillValidation
from app.schemas.learning_paths_schemas import (
    SkillValidationResponse, SkillValidationCreate, SkillValidationUpdate,
    UserSkillsResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("", response_model=SkillValidationResponse, status_code=status.HTTP_201_CREATED)
def create_skill_validation(
    skill_data: SkillValidationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create skill validation (admin/mentor)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN", "MENTOR"]:
        raise HTTPException(status_code=403, detail="Only admins/mentors can validate skills")
    
    # Check if skill already exists for user
    existing = db.query(SkillValidation).filter(
        SkillValidation.user_id == skill_data.user_id,
        SkillValidation.skill_name == skill_data.skill_name,
        SkillValidation.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Skill already validated for this user")
    
    validation = SkillValidation(
        **skill_data.dict(),
        validated_by=current_user.id,
        validated_at=datetime.utcnow()
    )
    
    db.add(validation)
    db.commit()
    db.refresh(validation)
    return validation


@router.get("/user/{user_id}", response_model=UserSkillsResponse)
def get_user_skills(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's validated skills (public view)"""
    skills = db.query(SkillValidation).filter(
        SkillValidation.user_id == user_id,
        SkillValidation.is_active == True
    ).order_by(
        desc(SkillValidation.proficiency_level),
        desc(SkillValidation.confidence_score)
    ).all()
    
    return {
        "user_id": user_id,
        "skills": skills,
        "skill_count": len(skills)
    }


@router.get("/me", response_model=UserSkillsResponse)
def get_my_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's skills"""
    skills = db.query(SkillValidation).filter(
        SkillValidation.user_id == current_user.id,
        SkillValidation.is_active == True
    ).order_by(
        desc(SkillValidation.proficiency_level),
        desc(SkillValidation.confidence_score)
    ).all()
    
    return {
        "user_id": current_user.id,
        "skills": skills,
        "skill_count": len(skills)
    }


@router.get("/{skill_id}", response_model=SkillValidationResponse)
def get_skill_validation(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """Get specific skill validation"""
    skill = db.query(SkillValidation).filter(SkillValidation.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill validation not found")
    
    return skill


@router.patch("/{skill_id}", response_model=SkillValidationResponse)
def update_skill_validation(
    skill_id: int,
    update_data: SkillValidationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update skill validation"""
    skill = db.query(SkillValidation).filter(SkillValidation.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill validation not found")
    
    # Only owner or admin can update
    if skill.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this skill")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(skill, key, value)
    
    skill.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_validation(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate skill validation"""
    skill = db.query(SkillValidation).filter(SkillValidation.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill validation not found")
    
    if skill.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    skill.is_active = False
    db.commit()


@router.post("/{skill_id}/endorse")
def endorse_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endorse a user's skill (increase confidence)"""
    skill = db.query(SkillValidation).filter(SkillValidation.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill validation not found")
    
    if current_user.id == skill.user_id:
        raise HTTPException(status_code=400, detail="Cannot endorse your own skill")
    
    # Increase confidence score slightly
    skill.confidence_score = min(100, skill.confidence_score + 5)
    db.commit()
    db.refresh(skill)
    
    return {"endorsed": True, "confidence_score": skill.confidence_score}


@router.get("/search/{skill_name}", response_model=List[SkillValidationResponse])
def search_skills(
    skill_name: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search for skills by name"""
    skills = db.query(SkillValidation).filter(
        SkillValidation.skill_name.ilike(f"%{skill_name}%"),
        SkillValidation.is_active == True
    ).order_by(
        desc(SkillValidation.confidence_score)
    ).offset(skip).limit(limit).all()
    
    return skills


@router.get("/trending", response_model=List[dict])
def get_trending_skills(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending skills"""
    from sqlalchemy import func
    
    trending = db.query(
        SkillValidation.skill_name,
        func.count(SkillValidation.id).label("count"),
        func.avg(SkillValidation.confidence_score).label("avg_confidence")
    ).filter(
        SkillValidation.is_active == True
    ).group_by(
        SkillValidation.skill_name
    ).order_by(
        desc(func.count(SkillValidation.id))
    ).limit(limit).all()
    
    return [
        {
            "skill_name": skill[0],
            "endorsement_count": skill[1],
            "average_confidence": round(skill[2], 2)
        }
        for skill in trending
    ]


@router.get("/user/{user_id}/count")
def get_user_skill_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get number of validated skills for user"""
    count = db.query(SkillValidation).filter(
        SkillValidation.user_id == user_id,
        SkillValidation.is_active == True
    ).count()
    
    return {"user_id": user_id, "skill_count": count}
