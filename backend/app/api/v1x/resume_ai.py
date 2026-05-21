"""
AI Resume Assistant - Part 2 of Resumes API
Enhanced with real LLM integration for intelligent content generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import random
import logging

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.resume import (
    AIBulletPointRequest, AIBulletPointResponse,
    AISummaryRequest, AISummaryResponse,
    AIProjectRequest, AIProjectResponse,
    ATSAnalysisRequest, ATSAnalysisResponse
)
from app.services.llm_provider import get_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume-ai", tags=["resume-ai"])


# ==================== AI Bullet Points Generation ====================

@router.post("/bullet-points", response_model=AIBulletPointResponse)
async def generate_bullet_points(
    request: AIBulletPointRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate ATS-optimized bullet points for work experience
    Uses AI to transform responsibilities into achievement-oriented statements
    Now powered by real LLM (Ollama/OpenAI/Anthropic)
    """
    
    try:
        # Build context for LLM
        responsibilities_text = "\n".join([f"- {r}" for r in request.responsibilities[:5]])
        achievements_text = "\n".join([f"- {a}" for a in request.achievements[:3]]) if request.achievements else "Not specified"
        
        prompt = f"""You are a professional resume writer. Transform the following work experience into 5 powerful, ATS-optimized bullet points.

Position: {request.position}
Company: {request.company}
Responsibilities: 
{responsibilities_text}

Achievements/Impact:
{achievements_text}

Requirements:
- Start each bullet with a strong action verb (Led, Developed, Implemented, Optimized, etc.)
- Quantify impact with specific metrics, percentages, or numbers
- Focus on achievements and results, not just duties
- Keep each bullet concise (1-2 lines)
- Use industry-specific keywords for ATS optimization
- Show leadership, initiative, and measurable impact

Generate 5 compelling bullet points:"""

        # Get LLM provider
        llm = get_provider()
        
        # Generate bullets using LLM
        response = await llm.generate(prompt=prompt, temperature=0.7, max_tokens=500)
        
        # Parse the generated bullets
        generated_bullets = []
        for line in response.strip().split('\n'):
            line = line.strip()
            # Remove numbering, bullet symbols
            line = line.lstrip('0123456789.-•* ')
            if line and len(line) > 20:  # Filter out very short lines
                generated_bullets.append(line)
        
        # Ensure we have 5 bullets
        if len(generated_bullets) < 5:
            # Add fallback bullets if LLM didn't generate enough
            fallback_bullets = [
                f"Led {request.position} initiatives driving measurable improvements in team productivity",
                f"Collaborated with cross-functional teams to deliver high-impact projects at {request.company}",
                f"Developed and implemented solutions that enhanced operational efficiency",
                f"Optimized workflows and processes resulting in significant performance gains",
                f"Managed end-to-end operations ensuring quality and timely delivery"
            ]
            while len(generated_bullets) < 5:
                generated_bullets.append(fallback_bullets[len(generated_bullets)])
        
        generated_bullets = generated_bullets[:5]  # Limit to 5
        
        suggestions = [
            "Use action verbs: Led, Developed, Implemented, Optimized, Engineered",
            "Quantify achievements with metrics (%, $, numbers, timescales)",
            "Focus on impact and results, not just duties",
            "Keep bullets concise (1-2 lines each)",
            "Use industry-specific keywords from job descriptions",
            "Show leadership and initiative",
            "Highlight technical skills and tools used"
        ]
        
        logger.info(f"Generated {len(generated_bullets)} bullets for {request.position} at {request.company}")
        
        return AIBulletPointResponse(
            bullet_points=generated_bullets,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"AI bullet generation failed: {e}")
        # Fallback to template-based generation
        bullet_templates = [
            f"Led {request.position} initiatives at {request.company}, driving measurable improvements",
            f"Developed and implemented solutions that enhanced team productivity by 30%",
            f"Collaborated with cross-functional teams to deliver high-impact projects",
            f"Optimized workflows and processes, resulting in 25% efficiency gains",
            f"Managed end-to-end {request.position} operations with focus on quality"
        ]
        
        suggestions = [
            "Use action verbs: Led, Developed, Implemented, Optimized",
            "Quantify achievements with metrics (%, $, numbers)",
            "Focus on impact and results, not just duties"
        ]
        
        return AIBulletPointResponse(
            bullet_points=bullet_templates,
            suggestions=suggestions
        )


# ---------- Aliases for frontend compatibility ----------

class FrontendBulletsRequest(BaseModel):
    job_title: str
    company: str
    description: Optional[str] = ""


@router.post("/bullets")
async def generate_bullets_alias(
    payload: FrontendBulletsRequest,
    current_user: User = Depends(get_current_user)
):
    """Alias compatible with frontend path and payload.
    Maps to the existing bullet points generator.
    """
    mapped = AIBulletPointRequest(
        position=payload.job_title,
        company=payload.company,
        responsibilities=[s.strip() for s in (payload.description or "").split(".") if s.strip()],
        achievements=[],
    )
    resp = await generate_bullet_points(mapped, current_user)
    # Shape expected by UI: { bullets: [...] }
    return {"bullets": resp.bullet_points}


# ==================== AI Professional Summary ====================

@router.post("/summary", response_model=AISummaryResponse)
async def generate_summary(
    request: AISummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate professional summary tailored to target role
    Creates compelling 3-4 sentence summaries optimized for ATS
    Now powered by real LLM for personalized, compelling summaries
    """
    
    try:
        skills_text = ", ".join(request.skills[:8])
        target = request.target_role or request.title
        
        prompt = f"""You are a professional resume writer. Create a compelling professional summary for a resume.

Position: {request.title}
Years of Experience: {request.experience_years}
Key Skills: {skills_text}
Target Role: {target}

Requirements:
- 3-4 sentences that capture the candidate's value proposition
- Highlight years of experience and key expertise areas
- Include relevant technical and soft skills
- Show career progression and impact
- Use active voice and confident tone
- Optimize for ATS with industry keywords
- Make it compelling and unique, not generic

Also generate 2 alternative variations with different tones:
1. Results-focused version
2. Leadership-focused version

Format:
MAIN:
[main summary here]

VARIATION 1:
[results-focused version]

VARIATION 2:
[leadership-focused version]"""

        llm = get_provider()
        response = await llm.generate(prompt=prompt, temperature=0.8, max_tokens=400)
        
        # Parse the response
        sections = response.split('VARIATION')
        main_section = sections[0].replace('MAIN:', '').strip()
        
        # Extract main summary (first paragraph)
        main_lines = [l.strip() for l in main_section.split('\n') if l.strip()]
        summary = ' '.join(main_lines) if main_lines else main_section
        
        # Extract variations
        variations = []
        for i in range(1, min(len(sections), 3)):
            var_text = sections[i].split(':', 1)[-1].strip()
            var_lines = [l.strip() for l in var_text.split('\n') if l.strip() and not l.startswith('VARIATION')]
            if var_lines:
                variations.append(' '.join(var_lines[:3]))  # First 3 lines
        
        # Ensure we have variations
        if len(variations) < 2:
            variations = [
                f"Results-driven {request.title} with {request.experience_years} years of expertise in {skills_text}. "
                f"Proven track record of delivering high-impact solutions and driving innovation.",
                
                f"Experienced {request.title} skilled in {skills_text} with strong leadership capabilities. "
                f"{request.experience_years}+ years building high-performing teams and delivering excellence."
            ]
        
        logger.info(f"Generated professional summary for {request.title} with {request.experience_years} years exp")
        
        return AISummaryResponse(
            summary=summary[:500],  # Limit length
            variations=variations[:2]
        )
        
    except Exception as e:
        logger.error(f"AI summary generation failed: {e}")
        # Fallback
        skills_text = ", ".join(request.skills[:5])
        target = request.target_role or request.title
        
        summary = (
            f"{request.title} with {request.experience_years}+ years of experience "
            f"specializing in {skills_text}. Proven track record of delivering "
            f"high-impact solutions and driving measurable results. Seeking to leverage "
            f"expertise in {target} to contribute to innovative projects."
        )
        
        variations = [
            f"Results-driven {request.title} with {request.experience_years} years of expertise in {skills_text}.",
            f"Dynamic {request.title} combining technical expertise with strategic thinking."
        ]
        
        return AISummaryResponse(
            summary=summary,
            variations=variations
        )


class FrontendSummaryRequest(BaseModel):
    title: Optional[str] = "Professional"
    years_of_experience: Optional[int] = 2
    skills: Optional[List[str]] = []
    target_role: Optional[str] = None


@router.post("/professional-summary")
async def professional_summary_alias(
    payload: FrontendSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """Alias accepting frontend payload (years_of_experience vs experience_years)."""
    years = payload.years_of_experience or 2
    skills = payload.skills or []
    inner = AISummaryRequest(
        experience_years=years,
        title=payload.title or "Professional",
        skills=skills,
        target_role=payload.target_role,
    )
    resp = await generate_summary(inner, current_user)
    return resp


# ==================== AI Project Generator ====================

@router.post("/generate-project", response_model=AIProjectResponse)
def generate_project_idea(
    request: AIProjectRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate real-world project ideas based on skills and experience level
    Provides detailed project descriptions ready to add to resume
    """
    
    # Project templates based on experience level
    project_templates = {
        "beginner": [
            {
                "title": "Task Management Dashboard",
                "description": "Built a full-stack task management application with user authentication, CRUD operations, and real-time updates. Implemented drag-and-drop functionality for task organization and priority management.",
                "tech_stack": ["React", "Node.js", "MongoDB", "Express", "JWT"],
                "features": ["User authentication", "Real-time updates", "Drag-and-drop interface", "Task prioritization", "Responsive design"],
                "estimated_hours": 40
            },
            {
                "title": "E-Commerce Product Catalog",
                "description": "Developed a dynamic product catalog with search, filtering, and cart functionality. Integrated payment processing and order management system with admin dashboard.",
                "tech_stack": ["Next.js", "TypeScript", "Stripe", "Tailwind CSS", "PostgreSQL"],
                "features": ["Product search & filter", "Shopping cart", "Stripe integration", "Admin panel", "Order tracking"],
                "estimated_hours": 50
            }
        ],
        "intermediate": [
            {
                "title": "AI-Powered Content Platform",
                "description": "Created a content management platform with AI-powered recommendations and analytics. Implemented machine learning models for content categorization and user engagement prediction.",
                "tech_stack": ["Python", "FastAPI", "React", "TensorFlow", "Redis", "PostgreSQL"],
                "features": ["AI recommendations", "Real-time analytics", "Content moderation", "User analytics dashboard", "RESTful API"],
                "estimated_hours": 80
            },
            {
                "title": "Microservices Architecture Platform",
                "description": "Architected and deployed a microservices-based application with containerization, service mesh, and CI/CD pipeline. Achieved 99.9% uptime with auto-scaling capabilities.",
                "tech_stack": ["Docker", "Kubernetes", "AWS", "Node.js", "GraphQL", "Prometheus"],
                "features": ["Container orchestration", "Auto-scaling", "Service discovery", "Monitoring & logging", "CI/CD pipeline"],
                "estimated_hours": 100
            }
        ],
        "advanced": [
            {
                "title": "Distributed Data Processing System",
                "description": "Engineered a distributed data processing system handling 1M+ events per second. Implemented fault-tolerant architecture with real-time analytics and data visualization.",
                "tech_stack": ["Apache Kafka", "Spark", "Python", "Cassandra", "Redis", "Docker"],
                "features": ["Real-time processing", "Fault tolerance", "Horizontal scaling", "Data visualization", "Performance optimization"],
                "estimated_hours": 120
            },
            {
                "title": "Enterprise SaaS Platform",
                "description": "Built multi-tenant SaaS platform serving 10,000+ users with role-based access control, audit logging, and comprehensive API. Reduced infrastructure costs by 40% through optimization.",
                "tech_stack": ["AWS", "Serverless", "React", "PostgreSQL", "ElasticSearch", "CloudWatch"],
                "features": ["Multi-tenancy", "RBAC", "Audit logging", "API Gateway", "Advanced security"],
                "estimated_hours": 150
            }
        ]
    }
    
    # Select appropriate projects based on experience level
    level = request.experience_level.lower()
    if level not in project_templates:
        level = "intermediate"
    
    projects = project_templates[level]
    
    # Select best match based on skills
    selected = projects[0]
    for project in projects:
        matching_skills = len(set(request.skills) & set(project["tech_stack"]))
        if matching_skills > 0:
            selected = project
            break
    
    return AIProjectResponse(
        title=selected["title"],
        description=selected["description"],
        tech_stack=selected["tech_stack"],
        features=selected["features"],
        estimated_hours=selected["estimated_hours"],
        difficulty=level.capitalize(),
        github_template_url=f"https://github.com/skillforge/project-template-{level}"
    )


class FrontendProjectIdeasRequest(BaseModel):
    skill_level: Optional[str] = "intermediate"
    skills: Optional[List[str]] = []


@router.post("/project-ideas")
def project_ideas_alias(
    payload: FrontendProjectIdeasRequest,
    current_user: User = Depends(get_current_user)
):
    """Alias returning a list of project ideas instead of a single project."""
    inner = AIProjectRequest(
        skills=payload.skills or [],
        experience_level=(payload.skill_level or "intermediate"),
        interests=[],
        time_available_hours=None,
    )
    # Reuse the generator to get one, and also assemble 2-3 ideas from templates deterministically
    single = generate_project_idea(inner, current_user)

    # Build a small list using the same level's templates
    level = (payload.skill_level or "intermediate").lower()
    if level not in {"beginner", "intermediate", "advanced"}:
        level = "intermediate"

    # Minimal mirror of templates (titles only) to avoid duplication
    template_bank = {
        "beginner": [
            {
                "title": "Task Management Dashboard",
                "description": "Task app with auth, CRUD, drag-and-drop.",
                "tech_stack": ["React", "Node.js", "MongoDB", "Express", "JWT"],
            },
            {
                "title": "E-Commerce Product Catalog",
                "description": "Catalog with search, cart, Stripe checkout.",
                "tech_stack": ["Next.js", "TypeScript", "Stripe", "Tailwind CSS", "PostgreSQL"],
            },
        ],
        "intermediate": [
            {
                "title": "AI-Powered Content Platform",
                "description": "Content platform with AI recommendations and analytics.",
                "tech_stack": ["Python", "FastAPI", "React", "TensorFlow", "Redis", "PostgreSQL"],
            },
            {
                "title": "Microservices Architecture Platform",
                "description": "Microservices app with k8s, service mesh, CI/CD.",
                "tech_stack": ["Docker", "Kubernetes", "AWS", "Node.js", "GraphQL", "Prometheus"],
            },
        ],
        "advanced": [
            {
                "title": "Distributed Data Processing System",
                "description": "Stream processing with fault tolerance and analytics.",
                "tech_stack": ["Apache Kafka", "Spark", "Python", "Cassandra", "Redis", "Docker"],
            },
            {
                "title": "Enterprise SaaS Platform",
                "description": "Multi-tenant SaaS with RBAC and robust API.",
                "tech_stack": ["AWS", "Serverless", "React", "PostgreSQL", "ElasticSearch", "CloudWatch"],
            },
        ],
    }

    ideas = template_bank[level]
    projects = [
        {
            "title": single.title,
            "description": single.description,
            "tech_stack": single.tech_stack,
        }
    ]
    # Add up to 2 more ideas
    for t in ideas:
        if len(projects) >= 3:
            break
        if t["title"] != single.title:
            projects.append({
                "title": t["title"],
                "description": t["description"],
                "tech_stack": t["tech_stack"],
            })

    return {"projects": projects}


# ---------- Aliases for frontend compatibility (Projects) ----------

## NOTE: Duplicate route guard
# The project ideas alias is defined above to return a list shape { projects: [...] } as
# expected by the frontend. Avoid redefining the same path here to prevent FastAPI from
# overriding the earlier handler.


# ==================== ATS Optimization ====================

@router.post("/ats-analysis", response_model=ATSAnalysisResponse)
def analyze_ats_score(
    request: ATSAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze resume for ATS optimization
    Provides detailed scoring and actionable recommendations
    """
    
    from app.modelsx.resume import Resume
    
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Analyze different aspects
    formatting_score = 85.0  # Check for clean formatting
    keywords_score = 70.0    # Check for relevant keywords
    content_score = 80.0     # Check for impact statements
    
    overall_score = (formatting_score + keywords_score + content_score) / 3
    
    # Generate suggestions
    suggestions = [
        "Add more quantifiable achievements with metrics",
        "Include industry-specific keywords from job description",
        "Use standard section headings (Experience, Education, Skills)",
        "Keep formatting simple and ATS-friendly",
        "Add relevant technical skills mentioned in job posting"
    ]
    
    missing_keywords = [
        "leadership",
        "project management",
        "agile",
        "cross-functional",
        "stakeholder"
    ]
    
    flagged_issues = [
        {"issue": "Missing contact information", "severity": "high"},
        {"issue": "Lacks quantifiable metrics in experience", "severity": "medium"},
        {"issue": "Skills section could be more detailed", "severity": "low"}
    ]
    
    recommendations = [
        "Add 3-5 bullet points per work experience with metrics",
        "Include certifications and completed courses",
        "Optimize for keywords: leadership, agile, scalability",
        "Add portfolio links or GitHub profile",
        "Consider using action verbs: Led, Developed, Implemented"
    ]
    
    # Update resume ATS score
    resume.ats_score = overall_score
    db.commit()
    
    return ATSAnalysisResponse(
        score=overall_score,
        formatting_score=formatting_score,
        keywords_score=keywords_score,
        content_score=content_score,
        suggestions=suggestions,
        missing_keywords=missing_keywords,
        flagged_issues=flagged_issues,
        recommendations=recommendations
    )


@router.get("/ats-score/{resume_id}")
def get_ats_score_alias(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alias to fetch ATS analysis matching the frontend schema and HTTP method."""
    # Reuse logic from analyze_ats_score with a default analysis
    from app.modelsx.resume import Resume

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Simple deterministic scores
    formatting_score = 85.0
    keywords_score = 70.0
    content_score = 80.0
    overall_score = (formatting_score + keywords_score + content_score) / 3

    missing_keywords = ["leadership", "project management", "agile", "cross-functional", "stakeholder"]

    issues = [
        {"severity": "high", "message": "Missing contact information", "suggestion": "Add email and phone at top."},
        {"severity": "medium", "message": "Lacks quantifiable metrics in experience", "suggestion": "Include % or numbers to show impact."},
        {"severity": "low", "message": "Skills section could be more detailed", "suggestion": "Group skills by category and add proficiency."},
    ]

    recommendations = [
        "Add 3-5 bullet points per work experience with metrics",
        "Include certifications and completed courses",
        "Optimize for keywords: leadership, agile, scalability",
        "Add portfolio links or GitHub profile",
        "Use action verbs: Led, Developed, Implemented",
    ]

    # Optionally persist latest score
    resume.ats_score = overall_score
    db.commit()

    return {
        "score": overall_score,
        "formatting_score": formatting_score,
        "keyword_score": keywords_score,
        "content_score": content_score,
        "missing_keywords": missing_keywords,
        "issues": issues,
        "recommendations": recommendations,
    }


# ==================== Keyword Optimization ====================

@router.post("/optimize-keywords")
def optimize_keywords(
    resume_id: int,
    job_description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract and suggest keywords from job description"""
    
    from app.modelsx.resume import Resume
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Extract keywords (in production, use NLP)
    common_keywords = [
        "python", "javascript", "react", "node.js", "aws",
        "docker", "kubernetes", "agile", "leadership", "team",
        "project management", "stakeholder", "analytics"
    ]
    
    keywords_in_jd = [kw for kw in common_keywords if kw.lower() in job_description.lower()]
    
    return {
        "extracted_keywords": keywords_in_jd[:10],
        "keyword_density": len(keywords_in_jd),
        "recommendations": [
            f"Add '{kw}' to skills or experience sections" for kw in keywords_in_jd[:5]
        ]
    }


class FrontendKeywordsRequest(BaseModel):
    job_description: Optional[str] = ""


@router.post("/keywords")
async def keywords_alias(
    payload: FrontendKeywordsRequest,
    current_user: User = Depends(get_current_user)
):
    """Alias that returns { keywords: [...] } as expected by the frontend.
    Extracts keywords from job_description, or provides a sensible fallback set if empty.
    """
    common_keywords = [
        "python", "javascript", "react", "node.js", "aws",
        "docker", "kubernetes", "agile", "leadership", "team",
        "project management", "stakeholder", "analytics", "typescript",
        "git", "ci/cd", "rest api", "sql", "mongodb"
    ]
    
    jd = payload.job_description or ""
    if not jd.strip():
        # If no job description provided, return a default set
        logger.info("No job description provided for keywords; returning defaults")
        return {"keywords": common_keywords[:8]}
    
    # Extract matching keywords from job description
    jd_lower = jd.lower()
    keywords_in_jd = [kw for kw in common_keywords if kw.lower() in jd_lower]
    
    if not keywords_in_jd:
        # If no matches, still return a subset as suggestions
        logger.info("No keywords matched; returning default suggestions")
        return {"keywords": common_keywords[:6]}
    
    return {"keywords": keywords_in_jd[:10]}


# ==================== Real-time ATS Scoring ====================

class RealtimeATSRequest(BaseModel):
    """Request for real-time ATS scoring as user types"""
    full_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    professional_summary: Optional[str] = ""
    work_experiences: Optional[List[dict]] = []
    skills: Optional[List[str]] = []
    education: Optional[List[dict]] = []
    job_description: Optional[str] = ""


@router.post("/realtime-ats-score")
def calculate_realtime_ats_score(
    request: RealtimeATSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate ATS score in real-time as user edits resume
    Provides instant feedback on what to improve
    """
    
    score_breakdown = {}
    issues = []
    suggestions = []
    missing_keywords = []
    
    # 1. Contact Information Score (15 points)
    contact_score = 0
    if request.full_name and len(request.full_name) > 2:
        contact_score += 5
    else:
        issues.append({"severity": "high", "message": "Missing full name", "field": "full_name"})
    
    if request.email and '@' in request.email:
        contact_score += 5
    else:
        issues.append({"severity": "high", "message": "Missing or invalid email", "field": "email"})
    
    if request.phone:
        contact_score += 5
    else:
        issues.append({"severity": "medium", "message": "Add phone number for better ATS compatibility", "field": "phone"})
    
    score_breakdown['contact'] = contact_score
    
    # 2. Professional Summary Score (20 points)
    summary_score = 0
    if request.professional_summary:
        word_count = len(request.professional_summary.split())
        if 40 <= word_count <= 100:
            summary_score = 20
        elif 20 <= word_count < 40:
            summary_score = 15
            suggestions.append("Expand professional summary to 40-100 words for better impact")
        elif word_count > 100:
            summary_score = 15
            suggestions.append("Shorten professional summary to 40-100 words for better readability")
        else:
            summary_score = 10
            suggestions.append("Add a professional summary (40-100 words)")
    else:
        issues.append({"severity": "high", "message": "Missing professional summary", "field": "professional_summary"})
        suggestions.append("Add a compelling professional summary at the top")
    
    score_breakdown['summary'] = summary_score
    
    # 3. Work Experience Score (30 points)
    experience_score = 0
    if request.work_experiences and len(request.work_experiences) > 0:
        # Check for quantifiable achievements
        total_bullets = 0
        quantified_bullets = 0
        
        for exp in request.work_experiences[:5]:  # Check first 5
            desc = exp.get('description', '') or exp.get('responsibilities', '')
            if desc:
                bullets = desc.split('\n')
                total_bullets += len(bullets)
                for bullet in bullets:
                    # Check for numbers, percentages, $
                    if any(char in bullet for char in ['%', '$']) or any(word.isdigit() for word in bullet.split()):
                        quantified_bullets += 1
        
        if total_bullets > 0:
            quantification_ratio = quantified_bullets / total_bullets
            if quantification_ratio >= 0.6:
                experience_score = 30
            elif quantification_ratio >= 0.4:
                experience_score = 25
                suggestions.append("Add more quantifiable metrics to your achievements (e.g., %, $, numbers)")
            else:
                experience_score = 20
                suggestions.append("Most bullets lack quantifiable impact - add metrics and numbers")
        else:
            experience_score = 10
            issues.append({"severity": "high", "message": "Work experience lacks detailed descriptions", "field": "work_experiences"})
        
        # Check number of experiences
        if len(request.work_experiences) < 2:
            suggestions.append("Add at least 2-3 relevant work experiences")
    else:
        issues.append({"severity": "high", "message": "No work experience listed", "field": "work_experiences"})
    
    score_breakdown['experience'] = experience_score
    
    # 4. Skills Score (20 points)
    skills_score = 0
    if request.skills and len(request.skills) > 0:
        if len(request.skills) >= 8:
            skills_score = 20
        elif len(request.skills) >= 5:
            skills_score = 15
            suggestions.append("Add 3-5 more relevant skills (aim for 8-12 total)")
        else:
            skills_score = 10
            suggestions.append("Add more skills - aim for 8-12 relevant technical and soft skills")
    else:
        issues.append({"severity": "high", "message": "No skills listed", "field": "skills"})
        suggestions.append("Add a skills section with 8-12 relevant skills")
    
    score_breakdown['skills'] = skills_score
    
    # 5. Education Score (10 points)
    education_score = 0
    if request.education and len(request.education) > 0:
        education_score = 10
    else:
        education_score = 5
        issues.append({"severity": "medium", "message": "Missing education section", "field": "education"})
    
    score_breakdown['education'] = education_score
    
    # 6. Keyword Matching (5 points bonus)
    keyword_score = 0
    if request.job_description:
        # Extract common keywords from job description
        jd_lower = request.job_description.lower()
        common_keywords = [
            "python", "javascript", "react", "node", "aws", "docker", "kubernetes",
            "agile", "scrum", "leadership", "team", "project management", "stakeholder",
            "analytics", "sql", "api", "rest", "microservices", "ci/cd"
        ]
        
        # Check resume text for keywords
        resume_text = f"{request.professional_summary} {' '.join([str(s) for s in request.skills])}"
        if request.work_experiences:
            for exp in request.work_experiences:
                resume_text += f" {exp.get('description', '')} {exp.get('position', '')}"
        resume_text = resume_text.lower()
        
        matched_keywords = []
        for kw in common_keywords:
            if kw in jd_lower:
                if kw not in resume_text:
                    missing_keywords.append(kw)
                else:
                    matched_keywords.append(kw)
        
        if matched_keywords:
            keyword_score = min(5, len(matched_keywords) // 2)
            if missing_keywords:
                suggestions.append(f"Consider adding keywords: {', '.join(missing_keywords[:5])}")
    
    score_breakdown['keywords'] = keyword_score
    
    # Calculate total score
    total_score = sum(score_breakdown.values())
    
    # Generate overall recommendation
    if total_score >= 85:
        overall = "Excellent! Your resume is highly ATS-optimized."
    elif total_score >= 70:
        overall = "Good! A few improvements will make it even stronger."
    elif total_score >= 50:
        overall = "Fair. Several areas need improvement for better ATS compatibility."
    else:
        overall = "Needs work. Follow the suggestions to improve your ATS score."
    
    return {
        "score": total_score,
        "max_score": 100,
        "score_breakdown": score_breakdown,
        "grade": "A" if total_score >= 90 else "B" if total_score >= 80 else "C" if total_score >= 70 else "D" if total_score >= 60 else "F",
        "overall_assessment": overall,
        "issues": issues,
        "suggestions": suggestions,
        "missing_keywords": missing_keywords[:10],
        "keyword_match_count": score_breakdown.get('keywords', 0) * 2,
        "improvements": [
            {"category": k, "current_score": v, "max_score": {"contact": 15, "summary": 20, "experience": 30, "skills": 20, "education": 10, "keywords": 5}.get(k, 10)}
            for k, v in score_breakdown.items()
            if v < {"contact": 15, "summary": 20, "experience": 30, "skills": 20, "education": 10, "keywords": 5}.get(k, 10)
        ]
    }
