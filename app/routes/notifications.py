
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.models.notification import Notification, NotificationPreferences
from app.schemas.notification import NotificationCreate, NotificationMarkReadSchema, NotificationPreferencesUpdateSchema
from app.core.security import get_current_user
from app.models.models.user import User

notifications_router = APIRouter()

@notifications_router.post(
    "/", 
    response_model=NotificationMarkReadSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new notification (Admin/Internal)"
)
async def create_notification(
    notification: NotificationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # This route might be for internal system use or admin to send notifications
    # Add proper authorization check if only admins can create notifications
    db_notification = Notification.model_validate(notification)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification

@notifications_router.get(
    "/me", 
    response_model=List[NotificationMarkReadSchema],
    summary="Get all notifications for the current user"
)
async def get_user_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    notifications = session.query(Notification).filter(Notification.user_id == current_user.id).all()
    return notifications

@notifications_router.get(
    "/{notification_id}", 
    response_model=NotificationMarkReadSchema,
    summary="Get a specific notification by ID"
)
async def get_notification_by_id(
    notification_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    notification = session.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification

# @notifications_router.put(
#     "/{notification_id}", 
#     response_model=NotificationMarkReadSchema,
#     summary="Update a notification (e.g., mark as read)"
# )
# async def update_notification(
#     notification_id: UUID,
#     notification_update: NotificationUpdate,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     notification = session.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
#     if not notification:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
#     notification.sqlmodel_update(notification_update.model_dump(exclude_unset=True))
#     session.add(notification)
#     session.commit()
#     session.refresh(notification)
#     return notification

@notifications_router.delete(
    "/{notification_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notification"
)
async def delete_notification(
    notification_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    notification = session.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    session.delete(notification)
    session.commit()
    return

# Notification Preferences Routes

# @notifications_router.get(
#     "/preferences/me", 
#     response_model=NotificationPreferenceRead,
#     summary="Get current user's notification preferences"
# )
# async def get_my_notification_preferences(
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     preferences = session.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).first()
#     if not preferences:
#         # Create default preferences if none exist
#         preferences = NotificationPreferences(user_id=current_user.id)
#         session.add(preferences)
#         session.commit()
#         session.refresh(preferences)
#     return preferences

# @notifications_router.put(
#     "/preferences/me", 
#     response_model=NotificationPreferenceRead,
#     summary="Update current user's notification preferences"
# )
# async def update_my_notification_preferences(
#     preference_update: NotificationPreferencesUpdateSchema,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     preferences = session.query(NotificationPreferences).filter(NotificationPreferences.user_id == current_user.id).first()
#     if not preferences:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification preferences not found")
    
#     preferences.sqlmodel_update(preference_update.model_dump(exclude_unset=True))
#     session.add(preferences)
#     session.commit()
#     session.refresh(preferences)
#     return preferences

__all__ = ["notifications_router"]


