"""Seed a sample resume with content for export testing.
Run: python tools/seed_sample_resume.py
"""
import sys
import os
from datetime import datetime

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.db import SessionLocal
from app.modelsx.resume import Resume, WorkExperience, Education, ResumeProject, ResumeSkill, ResumeCertificate


def seed():
    db = SessionLocal()
    try:
        # Create a sample user if none exists (assume user id 1 exists in many dev setups)
        user_id = 1

        resume = Resume(
            user_id=user_id,
            title='Sample Resume',
            full_name='Jane Doe',
            email='jane.doe@example.com',
            phone='555-123-4567',
            location='Seattle, WA',
            summary='Experienced software engineer with a focus on building reliable APIs.',
            font_family='Inter',
            layout='modern',
            accent_color='#0ea5e9',
            heading_color='#0369a1',
            text_color='#0f172a',
            page_size='A4',
            page_margins={'top':20,'bottom':20,'left':20,'right':20}
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        we = WorkExperience(
            resume_id=resume.id,
            company='Acme Corp',
            position='Senior Backend Engineer',
            location='Remote',
            start_date='Jan 2021',
            end_date='Present',
            is_current=True,
            description='Led backend team and improved API performance by 40%.',
            bullet_points=['Designed microservices', 'Improved test coverage']
        )
        edu = Education(
            resume_id=resume.id,
            institution='State University',
            degree='B.Sc. Computer Science',
            field_of_study='Computer Science',
            start_date='2015',
            end_date='2019',
            gpa='3.8'
        )
        proj = ResumeProject(
            resume_id=resume.id,
            title='Open Source Library',
            description='A reusable library for parsing resumes.',
            tech_stack=['Python','FastAPI','Postgres'],
            github_url='https://github.com/example/library'
        )
        skill = ResumeSkill(
            resume_id=resume.id,
            name='Python',
            category='Programming',
            proficiency='Expert',
            years_of_experience=6
        )
        cert = ResumeCertificate(
            resume_id=resume.id,
            name='Certified Developer',
            issuing_organization='Example Org',
            issue_date='2023-05-01'
        )

        db.add_all([we, edu, proj, skill, cert])
        db.commit()

        print(f"Seeded resume id={resume.id}")
    finally:
        db.close()

if __name__ == '__main__':
    seed()
