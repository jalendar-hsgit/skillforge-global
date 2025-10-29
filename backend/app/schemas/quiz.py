from pydantic import BaseModel
from typing import List, Optional

class QuizQuestion(BaseModel):
    id: str
    type: str  # "mcq" for now
    text: str
    options: List[str]
    answerIndex: int
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: str
    title: str
    questions: List[QuizQuestion]

class QuizEnvelope(BaseModel):
    id: str
    title: str
    questions: List[QuizQuestion]

class QuizSubmitItem(BaseModel):
    id: str
    answerIndex: int

class QuizSubmitIn(BaseModel):
    path: str
    answers: List[QuizSubmitItem]

class QuizSubmitOutItem(BaseModel):
    id: str
    correct: bool
    correctIndex: int
    explanation: Optional[str] = None

class QuizSubmitOut(BaseModel):
    score: int
    total: int
    results: List[QuizSubmitOutItem]
