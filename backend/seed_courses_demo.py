"""Seed demo courses if table is empty (non-destructive)."""
from app.core.db import SessionLocal
from app.modelsx.course import Course
import json

def seed_courses():
    db = SessionLocal()
    try:
        count = db.query(Course).count()
        if count > 0:
            print(f"✓ Courses table already has {count} rows, skipping seed")
            return
        
        print("⚡ Courses table is empty, seeding demo courses...")
        courses_data = [
            {
                "title": "Python for Beginners",
                "description": "Learn Python basics from scratch",
                "instructor": "John Doe",
                "duration_hours": 40,
                "level": "beginner",
                "category": "programming",
                "image_url": "https://via.placeholder.com/300",
                "price": 49.99,
                "is_published": True
            },
            {
                "title": "Advanced JavaScript",
                "description": "Master async/await, closures, and modern JS",
                "instructor": "Jane Smith",
                "duration_hours": 50,
                "level": "advanced",
                "category": "web-development",
                "image_url": "https://via.placeholder.com/300",
                "price": 79.99,
                "is_published": True
            },
            {
                "title": "Data Science Fundamentals",
                "description": "Pandas, NumPy, and data visualization",
                "instructor": "Dr. Alex Johnson",
                "duration_hours": 60,
                "level": "intermediate",
                "category": "data-science",
                "image_url": "https://via.placeholder.com/300",
                "price": 99.99,
                "is_published": True
            }
        ]
        
        for course_data in courses_data:
            course = Course(**course_data)
            db.add(course)
        
        db.commit()
        print(f"✓ Created {len(courses_data)} demo courses")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_courses()
