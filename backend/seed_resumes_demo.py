"""Seed demo resumes for test users if table is empty (non-destructive)."""
from app.core.db import SessionLocal
from app.models.user import User
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeSkill
from datetime import datetime, timedelta

def seed_resumes():
    db = SessionLocal()
    try:
        count = db.query(Resume).count()
        if count > 0:
            print(f"✓ Resumes table already has {count} rows, skipping seed")
            return
        
        print("⚡ Resumes table is empty, seeding demo resumes...")
        
        # Get test users
        users = {
            'superadmin': db.query(User).filter(User.email == 'superadmin@skillforge.com').first(),
            'admin': db.query(User).filter(User.email == 'admin@skillforge.com').first(),
            'mentor': db.query(User).filter(User.email == 'mentor@skillforge.com').first(),
            'user': db.query(User).filter(User.email == 'user@skillforge.com').first(),
        }
        
        if not users['user']:
            print("⚠ user@skillforge.com not found, skipping resume seed")
            return
        
        # Create resume for regular user
        resume = Resume(
            user_id=users['user'].id,
            title="Software Engineer",
            full_name="Alex Johnson",
            email="alex@example.com",
            phone="+1-234-567-8900",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/alexjohnson",
            summary="Experienced software engineer with 5 years of full-stack development expertise.",
            ats_score=85.5,
            is_active=True
        )
        db.add(resume)
        db.flush()  # Get resume.id
        
        # Add work experience
        exp = WorkExperience(
            resume_id=resume.id,
            company="Tech Corp",
            position="Senior Software Engineer",
            location="San Francisco, CA",
            start_date=(datetime.now() - timedelta(days=730)).date(),
            end_date=None,
            description="Lead full-stack development for cloud platform",
            bullet_points=["Architected microservices", "Led team of 5 engineers", "Improved performance by 40%"]
        )
        db.add(exp)
        
        # Add education
        edu = Education(
            resume_id=resume.id,
            institution="University of California",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            start_date=datetime(2015, 9, 1).date(),
            end_date=datetime(2019, 5, 31).date()
        )
        db.add(edu)
        
        # Add skills
        for skill_name in ["Python", "JavaScript", "React", "PostgreSQL", "AWS"]:
            skill = ResumeSkill(
                resume_id=resume.id,
                skill_name=skill_name,
                proficiency_level="Expert"
            )
            db.add(skill)
        
        db.commit()
        print(f"✓ Created 1 demo resume with 5 skills, 1 work experience, 1 education")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_resumes()
