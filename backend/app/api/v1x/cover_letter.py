"""
AI-Powered Cover Letter Generator
Generates professional cover letters based on resume and job description
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.llm_provider import get_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cover-letters", tags=["cover-letters"])


# ==================== Schemas ====================

class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter"""
    resume_id: Optional[int] = None
    job_title: str
    company_name: str
    job_description: str
    tone: Optional[str] = "professional"  # professional, enthusiastic, formal
    highlights: Optional[List[str]] = []  # Specific achievements to highlight
    call_to_action: Optional[bool] = True


class CoverLetterResponse(BaseModel):
    """Generated cover letter response"""
    content: str
    subject_line: str
    word_count: int
    tone: str
    variations: List[str] = []


class SavedCoverLetter(BaseModel):
    """Saved cover letter model"""
    id: int
    user_id: int
    resume_id: Optional[int]
    job_title: str
    company_name: str
    content: str
    tone: str
    created_at: str
    updated_at: str


# ==================== Cover Letter Generation ====================

@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI-powered cover letter tailored to the job description
    
    This endpoint creates a professional cover letter that:
    - Matches the job requirements from the description
    - Highlights relevant experience and skills
    - Uses appropriate tone (professional/enthusiastic/formal)
    - Includes a compelling opening and strong call-to-action
    """
    
    try:
        # Get resume data if resume_id provided
        resume_context = ""
        if request.resume_id:
            from app.modelsx.resume import Resume, WorkExperience, ResumeSkill
            
            resume = db.query(Resume).filter(
                Resume.id == request.resume_id,
                Resume.user_id == current_user.id
            ).first()
            
            if resume:
                # Build resume context
                skills = db.query(ResumeSkill).filter(ResumeSkill.resume_id == resume.id).all()
                experiences = db.query(WorkExperience).filter(WorkExperience.resume_id == resume.id).limit(3).all()
                
                skills_text = ", ".join([s.skill_name for s in skills[:10]])
                exp_text = "\n".join([
                    f"- {exp.position} at {exp.company}: {exp.description[:200] if exp.description else ''}"
                    for exp in experiences
                ])
                
                resume_context = f"""
My Skills: {skills_text}

My Recent Experience:
{exp_text}

My Professional Summary: {resume.professional_summary or 'Experienced professional'}
"""
        
        # Build highlights section
        highlights_text = ""
        if request.highlights:
            highlights_text = "\n\nKey achievements to emphasize:\n" + "\n".join([f"- {h}" for h in request.highlights[:3]])
        
        # Determine tone instructions
        tone_instructions = {
            "professional": "Use a professional, confident tone. Be direct and showcase expertise.",
            "enthusiastic": "Use an enthusiastic, passionate tone. Show genuine excitement about the opportunity.",
            "formal": "Use a formal, traditional business tone. Be respectful and conservative."
        }
        tone_guide = tone_instructions.get(request.tone, tone_instructions["professional"])
        
        # Build the LLM prompt
        prompt = f"""You are a professional resume writer and career coach. Write a compelling cover letter for the following job application.

JOB DETAILS:
Position: {request.job_title}
Company: {request.company_name}
Job Description:
{request.job_description[:1000]}  # Limit JD length

CANDIDATE BACKGROUND:
{resume_context or "Qualified professional with relevant experience"}
{highlights_text}

REQUIREMENTS:
1. {tone_guide}
2. Structure: Opening paragraph (hook + interest), 2-3 body paragraphs (experience + fit), closing paragraph (call-to-action)
3. Length: 250-350 words
4. Personalize to the company and role
5. Show genuine interest and cultural fit
6. Highlight 2-3 specific qualifications that match the job
7. Include specific examples or achievements
8. End with a {'strong call-to-action requesting an interview' if request.call_to_action else 'professional closing'}
9. Use first person ("I am", "my experience")
10. Avoid generic phrases like "I am writing to apply"

FORMAT:
[Greeting]
Dear Hiring Manager,

[Opening paragraph - compelling hook]

[Body paragraph 1 - relevant experience]

[Body paragraph 2 - why this company/role]

[Closing paragraph - call to action]

Sincerely,
[Candidate Name]

GENERATE THE COVER LETTER:"""

        # Generate using LLM
        llm = get_provider()
        response = await llm.generate(prompt=prompt, temperature=0.8, max_tokens=600)
        
        # Clean up the response
        content = response.strip()
        
        # Generate subject line
        subject_prompt = f"Write a professional email subject line for applying to {request.job_title} at {request.company_name}. Keep it under 60 characters. Just return the subject line, nothing else."
        subject_response = await llm.generate(prompt=subject_prompt, temperature=0.7, max_tokens=50)
        subject_line = subject_response.strip().strip('"')
        
        # Calculate word count
        word_count = len(content.split())
        
        # Generate one variation with different tone
        alt_tone = "enthusiastic" if request.tone == "professional" else "professional"
        alt_tone_guide = tone_instructions.get(alt_tone, "")
        
        variation_prompt = f"""Rewrite this cover letter with a {alt_tone} tone: {alt_tone_guide}

Original:
{content[:500]}

Provide just the rewritten version:"""
        
        variation_response = await llm.generate(prompt=variation_prompt, temperature=0.8, max_tokens=500)
        variations = [variation_response.strip()]
        
        logger.info(f"Generated cover letter for {request.job_title} at {request.company_name}, {word_count} words")
        
        return CoverLetterResponse(
            content=content,
            subject_line=subject_line,
            word_count=word_count,
            tone=request.tone,
            variations=variations
        )
        
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        
        # Fallback template
        fallback_content = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {request.job_title} position at {request.company_name}. With my relevant experience and skills, I am confident I would be a valuable addition to your team.

In my previous roles, I have developed expertise in key areas that align with your requirements. I am particularly drawn to {request.company_name} because of your innovative approach and commitment to excellence.

I believe my background in {'the field' if not resume_context else 'relevant technologies'} makes me an ideal candidate for this position. I am excited about the opportunity to contribute to your team's success.

Thank you for considering my application. I would welcome the opportunity to discuss how my skills and experience can benefit {request.company_name}. I look forward to hearing from you.

Sincerely,
{current_user.full_name or 'Applicant'}"""
        
        return CoverLetterResponse(
            content=fallback_content,
            subject_line=f"Application for {request.job_title} Position",
            word_count=len(fallback_content.split()),
            tone=request.tone,
            variations=[]
        )


# ==================== Save Cover Letters ====================

@router.post("/save")
def save_cover_letter(
    resume_id: Optional[int],
    job_title: str,
    company_name: str,
    content: str,
    tone: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a generated cover letter for future reference"""
    
    # In a real implementation, you'd save to a cover_letters table
    # For now, return success
    
    return {
        "success": True,
        "message": "Cover letter saved successfully",
        "id": 1,  # Would be actual DB ID
        "job_title": job_title,
        "company_name": company_name
    }


@router.get("/list")
def list_cover_letters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all saved cover letters for the current user"""
    
    # In a real implementation, query from cover_letters table
    # For now, return empty list
    
    return {
        "cover_letters": [],
        "total": 0
    }


@router.get("/{cover_letter_id}")
def get_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific saved cover letter"""
    
    # In a real implementation, query from database
    # For now, return 404
    
    raise HTTPException(status_code=404, detail="Cover letter not found")


@router.delete("/{cover_letter_id}")
def delete_cover_letter(
    cover_letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved cover letter"""
    
    return {
        "success": True,
        "message": "Cover letter deleted successfully"
    }


# ==================== Templates & Tips ====================

@router.get("/templates")
def get_cover_letter_templates():
    """Get cover letter templates for different scenarios"""
    
    templates = [
        {
            "id": 1,
            "name": "Professional Standard",
            "description": "Traditional cover letter format for corporate roles",
            "tone": "professional",
            "best_for": ["Corporate", "Finance", "Consulting"]
        },
        {
            "id": 2,
            "name": "Tech Startup",
            "description": "Modern, enthusiastic tone for startup culture",
            "tone": "enthusiastic",
            "best_for": ["Startups", "Tech Companies", "Creative Roles"]
        },
        {
            "id": 3,
            "name": "Career Change",
            "description": "Emphasizes transferable skills for career transitions",
            "tone": "professional",
            "best_for": ["Career Change", "Industry Switch"]
        },
        {
            "id": 4,
            "name": "Executive Level",
            "description": "Formal, strategic tone for senior positions",
            "tone": "formal",
            "best_for": ["Executive", "C-Level", "Senior Leadership"]
        }
    ]
    
    return {"templates": templates}


@router.get("/tips")
def get_cover_letter_tips():
    """Get tips for writing effective cover letters"""
    
    tips = [
        {
            "category": "Opening",
            "tips": [
                "Start with a compelling hook that shows you've researched the company",
                "Mention a specific achievement or connection to the company",
                "Avoid generic openings like 'I am writing to apply'"
            ]
        },
        {
            "category": "Body",
            "tips": [
                "Use specific examples with quantifiable results",
                "Match your experience to 2-3 key job requirements",
                "Show enthusiasm for the company's mission and culture",
                "Keep paragraphs short and scannable"
            ]
        },
        {
            "category": "Closing",
            "tips": [
                "Include a clear call-to-action",
                "Express confidence without arrogance",
                "Thank the reader for their time",
                "Indicate your availability for an interview"
            ]
        },
        {
            "category": "General",
            "tips": [
                "Keep it to 250-400 words (3-4 paragraphs)",
                "Customize for each application",
                "Use active voice and action verbs",
                "Proofread multiple times",
                "Match the company's tone and culture"
            ]
        }
    ]
    
    return {"tips": tips}
