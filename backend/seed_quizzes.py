"""
Seed quizzes into the database from quizzes.json
"""
import sys
import json
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.db import SessionLocal

def seed_quizzes():
    """Seed quizzes from JSON file into database"""
    
    # Read quizzes.json
    quizzes_file = Path(__file__).parent / "app" / "data" / "quizzes.json"
    
    if not quizzes_file.exists():
        print(f"❌ Quizzes file not found: {quizzes_file}")
        return
    
    with open(quizzes_file, 'r', encoding='utf-8') as f:
        quizzes_data = json.load(f)
    
    db = SessionLocal()
    
    try:
        # Map of path slugs to course IDs (assuming courses exist)
        path_to_course = {
            'python-ai': 1,
            'fullstack': 2,
            'aws-devops': 3,
            'cybersec': 4,
            'flutter': 5
        }
        
        for slug, quiz_data in quizzes_data.items():
            print(f"\n📝 Processing quiz: {slug}")
            
            course_id = path_to_course.get(slug, 1)
            title = quiz_data.get('title', f'Quiz for {slug}')
            
            # Check if quiz already exists for this course
            existing = db.execute(
                text("SELECT id FROM quizzes WHERE course_id=:cid"),
                {"cid": course_id}
            ).first()
            
            if existing:
                quiz_id = existing[0]
                print(f"  ✓ Quiz already exists with ID: {quiz_id}")
            else:
                # Insert quiz
                result = db.execute(
                    text("INSERT INTO quizzes (course_id, title, path_slug) VALUES (:cid, :title, :slug) RETURNING id"),
                    {"cid": course_id, "title": title, "slug": slug}
                )
                quiz_id = result.fetchone()[0]
                db.commit()
                print(f"  ✓ Created quiz with ID: {quiz_id}")
            
            # Delete existing questions for this quiz
            db.execute(text("DELETE FROM quiz_questions WHERE quiz_id=:qid"), {"qid": quiz_id})
            
            # Insert questions
            questions = quiz_data.get('questions', [])
            for q in questions:
                q_text = q.get('text', '')
                options = q.get('options', [])
                answer_index = q.get('answerIndex', 0)
                
                # Store answer as the text of the correct option
                correct_answer = options[answer_index] if answer_index < len(options) else ""
                
                db.execute(
                    text("""
                        INSERT INTO quiz_questions (quiz_id, question, options, answer)
                        VALUES (:qid, :q_text, :options, :answer)
                    """),
                    {
                        "qid": quiz_id,
                        "q_text": q_text,
                        "options": json.dumps(options),
                        "answer": correct_answer
                    }
                )
            
            db.commit()
            print(f"  ✓ Inserted {len(questions)} questions")
        
        print("\n✅ All quizzes seeded successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding quizzes: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding quizzes into database...\n")
    seed_quizzes()
