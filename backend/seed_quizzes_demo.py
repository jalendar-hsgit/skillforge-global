"""Seed demo quizzes if table is empty (non-destructive)."""
from app.core.db import SessionLocal
from app.modelsx.quiz import Quiz
import json

def seed_quizzes():
    db = SessionLocal()
    try:
        count = db.query(Quiz).count()
        if count > 0:
            print(f"✓ Quizzes table already has {count} rows, skipping seed")
            return
        
        print("⚡ Quizzes table is empty, seeding demo quizzes...")
        quizzes_data = [
            {
                "title": "Python Basics Quiz",
                "description": "Test your Python fundamentals",
                "category": "python",
                "difficulty": "beginner",
                "questions_count": 10,
                "passing_score": 70,
                "time_limit_minutes": 15,
                "is_published": True,
                "questions": json.dumps([
                    {
                        "question": "What is the output of print(2 ** 3)?",
                        "options": ["6", "8", "9", "12"],
                        "correct_answer": "8"
                    },
                    {
                        "question": "Which of these is a mutable data type?",
                        "options": ["tuple", "string", "list", "int"],
                        "correct_answer": "list"
                    }
                ])
            },
            {
                "title": "JavaScript ES6 Quiz",
                "description": "Modern JavaScript features",
                "category": "javascript",
                "difficulty": "intermediate",
                "questions_count": 8,
                "passing_score": 75,
                "time_limit_minutes": 20,
                "is_published": True,
                "questions": json.dumps([
                    {
                        "question": "What does 'const' mean in JavaScript?",
                        "options": ["Variable", "Constant", "Constructor", "Container"],
                        "correct_answer": "Constant"
                    }
                ])
            }
        ]
        
        for quiz_data in quizzes_data:
            quiz = Quiz(**quiz_data)
            db.add(quiz)
        
        db.commit()
        print(f"✓ Created {len(quizzes_data)} demo quizzes")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_quizzes()
