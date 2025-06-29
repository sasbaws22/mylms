"""
Certificate service for managing certificates and gamification
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status,Request,Depends
from datetime import datetime
import uuid

from app.models.models.certificate import Certificate, CertificateType
from app.models.models.user import User
from app.models.models.course import Course
from app.schemas.certificate import (
    CertificateCreateSchema, CertificateUpdateSchema, CertificateSchema
)
from app.utils.audit import audit_service
from app.schemas.base import PaginatedResponse 
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData


class CertificateService:
    """Certificate management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_certificates(self, page: int = 1, limit: int = 20, user_id: Optional[str] = None, course_id: Optional[str] = None) -> PaginatedResponse[CertificateSchema]:
        """Get paginated list of certificates"""
        query = select(Certificate)
        
        if user_id:
            query = query.where(Certificate.user_id == user_id)
        
        if course_id:
            query = query.where(Certificate.course_id == course_id)
        
        total_query = select(func.count(Certificate.id))
        if user_id:
            total_query = total_query.where(Certificate.user_id == user_id)
        if course_id:
            total_query = total_query.where(Certificate.course_id == course_id)
        
        tota = await self.db.exec(total_query)
        total = tota.first()
        
        offset = (page - 1) * limit
        certificate = await self.db.exec(query.offset(offset).limit(limit))
        certificates = certificate.all()
        
        certificate_schemas = []
        for cert in certificates:
            users = await self.db.exec(select(User).where(User.id == cert.user_id))
            user = users.first()
            course = await  self.db.exec(select(Course).where(Course.id == cert.course_id))
            course = course.first()
            certificate_schemas.append(CertificateSchema(
                id=cert.id,
                user_id=cert.user_id,
                course_id=cert.course_id,
                certificate_type=cert.certificate_type,
                issued_at=cert.issued_at,
                expires_at=cert.expires_at,
                certificate_url=cert.certificate_url,
                verification_code=cert.verification_code,
                is_valid=cert.is_valid,
                user_name=user.full_name if user else "Unknown",
                course_title=course.title if course else "N/A",
                created_at=cert.created_at,
                updated_at=cert.updated_at
            ))
        
        return PaginatedResponse.create(certificate_schemas, total, page, limit)
    
    async def create_certificate(self,request:Request, certificate_data: CertificateCreateSchema) -> CertificateSchema:
        """Create a new certificate"""
        users = await self.db.exec(select(User).where(User.id == certificate_data.user_id))
        user = users.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        course = None
        if certificate_data.course_id:
            courses = await self.db.exec(select(Course).where(Course.id == certificate_data.course_id))
            course = courses.first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found"
                )
        
        new_certificate = Certificate(
            user_id=certificate_data.user_id,
            course_id=certificate_data.course_id,
            certificate_type=certificate_data.certificate_type,
            issued_at=certificate_data.issued_at or datetime.utcnow(),
            expires_at=certificate_data.expires_at,
            certificate_url=certificate_data.certificate_url,
            verification_code=str(uuid.uuid4()), # Generate unique verification code
            is_valid=True
        )
        
        self.db.add(new_certificate)
        await self.db.commit()
        await self.db.refresh(new_certificate) 

        await  audit_service.log_create(
        db= self.db,
        user_id= user.id, 
        entity_type= new_certificate.__tablename__,
        entity_id=new_certificate.id,
        ip_address=request.client.host if request.client else None,
        details={"firstname": user.first_name})
        
        return CertificateSchema(
            id=new_certificate.id,
            user_id=new_certificate.user_id,
            course_id=new_certificate.course_id,
            certificate_type=new_certificate.certificate_type,
            issued_at=new_certificate.issued_at,
            expires_at=new_certificate.expires_at,
            certificate_url=new_certificate.certificate_url,
            verification_code=new_certificate.verification_code,
            is_valid=new_certificate.is_valid,
            user_name=user.first_name,
            course_title=course.title if course else "N/A",
            created_at=new_certificate.created_at,
            updated_at=new_certificate.updated_at
        )
    
    async def get_certificate_by_id(self, certificate_id: str) -> CertificateSchema:
        """Get certificate by ID"""
        certificates = await self.db.exec(select(Certificate).where(Certificate.id == certificate_id))
        certificate = certificates.first()
        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        users = await  self.db.exec(select(User).where(User.id == certificate.user_id))
        user = users.first()
        courses = await self.db.exec(select(Course).where(Course.id == certificate.course_id))
        course = courses.first()
        
        return CertificateSchema(
            id=certificate.id,
            user_id=certificate.user_id,
            course_id=certificate.course_id,
            certificate_type=certificate.certificate_type,
            issued_at=certificate.issued_at,
            expires_at=certificate.expires_at,
            certificate_url=certificate.certificate_url,
            verification_code=certificate.verification_code,
            is_valid=certificate.is_valid,
            user_name=user.full_name if user else "Unknown",
            course_title=course.title if course else "N/A",
            created_at=certificate.created_at,
            updated_at=certificate.updated_at
        )
    
    async def update_certificate(self, certificate_id: str, certificate_data: CertificateUpdateSchema, request:Request,current_user :TokenData = Depends(access_token_bearer)) -> CertificateSchema:
        """Update certificate information"""
        certificates = await self.db.exec(select(Certificate).where(Certificate.id == certificate_id))
        certificate = certificates.first()  


        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        if certificate_data.certificate_type is not None:
            certificate.certificate_type = certificate_data.certificate_type
        if certificate_data.issued_at is not None:
            certificate.issued_at = certificate_data.issued_at
        if certificate_data.expires_at is not None:
            certificate.expires_at = certificate_data.expires_at
        if certificate_data.certificate_url is not None:
            certificate.certificate_url = certificate_data.certificate_url
        if certificate_data.is_valid is not None:
            certificate.is_valid = certificate_data.is_valid
        
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)  

        await  audit_service.log_create(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= certificate.__tablename__,
        entity_id=certificate.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
       
        
        return await self.get_certificate_by_id(certificate.id)
    
    async def delete_certificate(self, certificate_id: str,request:Request,current_user:TokenData=Depends(access_token_bearer)) -> Dict[str, str]:
        """Delete a certificate"""
        certificates = await self.db.exec(select(Certificate).where(Certificate.id == certificate_id))
        certificate = certificates.first()
        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        self.db.delete(certificate)
        await self.db.commit() 

        await  audit_service.log_delete(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= certificate.__tablename__,
        entity_id=None,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return {"message": "Certificate deleted successfully"}


