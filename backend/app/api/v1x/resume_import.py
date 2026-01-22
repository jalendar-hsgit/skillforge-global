"""
Resume Import API - Upload and parse PDF/DOCX resumes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Tuple
import os
import tempfile
import json

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.resume import Resume
from app.schemas.resume import ResumeOut

router = APIRouter(prefix="/resume-import", tags=["resume-import"])


def parse_pdf_resume(file_path: str) -> dict:
    """
    Extract text and structure from PDF resume.
    For MVP: simple text extraction using PyPDF2 or pdfplumber.
    Future: Use AI/NLP to extract structured data.
    """
    try:
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        
        # Basic parsing - split by common sections
        parsed_data = {
            "raw_text": text,
            "full_name": extract_name_from_text(text),
            "email": extract_email_from_text(text),
            "phone": extract_phone_from_text(text),
            "professional_summary": extract_summary_from_text(text),
        }
        
        return parsed_data
        
    except ImportError:
        # Fallback if PyPDF2 not available
        return {
            "raw_text": "PDF parsing library not installed. Please install PyPDF2.",
            "note": "Install with: pip install PyPDF2"
        }
    except Exception as e:
        return {
            "error": f"Failed to parse PDF: {str(e)}",
            "raw_text": ""
        }


def parse_docx_resume(file_path: str) -> dict:
    """
    Extract text and structure from DOCX resume.
    For MVP: simple text extraction using python-docx.
    """
    try:
        from docx import Document
        
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        parsed_data = {
            "raw_text": text,
            "full_name": extract_name_from_text(text),
            "email": extract_email_from_text(text),
            "phone": extract_phone_from_text(text),
            "professional_summary": extract_summary_from_text(text),
        }
        
        return parsed_data
        
    except ImportError:
        return {
            "raw_text": "DOCX parsing library not installed. Please install python-docx.",
            "note": "Install with: pip install python-docx"
        }
    except Exception as e:
        return {
            "error": f"Failed to parse DOCX: {str(e)}",
            "raw_text": ""
        }


def extract_name_from_text(text: str) -> Optional[str]:
    """Extract name from resume text (first non-empty line usually)"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines[0] if lines else None


def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email using stricter regex and basic sanity checks"""
    import re
    # Disallow leading/trailing dots, enforce TLD length 2-63, and at least one dot in domain
    email_pattern = r"\b(?!\.)[A-Za-z0-9._%+-]+(?<!\.)@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,63}\b"
    match = re.search(email_pattern, text)
    if match:
        email = match.group(0)
        # Basic sanity: length and no consecutive dots
        if 5 <= len(email) <= 254 and ".." not in email:
            return email
    return None


def extract_phone_from_text(text: str) -> Optional[str]:
    """Extract phone number using regex; prefer 8-15 digits (allows formats like +1-555-1234), allow separators."""
    import re
    # Normalize to simplify validation
    digits = re.sub(r"\D", "", text)
    # Quick scan for an 8-15 digit sequence (allows +1-555-1234 = 8 digits, rejects too-short 7-digit numbers)
    seq = re.search(r"\d{8,15}", digits)
    if not seq:
        return None
    # Now try to match a formatted number in the original text
    # More flexible pattern: optional country code + groups of 2-4 digits with separators
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)*\d{2,4}[-.\s]?\d{2,4}\b"
    match = re.search(phone_pattern, text)
    if match:
        # Validate matched string has 8-15 digits total
        matched_digits = re.sub(r"\D", "", match.group(0))
        if 8 <= len(matched_digits) <= 15:
            return match.group(0).strip()
    # Fallback to digit sequence
    return seq.group(0)


def extract_summary_from_text(text: str) -> Optional[str]:
    """
    Extract professional summary (look for Summary/About/Profile sections).
    This is a simple heuristic - future versions can use AI.
    """
    import re
    
    # Look for summary section (match heading on its own line, then capture content until next section or 2+ blank lines)
    summary_patterns = [
        r'(?:^|\n)\s*(?:PROFESSIONAL SUMMARY|SUMMARY|PROFILE|ABOUT)\s*\n+(.*?)(?=\n\s*(?:EXPERIENCE|EDUCATION|SKILLS|WORK HISTORY|EMPLOYMENT)|\n\n\n|$)',
    ]
    
    for pattern in summary_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # Limit to first 500 chars and ensure non-empty
            if summary:
                return summary[:500] if len(summary) > 500 else summary
    
    # If no section found, return first substantial paragraph as fallback
    # Split by double newlines to get paragraphs
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        cleaned = para.strip()
        # Skip very short paragraphs (likely headers or single lines)
        if len(cleaned) > 50:
            return cleaned[:500] if len(cleaned) > 500 else cleaned
    
    return None


# ---------- Additional heuristic extractors ----------

SECTION_HEADINGS = [
    # Work Experience
    ("work", ["WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EXPERIENCE", "EMPLOYMENT HISTORY", "CAREER HISTORY"]),
    # Education
    ("education", ["EDUCATION", "ACADEMIC BACKGROUND", "QUALIFICATIONS"]),
    # Skills
    ("skills", ["SKILLS", "TECHNICAL SKILLS", "TECH SKILLS", "CORE COMPETENCIES", "TOOLS"]),
]


def find_section_ranges(text: str) -> Dict[str, Tuple[int, int]]:
    """Find start-end indices for common sections using headings."""
    import re
    norm = text
    # Build a combined regex with named groups for robustness
    indices: List[Tuple[str, int]] = []
    for key, headings in SECTION_HEADINGS:
        for h in headings:
            for m in re.finditer(rf"(^|\n)\s*{re.escape(h)}\s*(\n|$)", norm, re.IGNORECASE):
                indices.append((key, m.start()))
    # Sort by position
    indices.sort(key=lambda x: x[1])
    # Compute ranges
    ranges: Dict[str, Tuple[int, int]] = {}
    for i, (key, start) in enumerate(indices):
        end = len(norm) if i == len(indices) - 1 else indices[i + 1][1]
        # Keep the first occurrence for each key
        if key not in ranges:
            ranges[key] = (start, end)
    return ranges


def extract_work_experience(text: str) -> List[Dict[str, str]]:
    rng = find_section_ranges(text).get("work")
    if not rng:
        return []
    section = text[rng[0]:rng[1]].strip()
    lines = [l.strip(" •-\t") for l in section.splitlines() if l.strip()]
    items: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for ln in lines:
        # Heuristic: lines with at least two words and Title Case might be position/company
        if not current:
            current = {"position": ln, "company": "", "description": ""}
        elif not current.get("company") and len(ln.split()) <= 6 and ln.lower().find(" at ") == -1:
            current["company"] = ln
        else:
            current["description"] = (current.get("description", "") + ("\n" if current.get("description") else "") + ln)
        # Split entries by blank lines is already done; rough cap length
        if len(current.get("description", "")) > 400:
            items.append(current)
            current = {}
    if current:
        items.append(current)
    # Keep up to 3 entries
    return items[:3]


def extract_education(text: str) -> List[Dict[str, str]]:
    rng = find_section_ranges(text).get("education")
    if not rng:
        return []
    section = text[rng[0]:rng[1]].strip()
    lines = [l.strip(" •-\t") for l in section.splitlines() if l.strip()]
    items: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for ln in lines:
        if not current:
            current = {"institution": ln, "degree": "", "field": ""}
        elif not current.get("degree") and ("bachelor" in ln.lower() or "master" in ln.lower() or "degree" in ln.lower() or "b.sc" in ln.lower() or "m.sc" in ln.lower()):
            current["degree"] = ln
        elif not current.get("field") and len(ln) < 80:
            current["field"] = ln
        else:
            # treat as additional info
            pass
    if current:
        items.append(current)
    return items[:2]


def extract_skills(text: str) -> List[str]:
    rng = find_section_ranges(text).get("skills")
    if not rng:
        # Try to infer skills by finding common separators in the whole text (fallback)
        candidate_lines = [l for l in text.splitlines() if "," in l or ";" in l]
        tokens: List[str] = []
        for ln in candidate_lines:
            tokens.extend([t.strip() for t in ln.replace(";", ",").split(",") if 1 < len(t.strip()) <= 40])
        # Deduplicate and keep short list
        seen = set()
        uniq: List[str] = []
        for t in tokens:
            k = t.lower()
            if k not in seen:
                seen.add(k)
                uniq.append(t)
        return uniq[:15]
    section = text[rng[0]:rng[1]].strip()
    # Split by commas, semicolons, or bullets
    import re
    parts = re.split(r"[\n,;•]+", section)
    skills = [p.strip() for p in parts if 1 < len(p.strip()) <= 40]
    # Remove heading echoes
    stop = {"skills", "technical skills", "core competencies", "tools"}
    skills = [s for s in skills if s.lower() not in stop]
    # Dedup, cap length
    seen = set()
    out: List[str] = []
    for s in skills:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out[:20]


def ai_enrich(parsed: Dict[str, any]) -> Dict[str, any]:
    """Optional lightweight enrichment without external AI: if summary missing, synthesize from skills."""
    if not parsed.get("professional_summary"):
        skills = parsed.get("skills", [])
        if skills:
            top = ", ".join(skills[:5])
            parsed["professional_summary"] = f"Experienced professional with strengths in {top}. Passionate about delivering impact and continuous improvement."
    return parsed


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    template_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse a resume file (PDF or DOCX).
    Creates a new resume with extracted data.
    """
    # Validate file type
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and DOCX files are supported."
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Save to temp file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "resume.pdf")[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Parse based on file type
        if file.content_type == 'application/pdf':
            parsed_data = parse_pdf_resume(temp_file_path)
        else:
            parsed_data = parse_docx_resume(temp_file_path)
        
        # Check for parsing errors
        if "error" in parsed_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=parsed_data["error"]
            )
        
        # Choose values (allow overrides from form fields)
        final_full_name = full_name or parsed_data.get("full_name")
        final_email = email or parsed_data.get("email")
        final_phone = phone or parsed_data.get("phone")
        final_summary = summary or parsed_data.get("professional_summary")
        final_template = template_id or "modern"

        # Create resume with parsed/overridden data
        resume = Resume(
            user_id=current_user.id,
            title=f"Imported Resume - {file.filename}",
            full_name=final_full_name,
            email=final_email,
            phone=final_phone,
            summary=final_summary,
            template_id=final_template
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Extract and add related data (work experience, education, skills)
        text = parsed_data.get("raw_text", "")
        
        # Add work experiences
        work_experiences = extract_work_experience(text)
        if work_experiences:
            from app.modelsx.resume import WorkExperience
            for exp in work_experiences:
                work_exp = WorkExperience(
                    resume_id=resume.id,
                    position=exp.get("position", ""),
                    company=exp.get("company", ""),
                    start_date=exp.get("start_date"),
                    end_date=exp.get("end_date"),
                    description=exp.get("description", "")
                )
                db.add(work_exp)
        
        # Add education
        education_entries = extract_education(text)
        if education_entries:
            from app.modelsx.resume import Education
            for edu in education_entries:
                education = Education(
                    resume_id=resume.id,
                    degree=edu.get("degree", ""),
                    institution=edu.get("institution", ""),
                    graduation_date=edu.get("graduation_date"),
                    gpa=edu.get("gpa")
                )
                db.add(education)
        
        # Add skills
        skills = extract_skills(text)
        if skills:
            from app.modelsx.resume import ResumeSkill
            for skill in skills:
                skill_entry = ResumeSkill(
                    resume_id=resume.id,
                    name=skill.get("name") if isinstance(skill, dict) else skill,
                    category=skill.get("category") if isinstance(skill, dict) else "Technical",
                    level=skill.get("level") if isinstance(skill, dict) else "Intermediate"
                )
                db.add(skill_entry)
        
        db.commit()
        db.refresh(resume)
        
        return resume
        
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/parse-preview", status_code=status.HTTP_200_OK)
async def parse_resume_preview(
    file: UploadFile = File(...),
    ai: Optional[bool] = Form(False),
    current_user: User = Depends(get_current_user)
):
    """
    Parse resume file and return preview without creating a resume.
    Useful for showing user what will be imported before committing.
    Enhanced error messages for better diagnostics.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate file type
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Only PDF and DOCX files are supported."
        )
    
    # Validate file size
    max_size = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        logger.warning(f"File too large: {len(file_content)} bytes (max {max_size})")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(file_content) // 1024 // 1024}MB). Maximum size is 10MB."
        )
    
    # Save to temp file
    temp_file = None
    try:
        suffix = os.path.splitext(file.filename or "resume.pdf")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Parse based on file type
        logger.info(f"Parsing {file.filename} ({file.content_type})")
        if file.content_type == 'application/pdf':
            parsed_data = parse_pdf_resume(temp_file_path)
        else:
            parsed_data = parse_docx_resume(temp_file_path)
        
        # Check for parse error
        if "error" in parsed_data:
            logger.error(f"Parse error: {parsed_data['error']}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse resume: {parsed_data['error']}"
            )
        
        if "note" in parsed_data and "not installed" in parsed_data.get("raw_text", ""):
            logger.error("Missing parsing library")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Server configuration issue: {parsed_data.get('raw_text')}"
            )

        # Add richer sections
        text = parsed_data.get("raw_text", "")
        if not text.strip():
            logger.warning(f"No text extracted from {file.filename}")
            # Still return what we have so user can see the issue
            parsed_data["note"] = "No text could be extracted from this file. It may be an image-based PDF or corrupted."
        
        parsed_data["work_experience"] = extract_work_experience(text)
        parsed_data["education"] = extract_education(text)
        parsed_data["skills"] = extract_skills(text)

        # Optionally enrich
        if ai:
            parsed_data = ai_enrich(parsed_data)
        
        logger.info(f"Parse successful: {file.filename}")
        return {
            "success": True,
            "filename": file.filename,
            "parsed_data": parsed_data,
            "ai_used": bool(ai),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error parsing {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during parse: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
