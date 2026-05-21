from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import JSON
from datetime import datetime
from app.core.db import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)

    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=False)     # ["a","b","c","d"] or full text options
    answer = Column(String, nullable=False)    # expected option value

    quiz = relationship("Quiz", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)     # FK to your existing users table
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    # Time tracking fields for enhanced analytics (NEW)
    completed_at = Column(DateTime, nullable=True)  # When quiz was finished
    time_spent_seconds = Column(Integer, nullable=True, default=0)  # Total time in seconds
    question_times = Column(JSON, nullable=True)  # {question_id: time_in_seconds}
    answers = Column(JSON, nullable=True)  # {question_id: selected_answer}
