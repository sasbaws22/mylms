
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List

from app.db.database import get_session
from app.services.certificate_service import CertificateService
from app.schemas.certificate import (
    CertificateCreateSchema, CertificateUpdateSchema, CertificateSchema,
    PaginatedCertificatesResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/", response_model=PaginatedCertificatesResponse)
async def get_certificates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of certificates"""
    certificate_service = CertificateService(db)
    return await certificate_service.get_certificates(page, limit, user_id, course_id)


@router.post("/", response_model=CertificateSchema, status_code=status.HTTP_201_CREATED)
async def create_certificate(
    certificate_data: CertificateCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new certificate"""
    certificate_service = CertificateService(db)
    return await certificate_service.create_certificate(certificate_data)


@router.get("/{certificate_id}", response_model=CertificateSchema)
async def get_certificate_by_id(
    certificate_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get certificate by ID"""
    certificate_service = CertificateService(db)
    return await certificate_service.get_certificate_by_id(certificate_id)


@router.put("/{certificate_id}", response_model=CertificateSchema)
async def update_certificate(
    certificate_id: str,
    certificate_data: CertificateUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update certificate information"""
    certificate_service = CertificateService(db)
    return await certificate_service.update_certificate(certificate_id, certificate_data)


@router.delete("/{certificate_id}", response_model=MessageResponse)
async def delete_certificate(
    certificate_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a certificate"""
    certificate_service = CertificateService(db)
    result = await certificate_service.delete_certificate(certificate_id)
    return MessageResponse(message=result["message"])


@router.get("/users/{user_id}", response_model=PaginatedCertificatesResponse)
async def get_certificates_by_user(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of certificates for a specific user"""
    certificate_service = CertificateService(db)
    return await certificate_service.get_certificates(page, limit, user_id=user_id)


@router.get("/courses/{course_id}", response_model=PaginatedCertificatesResponse)
async def get_certificates_by_course(
    course_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of certificates for a specific course"""
    certificate_service = CertificateService(db) 
    id = current_user.get("sub")
    return await certificate_service.get_certificates(page, limit, course_id=course_id)


# Create router instance for export
certificates_router = router


