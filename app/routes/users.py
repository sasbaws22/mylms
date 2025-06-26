"""
User management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional

from app.db.database import get_session
from app.services.user_service import UserService
from app.schemas.user import (
    UserListParams, UserDetailSchema, UserCreateSchema, UserUpdateSchema,
    UserStatsSchema
)
from app.schemas.auth import UserProfileSchema, TokenData
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer

router = APIRouter()


@router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of users"""
    user_service = UserService(db)
    params = UserListParams(
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await user_service.get_users(params, page, limit)


@router.post("/", response_model=UserDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new user (admin function)"""
    user_service = UserService(db)
    return await user_service.create_user(user_data)


@router.get("/stats", response_model=UserStatsSchema)
async def get_user_stats(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get user statistics"""
    user_service = UserService(db)
    return await user_service.get_user_stats()


@router.get("/profile", response_model=UserProfileSchema)
async def get_current_user_profile(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    print (f"Current user: {current_user}")
    """Get current user profile"""
    user_service = UserService(db) 
    id = current_user.get("sub")
   
    return await  user_service.get_user_by_id(id)


@router.put("/profile", response_model=UserDetailSchema)
async def update_current_user_profile(
    user_data: UserUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update current user profile"""
    user_service = UserService(db)
    id = current_user.get("sub")
    return await user_service.update_user(id, user_data)


@router.get("/{user_id}", response_model=UserDetailSchema)
async def get_user_by_id(
    user_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get user by ID"""
    user_service = UserService(db)
    return await user_service.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserDetailSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update user information"""
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Deactivate user account"""
    user_service = UserService(db)
    result = user_service.deactivate_user(user_id)
    return MessageResponse(message=result["message"])


# Create router instance for export
users_router = router


