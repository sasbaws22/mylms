from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status

from app.models.models.user import User
from app.schemas.user import (
    UserCreateSchema, UserUpdateSchema, UserDetailSchema,
    UserSummarySchema, UserListParams, UserStatsSchema
)
from app.schemas.base import PaginatedResponse
from app.core.security import get_password_hash

# Import related models for calculations
from app.models.models.course import Enrollment
from app.models.models.quiz import QuizAttempt
from app.models.models.certificate import Certificate,UserBadge 



class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users(self, params: UserListParams, page: int = 1, limit: int = 20) -> Any:
        """Get paginated list of users"""
        query = select(User)
        
        # Apply filters
        if params.is_active is not None:
            query = query.where(User.is_active == params.is_active)
        
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.email.ilike(search_term)) |
                (User.username.ilike(search_term))
            )
        
        # Apply sorting
        if params.sort_by == "name":
            if params.sort_order == "desc":
                query = query.order_by(User.first_name.desc(), User.last_name.desc())
            else:
                query = query.order_by(User.first_name.asc(), User.last_name.asc())
        elif params.sort_by == "email":
            if params.sort_order == "desc":
                query = query.order_by(User.email.desc())
            else:
                query = query.order_by(User.email.asc())
        else:  # Default to created_at
            if params.sort_order == "desc":
                query = query.order_by(User.created_at.desc())
            else:
                query = query.order_by(User.created_at.asc())
        
        # Get total count
        total_query = select(func.count(User.id))
        if params.is_active is not None:
            total_query = total_query.where(User.is_active == params.is_active)
        if params.search:
            search_term = f"%{params.search}%"
            total_query = total_query.where(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.email.ilike(search_term)) |
                (User.username.ilike(search_term))
            )
        
        result = await self.db.exec(total_query) 
        total = result
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result =  await self.db.exec(query) 
        users = result.all()
        
        
        
        return users
    
    async def get_user_by_id(self, user_id: str) -> UserDetailSchema:
        """Get user by ID with detailed information"""
        result5 = self.db.exec(select(User).where(User.id == user_id))
        user = result5
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Calculate user statistics
        total_enrollments = self.db.exec(select(func.count(Enrollment.id)).where(Enrollment.user_id == user.id)).first() or 0
        completed_courses = self.db.exec(select(func.count(Enrollment.id)).where(Enrollment.user_id == user.id, Enrollment.status == "completed")).first() or 0
        # Assuming total_points are calculated from quiz attempts or other activities
        total_points = self.db.exec(select(func.sum(QuizAttempt.score)).where(QuizAttempt.user_id == user.id)).first() or 0
        total_certificates = self.db.exec(select(func.count(Certificate.id)).where(Certificate.user_id == user.id)).first() or 0
        total_badges = self.db.exec(select(func.count(UserBadge.id)).where(UserBadge.user_id == user.id)).first() or 0
        
        return UserDetailSchema(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            avatar_url=user.avatar_url,
            total_enrollments=total_enrollments,
            completed_courses=completed_courses,
            total_points=total_points,
            total_certificates=total_certificates,
            total_badges=total_badges,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def create_user(self, user_data: UserCreateSchema) -> UserDetailSchema:
        """Create a new user (admin function)"""
        # Check if user already exists
        existing_user = self.db.exec(
            select(User).where(
                (User.email == user_data.email) | (User.username == user_data.username)
            )
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Generate password if not provided
        password = user_data.password 
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone_number, # Corrected to use 'phone' attribute
            is_active=user_data.is_active
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return self.get_user_by_id(str(new_user.id))
    
    def update_user(self, user_id: str, user_data: UserUpdateSchema) -> UserDetailSchema:
        """Update user information"""
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
        if user_data.phone_number is not None:
            user.phone = user_data.phone_number # Corrected to use 'phone' attribute
        if user_data.bio is not None:
            user.bio = user_data.bio
        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return self.get_user_by_id(str(user.id))
    
    def deactivate_user(self, user_id: str) -> Dict[str, str]:
        """Deactivate user account"""
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        self.db.add(user)
        self.db.commit()
        
        return {"message": "User deactivated successfully"}
    
    async def get_user_stats(self) -> Any:
        """Get user statistics"""
        results1 = await self.db.exec(select(func.count(User.id)))
        total_users = results1.first()
        results2 = await  self.db.exec(select(func.count(User.id)).where(User.is_active == True))
        active_users = results2.first()
        
        # Users created this month
        from datetime import datetime, timedelta
        this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        results3 = await  self.db.exec(
            select(func.count(User.id)).where(User.created_at >= this_month)
        )
        new_users_this_month = results3.first()
        # Assuming UserRole is an Enum or similar, and User has a 'role' attribute
        # You might need to adjust this based on your actual User and UserRole models
        results4 = self.db.exec(
            select(User.role, func.count(User.id))
            .group_by(User.role)
        )
        users_by_role_data = results4
       

        
        return UserStatsSchema(
            total_users=total_users or 0,
            active_users=active_users or 0,
            new_users_this_month=new_users_this_month or 0
        )


