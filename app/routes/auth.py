"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_session
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginSchema, TokenResponseSchema, RefreshTokenSchema,
    UserRegistrationSchema, ForgotPasswordSchema, ResetPasswordSchema,
    ChangePasswordSchema, UserResponseSchema, UserProfileSchema, TokenData
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer

router = APIRouter()


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistrationSchema,
    db: Session = Depends(get_session)
):
    """Register a new user account"""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponseSchema)
async def login_user(
    login_data: LoginSchema,
    db: Session = Depends(get_session)
):
    """User login with email and password"""
    auth_service = AuthService(db)
    return await auth_service.login_user(login_data)


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_access_token(
    refresh_data: RefreshTokenSchema,
    db: Session = Depends(get_session)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: TokenData = Depends(access_token_bearer)
):
    """Logout user and invalidate tokens"""
    # In a real implementation, you would add the token to a blacklist
    # For now, we'll just return a success message
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPasswordSchema,
    db: Session = Depends(get_session)
):
    """Request password reset email"""
    auth_service = AuthService(db)
    result = await auth_service.forgot_password(forgot_data)
    return MessageResponse(message=result["message"])


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordSchema,
    db: Session = Depends(get_session)
):
    """Reset password using reset token"""
    auth_service = AuthService(db)
    result = await auth_service.reset_password(reset_data)
    return MessageResponse(message=result["message"])


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    change_data: ChangePasswordSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Change user password"""
    auth_service = AuthService(db)
    result = await auth_service.change_password(current_user.username, change_data)
    return MessageResponse(message=result["message"])


@router.get("/profile", response_model=UserProfileSchema)
async def get_current_user_profile(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get current user profile"""
    auth_service = AuthService(db) 
    id = current_user.get("sub")
    return await auth_service.get_current_user_profile(id)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_code: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Verify user email address"""
    auth_service = AuthService(db)
    result = await auth_service.verify_email(current_user.username, verification_code)
    return MessageResponse(message=result["message"])


@router.get("/me", response_model=UserProfileSchema)
async def get_me(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get current user information (alias for /profile)"""
    auth_service = AuthService(db) 
    id = current_user.get("sub")
    return await auth_service.get_current_user_profile(id)


# Create router instance for export
auth_router = router


