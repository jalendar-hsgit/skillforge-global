"""
Resume ATS Scoring Service
Calculates ATS score based on resume content and formatting
"""

from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass
from enum import Enum

ATS_KEYWORDS = {
    "technical": [
        "python", "javascript", "java", "c++", "c#", "sql", "html", "css",
        "react", "angular", "vue", "django", "flask", "fastapi", "nodejs", "express",
        "mongodb", "mysql", "postgresql", "aws", "azure", "gcp", "docker", "kubernetes",
        "git", "ci/cd", "api", "rest", "graphql", "machine learning", "ai",
        "data analysis", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "project management",
        "problem solving", "critical thinking", "time management", "adaptability",
        "collaboration", "mentoring", "presentation", "negotiation"
    ],
    "certifications": [
        "aws", "azure", "gcp", "certified", "credential", "certification",
        "cpa", "pmp", "scrum", "cissp", "ccna"
    ],
    "methodologies": [
        "agile", "scrum", "kanban", "waterfall", "lean", "six sigma",
        "devops", "tdd", "bdd", "microservices"
    ]
}

@dataclass
class ATSScoreCriteria:
    """Individual scoring criteria"""
    name: str
    score: float
    max_score: float
    weight: float
    details: str

class ATSScorer:
    """
    ATS (Applicant Tracking System) Score Calculator
    Evaluates resume based on commonly tracked metrics
    """
    
    def __init__(self):
        self.scores: List[ATSScoreCriteria] = []
    
    def calculate_score(self, resume_text: str) -> Dict[str, Any]:
        """
        Calculate overall ATS score for a resume.
        Returns score (0-100) and detailed breakdown.
        """
        self.scores = []
        text_lower = resume_text.lower()
        
        # Calculate individual metrics
        self._score_keyword_match(text_lower)
        self._score_formatting(resume_text)
        self._score_section_completeness(text_lower)
        self._score_experience_clarity(resume_text)
        self._score_skill_specificity(text_lower)
        self._score_formatting_issues(resume_text)
        
        # Calculate weighted overall score
        total_score = sum(c.score * c.weight for c in self.scores)
        max_possible = sum(c.max_score * c.weight for c in self.scores)
        overall_score = int((total_score / max_possible * 100) if max_possible > 0 else 0)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(text_lower, resume_text)
        
        return {
            "overall_score": overall_score,
            "breakdown": [
                {
                    "name": c.name,
                    "score": int(c.score),
                    "max_score": int(c.max_score),
                    "weight": c.weight,
                    "percentage": int((c.score / c.max_score * 100) if c.max_score > 0 else 0),
                    "details": c.details
                }
                for c in self.scores
            ],
            "suggestions": suggestions,
            "ats_friendly": overall_score >= 75
        }
    
    def _score_keyword_match(self, text_lower: str):
        """Score based on technical and soft skill keywords"""
        max_score = 25
        found_keywords = 0
        total_keywords = 0
        
        for category, keywords in ATS_KEYWORDS.items():
            for keyword in keywords:
                total_keywords += 1
                if keyword in text_lower:
                    found_keywords += 1
        
        keyword_score = (found_keywords / total_keywords * max_score) if total_keywords > 0 else 0
        
        self.scores.append(ATSScoreCriteria(
            name="Keyword Matching",
            score=keyword_score,
            max_score=max_score,
            weight=1.0,
            details=f"Found {found_keywords}/{total_keywords} important keywords"
        ))
    
    def _score_formatting(self, text: str):
        """Score based on formatting consistency"""
        max_score = 15
        score = 15  # Start with full score
        
        # Deduct for common formatting issues
        issues = 0
        
        # Check for excessive bullet points or formatting inconsistency
        lines = text.split('\n')
        if len(lines) < 10:
            score -= 5
            issues += 1
        
        # Check for consistent use of dates
        date_pattern = r'\d{4}[-/]\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
        date_matches = len(re.findall(date_pattern, text.lower()))
        if date_matches < 3:
            score -= 3
            issues += 1
        
        # Check for email/phone formatting
        if not re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            score -= 2
            issues += 1
        
        score = max(0, score)
        
        self.scores.append(ATSScoreCriteria(
            name="Formatting",
            score=score,
            max_score=max_score,
            weight=1.0,
            details=f"Formatting issues found: {issues}"
        ))
    
    def _score_section_completeness(self, text_lower: str):
        """Score based on required resume sections"""
        max_score = 20
        score = 0
        sections_found = 0
        
        required_sections = {
            "contact": ["email", "phone", "linkedin"],
            "summary": ["summary", "professional", "objective"],
            "experience": ["experience", "work", "employment"],
            "education": ["education", "degree", "university"],
            "skills": ["skills", "technical", "competencies"]
        }
        
        for section, keywords in required_sections.items():
            found = any(kw in text_lower for kw in keywords)
            if found:
                sections_found += 1
                score += 4
        
        self.scores.append(ATSScoreCriteria(
            name="Section Completeness",
            score=score,
            max_score=max_score,
            weight=1.0,
            details=f"Found {sections_found}/{len(required_sections)} key sections"
        ))
    
    def _score_experience_clarity(self, text: str):
        """Score based on clear experience descriptions"""
        max_score = 20
        score = 0
        
        # Check for job titles
        job_title_keywords = ["developer", "engineer", "manager", "analyst", "designer",
                            "architect", "specialist", "consultant", "lead", "director"]
        job_count = sum(text.lower().count(kw) for kw in job_title_keywords)
        score += min(10, job_count * 2)
        
        # Check for action verbs (indicates strong experience descriptions)
        action_verbs = ["developed", "designed", "led", "managed", "implemented",
                       "created", "built", "achieved", "improved", "increased",
                       "reduced", "optimized", "collaborated", "mentored"]
        verb_count = sum(text.lower().count(verb) for verb in action_verbs)
        score += min(10, verb_count * 1.5)
        
        score = min(max_score, score)
        
        self.scores.append(ATSScoreCriteria(
            name="Experience Clarity",
            score=score,
            max_score=max_score,
            weight=1.0,
            details=f"Found {job_count} job titles and {verb_count} action verbs"
        ))
    
    def _score_skill_specificity(self, text_lower: str):
        """Score based on specific vs. generic skills mentioned"""
        max_score = 10
        score = 0
        
        specific_skills = 0
        generic_count = sum(text_lower.count(skill) for skill in 
                          ["leadership", "communication", "teamwork"])
        
        # Count specific technical skills
        tech_skills = ["python", "java", "javascript", "sql", "react",
                      "aws", "docker", "kubernetes", "git"]
        specific_skills = sum(text_lower.count(skill) for skill in tech_skills)
        
        # Balance: too many generic is bad
        if specific_skills > generic_count:
            score = 10
        elif specific_skills > 0:
            score = 8
        else:
            score = 5
        
        self.scores.append(ATSScoreCriteria(
            name="Skill Specificity",
            score=score,
            max_score=max_score,
            weight=1.0,
            details=f"Specific skills: {specific_skills}, Generic skills: {generic_count}"
        ))
    
    def _score_formatting_issues(self, text: str):
        """Deduct points for common ATS-unfriendly formatting"""
        max_score = 10
        score = 10
        
        issues = []
        
        # Check for tables (ATS unfriendly)
        if re.search(r'\|.*\|', text):
            score -= 2
            issues.append("Contains table formatting (ATS may not parse correctly)")
        
        # Check for graphics/image references
        if any(word in text.lower() for word in ["[image]", "<image>", "figure", "graphic"]):
            score -= 2
            issues.append("Contains image/graphic references")
        
        # Check for excessive special characters
        special_char_count = len(re.findall(r'[^a-zA-Z0-9\s\-._@,()]', text))
        if special_char_count > len(text) * 0.05:
            score -= 2
            issues.append("Contains too many special characters")
        
        # Check for very long words (might be format issues)
        words = text.split()
        long_words = sum(1 for w in words if len(w) > 20)
        if long_words > 5:
            score -= 1
            issues.append("Contains multiple very long words")
        
        score = max(0, score)
        
        self.scores.append(ATSScoreCriteria(
            name="Formatting Issues",
            score=score,
            max_score=max_score,
            weight=1.0,
            details=f"Issues found: {', '.join(issues) if issues else 'None'}"
        ))
    
    def _generate_suggestions(self, text_lower: str, text: str) -> List[str]:
        """Generate actionable suggestions based on scoring"""
        suggestions = []
        
        # Keyword suggestions
        missing_keywords = []
        for category, keywords in list(ATS_KEYWORDS.items())[:2]:  # Check first 2 categories
            for keyword in keywords[:5]:  # Check first 5 of each
                if keyword not in text_lower:
                    missing_keywords.append(keyword)
        
        if missing_keywords:
            suggestions.append(
                f"Add relevant keywords: {', '.join(missing_keywords[:3])} "
                "in your experience or skills section"
            )
        
        # Section suggestions
        if "summary" not in text_lower:
            suggestions.append("Add a professional summary or objective statement at the top")
        
        if "linkedin" not in text_lower:
            suggestions.append("Include your LinkedIn profile URL in contact information")
        
        # Formatting suggestions
        action_verbs = ["developed", "designed", "led", "managed"]
        action_count = sum(text_lower.count(v) for v in action_verbs)
        if action_count < 5:
            suggestions.append(
                "Use more action verbs (developed, designed, led, managed) "
                "to describe your accomplishments"
            )
        
        # Specific achievement suggestions
        achievement_markers = ["increased", "improved", "reduced", "achieved"]
        achievement_count = sum(text_lower.count(m) for m in achievement_markers)
        if achievement_count < 3:
            suggestions.append(
                "Add quantifiable achievements (e.g., 'Improved performance by 25%')"
            )
        
        # Return top suggestions
        return suggestions[:4]


# Singleton instance
ats_scorer = ATSScorer()
