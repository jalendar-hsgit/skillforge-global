"""
Unit tests for resume parsing logic in resume_import module.
"""
import pytest
from app.api.v1x.resume_import import (
    extract_email_from_text,
    extract_phone_from_text,
    extract_summary_from_text,
    extract_work_experience,
    extract_education,
    extract_skills,
    ai_enrich,
    find_section_ranges,
)


class TestEmailValidation:
    """Test email extraction with stricter validation."""

    def test_valid_email(self):
        text = "Contact me at john.doe@example.com for more info."
        assert extract_email_from_text(text) == "john.doe@example.com"

    def test_email_with_plus(self):
        text = "Reach out: jane+test@company.co.uk"
        assert extract_email_from_text(text) == "jane+test@company.co.uk"

    def test_no_leading_dot(self):
        text = "Invalid: .bad@example.com"
        result = extract_email_from_text(text)
        # Should not match emails starting with dot
        assert result != ".bad@example.com" if result else True

    def test_no_consecutive_dots(self):
        text = "user..name@example.com"
        result = extract_email_from_text(text)
        assert result is None  # Should reject consecutive dots

    def test_valid_tld_length(self):
        text = "Valid: user@example.museum"
        assert extract_email_from_text(text) == "user@example.museum"

    def test_no_email_found(self):
        text = "No email in this text at all."
        assert extract_email_from_text(text) is None

    def test_multiple_emails_returns_first(self):
        text = "Contacts: first@example.com, second@test.com"
        assert extract_email_from_text(text) == "first@example.com"


class TestPhoneValidation:
    """Test phone extraction with normalization."""

    def test_basic_phone(self):
        text = "Call me at 555-555-1234"
        result = extract_phone_from_text(text)
        assert result is not None
        assert "555" in result

    def test_international_phone(self):
        text = "International: +1 (555) 123-4567"
        result = extract_phone_from_text(text)
        assert result is not None

    def test_no_phone_found(self):
        text = "Just some text with no phone numbers."
        result = extract_phone_from_text(text)
        assert result is None

    def test_short_number_rejected(self):
        text = "Too short: 123-4567"  # Only 7 digits
        result = extract_phone_from_text(text)
        # Should either be None or find a longer match
        if result:
            digits = "".join(c for c in result if c.isdigit())
            assert len(digits) >= 10


class TestSummaryExtraction:
    """Test professional summary extraction."""

    def test_summary_section_found(self):
        text = """
PROFESSIONAL SUMMARY
Experienced developer with 5+ years of building web applications.
Passionate about clean code and user experience.

EXPERIENCE
Senior Developer at Acme Corp
"""
        result = extract_summary_from_text(text)
        assert result is not None
        assert "developer" in result.lower()
        assert len(result) <= 500

    def test_fallback_to_first_paragraph(self):
        text = """
Short intro line.

This is a longer first paragraph with more than fifty characters that should be picked up as a fallback summary when no section is found.

More content here.
"""
        result = extract_summary_from_text(text)
        assert result is not None
        assert "longer first paragraph" in result

    def test_no_summary(self):
        text = "Short text."
        result = extract_summary_from_text(text)
        # May be None or the short text itself
        assert result is None or len(result) > 0


class TestWorkExperienceExtraction:
    """Test work experience section parsing."""

    def test_work_section_found(self):
        text = """
WORK EXPERIENCE

Senior Software Engineer
Acme Corp
Built scalable microservices and led a team of 5 engineers.

Junior Developer
StartupXYZ
Developed frontend features using React and TypeScript.
"""
        result = extract_work_experience(text)
        assert len(result) > 0
        # Check first entry has some data
        assert any(result[0].get(k) for k in ["position", "company", "description"])

    def test_no_work_section(self):
        text = "Just a resume with no clear work section."
        result = extract_work_experience(text)
        assert result == []

    def test_caps_limit(self):
        text = """
EXPERIENCE
""" + "\n".join([f"Job {i}\nCompany {i}\nDescription {i}" for i in range(10)])
        result = extract_work_experience(text)
        # Should cap at 3 entries
        assert len(result) <= 3


class TestEducationExtraction:
    """Test education section parsing."""

    def test_education_section_found(self):
        text = """
EDUCATION

Bachelor of Science in Computer Science
State University
Graduated 2018

Master of Science in AI
Tech Institute
"""
        result = extract_education(text)
        assert len(result) > 0
        # Check first entry
        assert result[0].get("institution") or result[0].get("degree")

    def test_no_education_section(self):
        text = "Resume without education heading."
        result = extract_education(text)
        assert result == []

    def test_caps_limit(self):
        text = """
EDUCATION
""" + "\n".join([f"Degree {i}\nSchool {i}" for i in range(5)])
        result = extract_education(text)
        # Should cap at 2 entries
        assert len(result) <= 2


class TestSkillsExtraction:
    """Test skills section parsing."""

    def test_skills_section_found(self):
        text = """
SKILLS
Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
"""
        result = extract_skills(text)
        assert len(result) > 0
        assert "Python" in result
        assert "JavaScript" in result

    def test_fallback_comma_separated(self):
        text = "Technologies: Java, Spring Boot, PostgreSQL, Redis"
        result = extract_skills(text)
        # Should find some skills via fallback
        assert len(result) > 0

    def test_deduplication(self):
        text = """
SKILLS
Python, JavaScript, Python, React, JavaScript
"""
        result = extract_skills(text)
        # Should deduplicate
        assert result.count("Python") == 1
        assert result.count("JavaScript") == 1

    def test_caps_limit(self):
        text = "SKILLS\n" + ", ".join([f"Skill{i}" for i in range(50)])
        result = extract_skills(text)
        # Should cap at 20
        assert len(result) <= 20


class TestSectionRanges:
    """Test section heading detection."""

    def test_multiple_sections(self):
        text = """
Some intro text.

WORK EXPERIENCE
Senior Dev at Acme

EDUCATION
BS in CS

SKILLS
Python, Java
"""
        ranges = find_section_ranges(text)
        assert "work" in ranges
        assert "education" in ranges
        assert "skills" in ranges

    def test_case_insensitive(self):
        text = """
Work Experience
Dev job

Education
Degree
"""
        ranges = find_section_ranges(text)
        assert "work" in ranges
        assert "education" in ranges


class TestAIEnrichment:
    """Test optional AI enrichment."""

    def test_enriches_missing_summary(self):
        parsed = {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "skills": ["Python", "React", "AWS", "Docker", "SQL"],
        }
        result = ai_enrich(parsed)
        assert "professional_summary" in result
        assert result["professional_summary"]
        assert "Python" in result["professional_summary"]

    def test_preserves_existing_summary(self):
        parsed = {
            "professional_summary": "Existing summary text.",
            "skills": ["Java", "Spring"],
        }
        result = ai_enrich(parsed)
        assert result["professional_summary"] == "Existing summary text."

    def test_no_skills_no_enrichment(self):
        parsed = {"full_name": "John Doe"}
        result = ai_enrich(parsed)
        # Should not add summary if no skills
        assert result.get("professional_summary") is None


class TestEdgeCases:
    """Test edge cases and malformed input."""

    def test_empty_text(self):
        assert extract_email_from_text("") is None
        assert extract_phone_from_text("") is None
        assert extract_work_experience("") == []
        assert extract_education("") == []
        assert extract_skills("") == []

    def test_very_long_text(self):
        text = "Lorem ipsum " * 10000
        # Should not crash
        result = extract_summary_from_text(text)
        if result:
            assert len(result) <= 500

    def test_special_characters(self):
        text = "Email: test@example.com\nPhone: +1-555-1234\nSkills: C++, C#, .NET"
        assert extract_email_from_text(text) == "test@example.com"
        assert extract_phone_from_text(text) is not None
        skills = extract_skills(text)
        # Should handle special chars in skills
        assert any("C++" in s or "C#" in s or ".NET" in s for s in skills)
