"""
Certificate service for managing certificates and gamification
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from datetime import datetime
import uuid

from app.models.models.certificate import Certificate, CertificateType
from app.models.models.user import User
from app.models.models.course import Course
from app.schemas.certificate import (
    CertificateCreateSchema, CertificateUpdateSchema, CertificateSchema
)
from app.schemas.base import PaginatedResponse


class CertificateService:
    """Certificate management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_certificates(self, page: int = 1, limit: int = 20, user_id: Optional[str] = None, course_id: Optional[str] = None) -> PaginatedResponse[CertificateSchema]:
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
        
        total = self.db.exec(total_query).first()
        
        offset = (page - 1) * limit
        certificates = self.db.exec(query.offset(offset).limit(limit)).all()
        
        certificate_schemas = []
        for cert in certificates:
            user = self.db.exec(select(User).where(User.id == cert.user_id)).first()
            course = self.db.exec(select(Course).where(Course.id == cert.course_id)).first()
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
    
    def create_certificate(self, certificate_data: CertificateCreateSchema) -> CertificateSchema:
        """Create a new certificate"""
        user = self.db.exec(select(User).where(User.id == certificate_data.user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        course = None
        if certificate_data.course_id:
            course = self.db.exec(select(Course).where(Course.id == certificate_data.course_id)).first()
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
        self.db.commit()
        self.db.refresh(new_certificate)
        
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
            user_name=user.full_name,
            course_title=course.title if course else "N/A",
            created_at=new_certificate.created_at,
            updated_at=new_certificate.updated_at
        )
    
    def get_certificate_by_id(self, certificate_id: str) -> CertificateSchema:
        """Get certificate by ID"""
        certificate = self.db.exec(select(Certificate).where(Certificate.id == certificate_id)).first()
        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        user = self.db.exec(select(User).where(User.id == certificate.user_id)).first()
        course = self.db.exec(select(Course).where(Course.id == certificate.course_id)).first()
        
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
    
    def update_certificate(self, certificate_id: str, certificate_data: CertificateUpdateSchema) -> CertificateSchema:
        """Update certificate information"""
        certificate = self.db.exec(select(Certificate).where(Certificate.id == certificate_id)).first()
        
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
        self.db.commit()
        self.db.refresh(certificate)
        
        return self.get_certificate_by_id(certificate.id)
    
    def delete_certificate(self, certificate_id: str) -> Dict[str, str]:
        """Delete a certificate"""
        certificate = self.db.exec(select(Certificate).where(Certificate.id == certificate_id)).first()
        
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        self.db.delete(certificate)
        self.db.commit()
        
        return {"message": "Certificate deleted successfully"}


