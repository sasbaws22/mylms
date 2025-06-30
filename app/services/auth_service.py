from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
from fastapi import HTTPException, status,Request
import secrets
import string 
from sqlalchemy.orm import selectinload 
from app.utils.audit import audit_service

from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token,decode_url_safe_token, create_url_safe_token,verify_token
)
from app.core.config import settings
from app.models.models.user import User,UserRole
from app.schemas.auth import (
    LoginSchema, UserRegistrationSchema, TokenResponseSchema,
    ForgotPasswordSchema, ResetPasswordSchema, ChangePasswordSchema,
    UserResponseSchema, UserProfileSchema
)
from app.services.email_service import EmailService
from app.services.user_service import UserService


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService() # Instantiate the updated EmailService
        self.user_service = UserService(db)
    
    async def register_user(self, user_data: UserRegistrationSchema) -> UserResponseSchema:
        """Register a new user"""
        # Check if user already exists
        # existing_user = await self.db.exec(select(User).where(User.email == user_data.email))
        
        # if existing_user:
        #         raise HTTPException(
        #            status_code=status.HTTP_400_BAD_REQUEST,
        #             detail="Email already registered"
        #         )
    
               
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        # Send verification email
        await self._send_verification_email(new_user)
        
        return new_user
    
    async def login_user(self,login_data: LoginSchema,request:Request) -> TokenResponseSchema:
        """Authenticate user and return tokens"""
        # Find user by email
       # Get user by email
        result = await self.db.exec(select(User).where(User.email == login_data.email))
        user = result.first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

        if not user.is_active:
           raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        ) 
        
        # Update last login
        user.last_login = datetime.now()
        self.db.add(user)
        await self.db.commit()
        
        # Get user role and permissions
        result1 = await self.db.execute(select(User).where(User.role == user.role))
        role = result1.first()
        
        # Create token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        } 

        
        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub":str( user.id)}) 

        await  audit_service.log_login(
        db= self.db,
        user_id= user.id,
        ip_address=request.client.host if request.client else None,
        details={"email": user.email})
        
        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponseSchema:
        """Refresh access token using refresh token"""
        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        
        # Create new token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
        
        # Generate new tokens
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"sub": str( user.id)}) 

        
        
        return TokenResponseSchema(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def forgot_password(self, forgot_data: ForgotPasswordSchema) -> Dict[str, str]:
        """Send password reset email"""
        user = self.db.exec(
            select(User).where(User.email == forgot_data.email)
        ).first()
        
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Generate reset token
        reset_token = create_url_safe_token({"email": user.email})
        
        # Send reset email
        await self._send_password_reset_email(user, reset_token)
        
        return {"message": "If the email exists, a password reset link has been sent"}
    
    async def reset_password(self, reset_data: ResetPasswordSchema) -> Dict[str, str]:
        """Reset user password using reset token""" 
        token_data = decode_url_safe_token(reset_data.token)

        email = token_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user = self.db.exec(
            select(User).where(User.email == email)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = get_password_hash(reset_data.new_password)
        self.db.add(user)
        self.db.commit()
        
        return {"message": "Password reset successfully"}
    
    async def change_password(self, user_id: str, change_data: ChangePasswordSchema) -> Dict[str, str]:
        """Change user password"""
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(change_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = get_password_hash(change_data.new_password)
        self.db.add(user)
        self.db.commit()
        
        return {"message": "Password changed successfully"}
    
    async def verify_email(self, user_id: str, verification_code: str) -> Dict[str, str]:
        """Verify user email"""
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            return {"message": "Email already verified"}
        
        # In a real implementation, you would store and verify the verification code
        # For now, we'll just mark the user as verified
        user.is_verified = True
        self.db.add(user)
        self.db.commit()
        
        return {"message": "Email verified successfully"}
    
    async def get_current_user_profile(self, user_id: str) -> UserProfileSchema:
      """Get current user profile with detailed information"""
      users = await self.db.exec(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_points),
            selectinload(User.certificates),
            selectinload(User.user_badges),
        )
     )
      user = users.first()

      if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

      # Now safe to access these relationships
      total_points = len(user.user_points)
      total_certificates = len(user.certificates)
      total_badges = len(user.user_badges)
        
      return UserProfileSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone, 
            role_name= user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            avatar_url=user.avatar_url,
            total_points=total_points,
            total_certificates=total_certificates,
            total_badges=total_badges,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def _send_verification_email(self, user: User) -> None:
        """Send email verification email"""
        verification_token = create_url_safe_token({"user_id": str(user.id), "email": user.email})
        
        # Construct the verification link
        verification_link = f"{settings.BASE_URL}/verify-email?token={verification_token}"
        
        subject = f"Welcome to {settings.APP_NAME} - Verify Your Email"
        html_body = f"""
        <html>
        <body>
            <h2>Hello {user.first_name},</h2>
            <p>Welcome to {settings.APP_NAME}! Please verify your email address by clicking the link below:</p>
            <p><a href=\"{verification_link}\">Verify Email Address</a></p>
            <p>If you didn't create this account, please ignore this email.</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        await self.email_service.send_email(
            to_email=user.email,
            subject=subject,
            body="", # Pass empty body, as html_body is preferred
            html_body=html_body
        )    
    async def _send_password_reset_email(self, user: User, reset_token: str) -> None:
        """Send password reset email"""
        reset_link = f"{settings.BASE_URL}/reset-password?token={reset_token}"
        subject = f"{settings.APP_NAME} - Password Reset"
        html_body = f"""
        <html>
        <body>
            <h2>Hello {user.first_name},</h2>
            <p>You requested a password reset for your {settings.APP_NAME} account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href=\"{reset_link}\">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        await self.email_service.send_email(
            to_email=user.email,
            subject=subject,
            body="", # Pass empty body, as html_body is preferred
            html_body=html_body
        )


