"""
Webinar service for managing online events
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status,Depends,Request
from datetime import datetime

from app.models.models.webinar import Webinar, WebinarRegistration
from app.models.models.user import User
from app.schemas.webinar import (
    WebinarCreateSchema, WebinarUpdateSchema, WebinarSchema,
    WebinarRegistrationSchema
)
from app.schemas.base import PaginatedResponse 
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData 
from app.utils.audit import audit_service


class WebinarService:
    """Webinar management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_webinars(self, page: int = 1, limit: int = 20, search: Optional[str] = None, status_filter: Optional[str] = None) -> PaginatedResponse[WebinarSchema]:
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
        
        total = await self.db.exec(total_query)
        total = total.first()
        
        offset = (page - 1) * limit
        webinar = await self.db.exec(query.offset(offset).limit(limit))
        webinars = webinar.all()
        
        webinar_schemas = []
        for webinar in webinars:
            webinar_schemas.append(WebinarSchema.model_validate(webinar))
        
        return PaginatedResponse.create(webinar_schemas, total, page, limit)
    
    async def create_webinar(self,request:Request, webinar_data: WebinarCreateSchema,current_user:TokenData=Depends(access_token_bearer)) -> WebinarSchema:
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
        await self.db.commit()
        await self.db.refresh(new_webinar) 


        await  audit_service.log_create(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= new_webinar.__tablename__, 
        entity_id=new_webinar.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return WebinarSchema.model_validate(new_webinar)
    
    async def get_webinar_by_id(self, webinar_id: str) -> WebinarSchema:
        """Get webinar by ID"""
        webinarss= await self.db.exec(select(Webinar).where(Webinar.id == webinar_id))
        webinar = webinarss.first()
        
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        return WebinarSchema.model_validate(webinar)
    
    async def update_webinar(self, request:Request,webinar_id: str, webinar_data: WebinarUpdateSchema,current_user:TokenData=Depends(access_token_bearer)) -> WebinarSchema:
        """Update webinar information"""
        webinars = await self.db.exec(select(Webinar).where(Webinar.id == webinar_id))
        webinar = webinars.first()
        
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
        await self.db.commit()
        await self.db.refresh(webinar) 

        await  audit_service.log_update(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= webinar.__tablename__,
        entity_id= webinar.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return WebinarSchema.model_validate(webinar)
    
    async def delete_webinar(self, request:Request,webinar_id: str,current_user:TokenData=Depends(access_token_bearer)) -> Dict[str, str]:
        """Delete a webinar"""
        webinars = await self.db.exec(select(Webinar).where(Webinar.id == webinar_id))
        webinar = webinars.first()
        
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        self.db.delete(webinar)
        await self.db.commit() 

        await  audit_service.log_delete(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= webinar.__tablename__,
        entity_id= None,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return {"message": "Webinar deleted successfully"}
    
    async def register_for_webinar(self, webinar_id: str, user_id: str) -> WebinarRegistrationSchema:
        """Register a user for a webinar"""
        webinars = await self.db.exec(select(Webinar).where(Webinar.id == webinar_id))
        webinar = webinars.first()
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        users = await self.db.exec(select(User).where(User.id == user_id))
        user = users.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        existing_registrations = await self.db.exec(
            select(WebinarRegistration).where(
                (WebinarRegistration.webinar_id == webinar_id) &
                (WebinarRegistration.user_id == user_id)
            )
        )
        existing_registration = existing_registrations.first()
        
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
        await self.db.commit()
        await self.db.refresh(new_registration)
        
        return WebinarRegistrationSchema.model_validate(new_registration)
    
    async def get_webinar_registrations(self, webinar_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse[WebinarRegistrationSchema]:
        """Get paginated list of registrations for a webinar"""
        webinars = await self.db.exec(select(Webinar).where(Webinar.id == webinar_id))
        webinar = webinars.first()
        if not webinar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webinar not found"
            )
        
        query = select(WebinarRegistration).where(WebinarRegistration.webinar_id == webinar_id)
        tota = await self.db.exec(select(func.count(WebinarRegistration.id)).where(WebinarRegistration.webinar_id == webinar_id))
        total = tota.first()
        
        offset = (page - 1) * limit
        registration = await self.db.exec(query.offset(offset).limit(limit))
        registrations = registration.all()
        
        registration_schemas = []
        for reg in registrations:
            users = await self.db.exec(select(User).where(User.id == reg.user_id))
            user = users.first()
            registration_schemas.append(WebinarRegistrationSchema(
                id=reg.id,
                webinar_id=reg.webinar_id,
                user_id=reg.user_id,
                registered_at=reg.registered_at,
                user_name=user.full_name if user else "Unknown"
            ))
        
        return PaginatedResponse.create(registration_schemas, total, page, limit)
    
    async def unregister_from_webinar(self, webinar_id: str, user_id: str) -> Dict[str, str]:
        """Unregister a user from a webinar"""
        registrations = await self.db.exec(
            select(WebinarRegistration).where(
                (WebinarRegistration.webinar_id == webinar_id) &
                (WebinarRegistration.user_id == user_id)
            )
        )
        registration = registrations.first()
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not registered for this webinar"
            )
        
        self.db.delete(registration)
        await self.db.commit()
        
        return {"message": "Successfully unregistered from webinar"}


