from fastapi import APIRouter

router = APIRouter(prefix="/quizzes-db", tags=["quizzes-db"])

@router.get("")
def list_quizzes_db():
    return []
