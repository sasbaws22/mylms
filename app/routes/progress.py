
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List

from app.db.database import get_session
from app.services.progress_service import ProgressService
from app.schemas.progress import (
    UserCourseProgressSchema, ModuleProgressSchema, ContentProgressSchema,
    ProgressUpdateSchema, PaginatedUserCourseProgressResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

progress_router = APIRouter()


@progress_router.get("/users/{user_id}/courses", response_model=PaginatedUserCourseProgressResponse)
async def get_user_course_progress(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of course progress for a specific user"""
    progress_service = ProgressService(db)
    return await progress_service.get_user_course_progress(user_id, page, limit)


@progress_router.get("/users/{user_id}/courses/{course_id}", response_model=UserCourseProgressSchema)
async def get_user_progress_for_course(
    user_id: str,
    course_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get detailed progress for a user in a specific course"""
    progress_service = ProgressService(db)
    return await progress_service.get_user_progress_for_course(user_id, course_id)


@progress_router.post("/update", response_model=ContentProgressSchema)
async def update_content_progress(
    progress_data: ProgressUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update progress for a specific content item (module, video, document)"""
    progress_service = ProgressService(db) 
    id = current_user.get("sub")
    return await progress_service.update_content_progress(id, progress_data)


@progress_router.get("/modules/{module_id}/progress", response_model=List[ContentProgressSchema])
async def get_module_content_progress(
    module_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get progress for all content items within a module for the current user"""
    progress_service = ProgressService(db) 
    id = current_user.get("sub")
    return await progress_service.get_module_content_progress(id, module_id)


# Create router instance for export
progress_router = progress_router


