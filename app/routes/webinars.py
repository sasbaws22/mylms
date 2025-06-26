
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List
from datetime import datetime

from app.db.database import get_session
from app.services.webinar_service import WebinarService
from app.schemas.webinar import (
    WebinarCreateSchema, WebinarUpdateSchema, WebinarSchema,
    WebinarRegistrationSchema, PaginatedWebinarsResponse,
    PaginatedWebinarRegistrationsResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/", response_model=PaginatedWebinarsResponse)
async def get_webinars(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of webinars"""
    webinar_service = WebinarService(db)
    return await webinar_service.get_webinars(page, limit, search, status)


@router.post("/", response_model=WebinarSchema, status_code=status.HTTP_201_CREATED)
async def create_webinar(
    webinar_data: WebinarCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new webinar"""
    webinar_service = WebinarService(db)
    return await webinar_service.create_webinar(webinar_data)


@router.get("/{webinar_id}", response_model=WebinarSchema)
async def get_webinar_by_id(
    webinar_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get webinar by ID"""
    webinar_service = WebinarService(db)
    return await webinar_service.get_webinar_by_id(webinar_id)


@router.put("/{webinar_id}", response_model=WebinarSchema)
async def update_webinar(
    webinar_id: str,
    webinar_data: WebinarUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update webinar information"""
    webinar_service = WebinarService(db)
    return await webinar_service.update_webinar(webinar_id, webinar_data)


@router.delete("/{webinar_id}", response_model=MessageResponse)
async def delete_webinar(
    webinar_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a webinar"""
    webinar_service = WebinarService(db)
    result =await  webinar_service.delete_webinar(webinar_id)
    return MessageResponse(message=result["message"])


@router.post("/{webinar_id}/register", response_model=WebinarRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_for_webinar(
    webinar_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Register current user for a webinar"""
    webinar_service = WebinarService(db) 
    id = current_user.get("sub")
    return await  webinar_service.register_for_webinar(webinar_id, id)


@router.get("/{webinar_id}/registrations", response_model=PaginatedWebinarRegistrationsResponse)
async def get_webinar_registrations(
    webinar_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of registrations for a webinar"""
    webinar_service = WebinarService(db)
    return await webinar_service.get_webinar_registrations(webinar_id, page, limit)


@router.delete("/{webinar_id}/unregister", response_model=MessageResponse)
async def unregister_from_webinar(
    webinar_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Unregister current user from a webinar"""
    webinar_service = WebinarService(db) 
    id = current_user.get("sub")
    result = await webinar_service.unregister_from_webinar(webinar_id, id )
    return MessageResponse(message=result["message"])


# Create router instance for export
webinars_router = router


