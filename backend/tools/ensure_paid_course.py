"""
Ensure the DB has at least one paid course (and a sample video) for marketplace tests.
Safe to run multiple times.
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from pathlib import Path

from app.core.config import settings
from app.modelsx.course import Course
from app.modelsx.video import Video


def ensure_paid_course(session: Session) -> Course:
    # Look for any paid course
    course = session.query(Course).filter(Course.is_paid == True).first()
    if course:
        return course

    # Create one if missing
    course = Course(
        path="pro-python-basics",
        title="Pro Python Basics",
        description="A paid sample course used for automated tests.",
        category="testing",
        is_paid=True,
        price=Decimal("49.00"),
    )
    session.add(course)
    session.flush()  # get course.id

    # Add a sample video so detail page has content
    vid = Video(
        course_id=course.id,
        title="Welcome and Setup",
        youtube_id="dQw4w9WgXcQ",
        duration="5m",
    )
    session.add(vid)
    session.commit()
    session.refresh(course)
    return course


def main():
    # Ensure DB file directory exists for sqlite
    if settings.DATABASE_URL.startswith("sqlite"):
        # sqlite:///./app/data/skillforge.db -> ensure directory exists
        p = settings.DATABASE_URL.split("sqlite:///")[-1]
        path = Path(p)
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(settings.DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        course = ensure_paid_course(session)
        print({
            "id": course.id,
            "path": course.path,
            "title": course.title,
            "is_paid": course.is_paid,
            "price": float(course.price) if course.price else None,
        })


if __name__ == "__main__":
    main()
