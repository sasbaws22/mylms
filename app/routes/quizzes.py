
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List

from app.db.database import get_session
from app.services.quiz_service import QuizService
from app.schemas.quiz import (
    QuizCreateSchema, QuizUpdateSchema, QuizDetailSchema, QuizSummarySchema,
    QuestionCreateSchema, QuestionUpdateSchema, QuestionSchema,
    QuizResponseDetailSchema, QuizAttemptStartSchema,
    PaginatedQuizzesResponse, PaginatedQuizAttemptsResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/", response_model=PaginatedQuizzesResponse)
async def get_quizzes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    module_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of quizzes"""
    quiz_service = QuizService(db)
    return quiz_service.get_quizzes(page, limit, search, module_id)


@router.post("/", response_model=QuizDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new quiz"""
    quiz_service = QuizService(db)
    return quiz_service.create_quiz(quiz_data)


@router.get("/{quiz_id}", response_model=QuizDetailSchema)
async def get_quiz_by_id(
    quiz_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get quiz by ID with detailed information"""
    quiz_service = QuizService(db)
    return quiz_service.get_quiz_by_id(quiz_id)


@router.put("/{quiz_id}", response_model=QuizDetailSchema)
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update quiz information"""
    quiz_service = QuizService(db)
    return quiz_service.update_quiz(quiz_id, quiz_data)


@router.delete("/{quiz_id}", response_model=MessageResponse)
async def delete_quiz(
    quiz_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a quiz"""
    quiz_service = QuizService(db)
    result = quiz_service.delete_quiz(quiz_id)
    return MessageResponse(message=result["message"])


@router.post("/{quiz_id}/questions", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
async def add_question_to_quiz(
    quiz_id: str,
    question_data: QuestionCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Add a question to a quiz"""
    quiz_service = QuizService(db)
    return quiz_service.add_question_to_quiz(quiz_id, question_data)


@router.put("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(
    question_id: str,
    question_data: QuestionUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update question information"""
    quiz_service = QuizService(db)
    return quiz_service.update_question(question_id, question_data)


@router.delete("/questions/{question_id}", response_model=MessageResponse)
async def delete_question(
    question_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a question"""
    quiz_service = QuizService(db)
    result = quiz_service.delete_question(question_id)
    return MessageResponse(message=result["message"])


@router.post("/{quiz_id}/attempts", response_model=QuizDetailSchema, status_code=status.HTTP_201_CREATED)
async def submit_quiz_attempt(
    quiz_id: str,
    attempt_data: QuizAttemptStartSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Submit a quiz attempt"""
    quiz_service = QuizService(db)
    return quiz_service.submit_quiz_attempt(quiz_id, current_user.username, attempt_data)


@router.get("/{quiz_id}/attempts", response_model=PaginatedQuizAttemptsResponse)
async def get_quiz_attempts(
    quiz_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of quiz attempts for a quiz"""
    quiz_service = QuizService(db)
    return quiz_service.get_quiz_attempts(quiz_id, page, limit, user_id)


@router.get("/attempts/{attempt_id}", response_model=QuizResponseDetailSchema)
async def get_quiz_attempt_by_id(
    attempt_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get quiz attempt by ID with detailed information"""
    quiz_service = QuizService(db)
    return quiz_service.get_quiz_attempt_by_id(attempt_id)


# Create router instance for export
quizzes_router = router


