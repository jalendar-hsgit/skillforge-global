"""
Resume Builder API with AI Integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.quiz_attempt import QuizAttempt
from app.modelsx.resume import (
    Resume, WorkExperience, Education, ResumeProject, 
    ResumeSkill, ResumeCertificate, ResumeAchievement, ATSReport
)
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ResumeOut, ResumeListOut,
    WorkExperienceCreate, WorkExperienceOut,
    EducationCreate, EducationOut,
    ResumeProjectCreate, ResumeProjectOut,
    ResumeSkillCreate, ResumeSkillOut,
    ResumeCertificateCreate, ResumeCertificateOut,
    AchievementCreate, AchievementOut,
    AIBulletPointRequest, AIBulletPointResponse,
    AISummaryRequest, AISummaryResponse,
    AIProjectRequest, AIProjectResponse,
    ATSAnalysisRequest, ATSAnalysisResponse,
    ResumeAnalyticsOut
)

router = APIRouter(prefix="/resumes", tags=["resumes"])


# ==================== CRUD Operations ====================

@router.post("/", response_model=ResumeListOut, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new resume"""
    try:
        resume = Resume(
            user_id=current_user.id,
            **resume_data.dict()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        print(f"Error creating resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create resume: {str(e)}"
        )


@router.get("/", response_model=List[ResumeListOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all user's resumes"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume by ID"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Track view
    resume.views += 1
    db.commit()
    
    return resume


@router.put("/{resume_id}", response_model=ResumeOut)
@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update resume (supports both PUT and PATCH)"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    update_dict = resume_data.dict(exclude_unset=True)
    
    # Handle professional_summary alias
    if 'professional_summary' in update_dict and update_dict['professional_summary'] is not None:
        update_dict['summary'] = update_dict.pop('professional_summary')
    
    for key, value in update_dict.items():
        if hasattr(resume, key):
            setattr(resume, key, value)
    
    resume.version += 1
    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    return None


@router.post("/{resume_id}/duplicate", response_model=ResumeOut)
def duplicate_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate an existing resume"""
    original = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Create new resume
    new_resume = Resume(
        user_id=current_user.id,
        title=f"{original.title} (Copy)",
        template_id=original.template_id,
        full_name=original.full_name,
        email=original.email,
        phone=original.phone,
        location=original.location,
        linkedin_url=original.linkedin_url,
        github_url=original.github_url,
        portfolio_url=original.portfolio_url,
        website_url=original.website_url,
        summary=original.summary
    )
    db.add(new_resume)
    db.flush()
    
    # Copy work experiences
    for exp in original.work_experiences:
        new_exp = WorkExperience(
            resume_id=new_resume.id,
            company=exp.company,
            position=exp.position,
            location=exp.location,
            start_date=exp.start_date,
            end_date=exp.end_date,
            is_current=exp.is_current,
            description=exp.description,
            bullet_points=exp.bullet_points,
            order_index=exp.order_index
        )
        db.add(new_exp)
    
    # Copy education
    for edu in original.education:
        new_edu = Education(
            resume_id=new_resume.id,
            institution=edu.institution,
            degree=edu.degree,
            field_of_study=edu.field_of_study,
            location=edu.location,
            start_date=edu.start_date,
            end_date=edu.end_date,
            gpa=edu.gpa,
            description=edu.description,
            achievements=edu.achievements,
            order_index=edu.order_index
        )
        db.add(new_edu)
    
    # Copy projects, skills, certificates, achievements...
    db.commit()
    db.refresh(new_resume)
    
    return new_resume


@router.post("/{resume_id}/apply-template/{template_id}", response_model=ResumeOut)
def apply_template_to_resume(
    resume_id: int,
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply a template to an existing resume (changes styling, preserves content)"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Validate template exists
    from app.modelsx.resume import ResumeTemplate
    template = db.query(ResumeTemplate).filter(
        ResumeTemplate.id == int(template_id) if template_id.isdigit() else ResumeTemplate.name.ilike(f"%{template_id}%"),
        ResumeTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    # Apply template styling to resume
    resume.template_id = str(template.id)
    
    # Apply template config to resume styling
    if template.config:
        config = template.config
        if isinstance(config, str):
            import json
            config = json.loads(config)
        
        # Apply template layout and styling
        resume.layout = config.get('layout', resume.layout or 'single-column')
        resume.font_family = config.get('font', resume.font_family or 'Inter')
        resume.accent_color = config.get('accent_color', resume.accent_color or '#2563eb')
        resume.picture_style = config.get('picture_style', resume.picture_style or 'circle')
        resume.color_theme = config.get('color_theme', resume.color_theme or 'blue')
        
        # Apply advanced styling if provided
        if 'text_color' in config:
            resume.text_color = config['text_color']
        if 'heading_color' in config:
            resume.heading_color = config['heading_color']
        if 'line_spacing' in config:
            resume.line_spacing = config['line_spacing']
        if 'background_type' in config:
            resume.background_type = config['background_type']
        if 'rating_style' in config:
            resume.rating_style = config['rating_style']
    
    # Track template application in update timestamp
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resume)
    
    return resume


# ==================== Work Experience ====================

@router.post("/{resume_id}/work-experience", response_model=WorkExperienceOut)
def add_work_experience(
    resume_id: int,
    experience: WorkExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add work experience"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    work_exp = WorkExperience(resume_id=resume_id, **experience.dict())
    db.add(work_exp)
    db.commit()
    db.refresh(work_exp)
    
    return work_exp


@router.put("/work-experience/{exp_id}", response_model=WorkExperienceOut)
def update_work_experience(
    exp_id: int,
    experience: WorkExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work experience"""
    work_exp = db.query(WorkExperience).join(Resume).filter(
        WorkExperience.id == exp_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not work_exp:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    for key, value in experience.dict().items():
        setattr(work_exp, key, value)
    
    db.commit()
    db.refresh(work_exp)
    
    return work_exp


@router.delete("/work-experience/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_experience(
    exp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete work experience"""
    work_exp = db.query(WorkExperience).join(Resume).filter(
        WorkExperience.id == exp_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not work_exp:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    db.delete(work_exp)
    db.commit()
    return None


# ==================== Education ====================

@router.post("/{resume_id}/education", response_model=EducationOut)
def add_education(
    resume_id: int,
    education: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add education"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    edu = Education(resume_id=resume_id, **education.dict())
    db.add(edu)
    db.commit()
    db.refresh(edu)
    
    return edu


@router.put("/education/{education_id}", response_model=EducationOut)
def update_education(
    education_id: int,
    education: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update education"""
    edu = db.query(Education).join(Resume).filter(
        Education.id == education_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    
    for key, value in education.dict().items():
        setattr(edu, key, value)
    
    db.commit()
    db.refresh(edu)
    
    return edu


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete education"""
    edu = db.query(Education).join(Resume).filter(
        Education.id == education_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    
    db.delete(edu)
    db.commit()
    return None


# ==================== Projects ====================

@router.post("/{resume_id}/projects", response_model=ResumeProjectOut)
def add_project(
    resume_id: int,
    project: ResumeProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add project"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    proj = ResumeProject(resume_id=resume_id, **project.dict())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    
    return proj


@router.put("/projects/{project_id}", response_model=ResumeProjectOut)
def update_project(
    project_id: int,
    project: ResumeProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project"""
    proj = db.query(ResumeProject).join(Resume).filter(
        ResumeProject.id == project_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict().items():
        setattr(proj, key, value)
    
    db.commit()
    db.refresh(proj)
    
    return proj


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project"""
    proj = db.query(ResumeProject).join(Resume).filter(
        ResumeProject.id == project_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(proj)
    db.commit()
    return None


# ==================== Skills ====================

@router.post("/{resume_id}/skills", response_model=ResumeSkillOut)
def add_skill(
    resume_id: int,
    skill: ResumeSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add skill"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    skill_obj = ResumeSkill(resume_id=resume_id, **skill.dict())
    db.add(skill_obj)
    db.commit()
    db.refresh(skill_obj)
    
    return skill_obj


@router.post("/{resume_id}/skills/bulk", response_model=List[ResumeSkillOut])
def add_skills_bulk(
    resume_id: int,
    skills: List[ResumeSkillCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add multiple skills at once"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    skill_objects = []
    for skill in skills:
        skill_obj = ResumeSkill(resume_id=resume_id, **skill.dict())
        db.add(skill_obj)
        skill_objects.append(skill_obj)
    
    db.commit()
    for obj in skill_objects:
        db.refresh(obj)
    
    return skill_objects


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete skill"""
    skill = db.query(ResumeSkill).join(Resume).filter(
        ResumeSkill.id == skill_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(skill)
    db.commit()
    return None


# ==================== Certificates ====================

@router.post("/{resume_id}/certificates", response_model=ResumeCertificateOut)
def add_certificate(
    resume_id: int,
    certificate: ResumeCertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add certificate"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    cert = ResumeCertificate(resume_id=resume_id, **certificate.dict())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    
    return cert


@router.put("/certificates/{certificate_id}", response_model=ResumeCertificateOut)
def update_certificate(
    certificate_id: int,
    certificate: ResumeCertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update certificate"""
    cert = db.query(ResumeCertificate).join(Resume).filter(
        ResumeCertificate.id == certificate_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    for key, value in certificate.dict(exclude_unset=True).items():
        setattr(cert, key, value)
    
    db.commit()
    db.refresh(cert)
    
    return cert


@router.delete("/certificates/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete certificate"""
    cert = db.query(ResumeCertificate).join(Resume).filter(
        ResumeCertificate.id == certificate_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    db.delete(cert)
    db.commit()
    return None


@router.post("/{resume_id}/certificates/from-quizzes", response_model=List[ResumeCertificateOut])
def import_quiz_certificates(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Automatically import certificates from completed quizzes"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Query quiz_attempts table for passed quizzes
    passed_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.passed == True
    ).order_by(QuizAttempt.created_at.desc()).all()
    
    if not passed_attempts:
        return []
    
    # Get existing certificates to avoid duplicates
    existing_certs = db.query(ResumeCertificate).filter(
        ResumeCertificate.resume_id == resume_id
    ).all()
    
    existing_paths = {cert.name for cert in existing_certs if cert.name}
    
    imported_certificates = []
    
    for attempt in passed_attempts:
        # Skip if certificate for this path already exists
        cert_name = f"SkillForge {attempt.path} Certification"
        if cert_name in existing_paths:
            continue
        
        # Create certificate from quiz attempt
        certificate = ResumeCertificate(
            resume_id=resume_id,
            name=cert_name,
            issuing_organization="SkillForge Global",
            issue_date=attempt.created_at.strftime("%Y-%m-%d") if attempt.created_at else None,
            credential_id=f"SFG-{attempt.path.upper()}-{attempt.id}",
            is_verified=True,
            order_index=len(existing_certs) + len(imported_certificates)
        )
        
        db.add(certificate)
        imported_certificates.append(certificate)
    
    if imported_certificates:
        db.commit()
        for cert in imported_certificates:
            db.refresh(cert)
    
    return imported_certificates


# ==================== Achievements ====================

@router.post("/{resume_id}/achievements", response_model=AchievementOut)
def add_achievement(
    resume_id: int,
    achievement: AchievementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add achievement"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    ach = ResumeAchievement(resume_id=resume_id, **achievement.dict())
    db.add(ach)
    db.commit()
    db.refresh(ach)
    
    return ach


@router.put("/achievements/{achievement_id}", response_model=AchievementOut)
def update_achievement(
    achievement_id: int,
    achievement: AchievementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update achievement"""
    ach = db.query(ResumeAchievement).join(Resume).filter(
        ResumeAchievement.id == achievement_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    for key, value in achievement.dict().items():
        setattr(ach, key, value)
    
    db.commit()
    db.refresh(ach)
    
    return ach


@router.delete("/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(
    achievement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete achievement"""
    ach = db.query(ResumeAchievement).join(Resume).filter(
        ResumeAchievement.id == achievement_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    db.delete(ach)
    db.commit()
    return None
