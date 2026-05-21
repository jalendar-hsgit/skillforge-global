"""
Seed script to create demo mentor reviews for completed sessions
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.db import SessionLocal
from app.modelsx.mentor import MentorSession, MentorReview, SessionStatus
from app.models.user import User
from datetime import datetime, timedelta
import random

def seed_mentor_reviews():
    """Create reviews for completed mentor sessions"""
    db = SessionLocal()
    
    try:
        print("\n=== Seeding Mentor Reviews ===\n")
        
        # Get all completed sessions without reviews
        completed_sessions = db.query(MentorSession).filter(
            MentorSession.status == SessionStatus.COMPLETED
        ).all()
        
        if not completed_sessions:
            print("No completed sessions found. Updating some sessions to completed first...")
            
            # Update some pending/confirmed sessions to completed
            sessions_to_complete = db.query(MentorSession).filter(
                MentorSession.status.in_([SessionStatus.PENDING, SessionStatus.CONFIRMED])
            ).limit(20).all()
            
            for session in sessions_to_complete:
                # Set as completed if scheduled time has passed
                if session.scheduled_at < datetime.utcnow():
                    session.status = SessionStatus.COMPLETED
                    session.completed_at = session.scheduled_at + timedelta(hours=1)
                    print(f"  Marked session {session.id} as completed")
            
            db.commit()
            
            # Requery completed sessions
            completed_sessions = db.query(MentorSession).filter(
                MentorSession.status == SessionStatus.COMPLETED
            ).all()
        
        print(f"Found {len(completed_sessions)} completed sessions")
        
        # Check for existing reviews
        existing_reviews = {review.session_id for review in db.query(MentorReview).all()}
        print(f"Found {len(existing_reviews)} existing reviews")
        
        # Create reviews for sessions without them
        reviews_created = 0
        review_texts = [
            "Excellent mentor! Very knowledgeable and patient.",
            "Great session, learned a lot about the topic.",
            "Very helpful and clear explanations.",
            "Amazing mentor, highly recommend!",
            "Good session, covered all my questions.",
            "Fantastic experience, will book again.",
            "Very professional and well-prepared.",
            "Helpful session, got exactly what I needed.",
            "Outstanding mentor with great teaching skills.",
            "Solid session, good value for money.",
            "Extremely helpful and knowledgeable.",
            "Perfect session, exceeded my expectations.",
            "Very patient and easy to understand.",
            "Great insights and practical advice.",
            "Wonderful mentor, very encouraging."
        ]
        
        tag_options = [
            "Knowledgeable,Patient,Clear",
            "Helpful,Professional,Prepared",
            "Experienced,Friendly,Supportive",
            "Expert,Encouraging,Practical",
            "Skilled,Responsive,Thorough"
        ]
        
        for session in completed_sessions:
            if session.id not in existing_reviews:
                # Create a review with 4-5 star rating
                rating = random.choice([4, 4, 5, 5, 5])  # Bias towards 5 stars
                review_text = random.choice(review_texts)
                tags = random.choice(tag_options)
                
                review = MentorReview(
                    mentor_id=session.mentor_id,
                    session_id=session.id,
                    student_id=session.student_id,
                    rating=rating,
                    review_text=review_text,
                    tags=tags,
                    created_at=session.completed_at or datetime.utcnow()
                )
                
                db.add(review)
                reviews_created += 1
                
                print(f"  Created {rating} star review for session {session.id}")
        
        db.commit()
        
        print(f"\nCreated {reviews_created} new mentor reviews")
        
        # Update mentor average ratings
        from sqlalchemy import func
        from app.modelsx.mentor import Mentor
        
        mentors = db.query(Mentor).all()
        for mentor in mentors:
            avg_rating = db.query(func.avg(MentorReview.rating)).filter(
                MentorReview.mentor_id == mentor.id
            ).scalar()
            
            if avg_rating:
                mentor.average_rating = float(avg_rating)
                print(f"  Updated mentor {mentor.id} average rating: {avg_rating:.2f}")
        
        db.commit()
        
        print("\nMentor reviews seeded successfully!")
        print(f"   Total reviews: {len(existing_reviews) + reviews_created}")
        print(f"   Completed sessions: {len(completed_sessions)}")
        
    except Exception as e:
        print(f"\nError seeding reviews: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_mentor_reviews()
