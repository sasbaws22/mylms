"""
Webinar service for managing online events
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from datetime import datetime

from app.models.models.webinar import Webinar, WebinarRegistration
from app.models.models.user import User
from app.schemas.webinar import (
    WebinarCreateSchema, WebinarUpdateSchema, WebinarSchema,
    WebinarRegistrationSchema
)
from app.schemas.base import PaginatedResponse


class WebinarService:
    """Webinar management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_webinars(self, page: int = 1, limit: int = 20, search: Optional[str] = None, status_filter: Optional[str] = None) -> PaginatedResponse[WebinarSchema]:
        """Get paginated list of webinars"""
        query = select(Webinar)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Webinar.title.ilike(search_term)) |
                (Webinar.description.ilike(search_term))
            )
        
        if status_filter:
            query = query.where(Webinar.status == status_filter)
        
        total_query = select(func.count(Webinar.id))
        if search:
            search_term = f"%{search}%"
            total_query = total_query.where(
                (Webinar.title.ilike(search_term)) |
                (Webinar.description.ilike(search_term))
            )
        if status_filter:
            total_query = total_query.where(Webinar.status == status_filter)
        
        total = self.db.exec(total_query).first()
        
        offset = (page - 1) * limit
        webinars = self.db.exec(query.offset(offset).limit(limit)).all()
        
        webinar_schemas = []
        for webinar in webinars:
            webinar_schemas.append(WebinarSchema.model_validate(webinar))
        
        return PaginatedResponse.create(webinar_schemas, total, page, limit)
    
    def create_webinar(self, webinar_data: WebinarCreateSchema) -> WebinarSchema:
        """Create a new webinar"""
        new_webinar = Webinar(
            title=webinar_data.title,
            description=webinar_data.description,
            scheduled_at=webinar_data.scheduled_at,
            duration=webinar_data.duration,
            join_url=webinar_data.join_url,
            status=webinar_data.status,
            organizer_id=webinar_data.organizer_id
        )
        
        self.db.add(new_webinar)
        self.db.commit()
        self.db.refresh(new_webinar)
        
        return WebinarSchema.model_validate(new_webinar)
    
    def get_webinar_by_id(self, webinar_id: str) -> WebinarSchema:
        """Get webinar by ID"""
        webinar = self.db.exec(select(Webinar).where(Webinar.id == webinar_id)).first()
        
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        return WebinarSchema.model_validate(webinar)
    
    def update_webinar(self, webinar_id: str, webinar_data: WebinarUpdateSchema) -> WebinarSchema:
        """Update webinar information"""
        webinar = self.db.exec(select(Webinar).where(Webinar.id == webinar_id)).first()
        
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        if webinar_data.title is not None:
            webinar.title = webinar_data.title
        if webinar_data.description is not None:
            webinar.description = webinar_data.description
        if webinar_data.scheduled_at is not None:
            webinar.scheduled_at = webinar_data.scheduled_at
        if webinar_data.duration is not None:
            webinar.duration = webinar_data.duration
        if webinar_data.join_url is not None:
            webinar.join_url = webinar_data.join_url
        if webinar_data.status is not None:
            webinar.status = webinar_data.status
        if webinar_data.organizer_id is not None:
            webinar.organizer_id = webinar_data.organizer_id
        
        self.db.add(webinar)
        self.db.commit()
        self.db.refresh(webinar)
        
        return WebinarSchema.model_validate(webinar)
    
    def delete_webinar(self, webinar_id: str) -> Dict[str, str]:
        """Delete a webinar"""
        webinar = self.db.exec(select(Webinar).where(Webinar.id == webinar_id)).first()
        
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        self.db.delete(webinar)
        self.db.commit()
        
        return {"message": "Webinar deleted successfully"}
    
    def register_for_webinar(self, webinar_id: str, user_id: str) -> WebinarRegistrationSchema:
        """Register a user for a webinar"""
        webinar = self.db.exec(select(Webinar).where(Webinar.id == webinar_id)).first()
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        existing_registration = self.db.exec(
            select(WebinarRegistration).where(
                (WebinarRegistration.webinar_id == webinar_id) &
                (WebinarRegistration.user_id == user_id)
            )
        ).first()
        
        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered for this webinar"
            )
        
        new_registration = WebinarRegistration(
            webinar_id=webinar_id,
            user_id=user_id,
            registered_at=datetime.utcnow()
        )
        
        self.db.add(new_registration)
        self.db.commit()
        self.db.refresh(new_registration)
        
        return WebinarRegistrationSchema.model_validate(new_registration)
    
    def get_webinar_registrations(self, webinar_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse[WebinarRegistrationSchema]:
        """Get paginated list of registrations for a webinar"""
        webinar = self.db.exec(select(Webinar).where(Webinar.id == webinar_id)).first()
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        query = select(WebinarRegistration).where(WebinarRegistration.webinar_id == webinar_id)
        total = self.db.exec(select(func.count(WebinarRegistration.id)).where(WebinarRegistration.webinar_id == webinar_id)).first()
        
        offset = (page - 1) * limit
        registrations = self.db.exec(query.offset(offset).limit(limit)).all()
        
        registration_schemas = []
        for reg in registrations:
            user = self.db.exec(select(User).where(User.id == reg.user_id)).first()
            registration_schemas.append(WebinarRegistrationSchema(
                id=reg.id,
                webinar_id=reg.webinar_id,
                user_id=reg.user_id,
                registered_at=reg.registered_at,
                user_name=user.full_name if user else "Unknown"
            ))
        
        return PaginatedResponse.create(registration_schemas, total, page, limit)
    
    def unregister_from_webinar(self, webinar_id: str, user_id: str) -> Dict[str, str]:
        """Unregister a user from a webinar"""
        registration = self.db.exec(
            select(WebinarRegistration).where(
                (WebinarRegistration.webinar_id == webinar_id) &
                (WebinarRegistration.user_id == user_id)
            )
        ).first()
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not registered for this webinar"
            )
        
        self.db.delete(registration)
        self.db.commit()
        
        return {"message": "Successfully unregistered from webinar"}


