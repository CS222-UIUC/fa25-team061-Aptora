"""
Notifications Router

API endpoints for managing notification settings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import User
from ..auth.dependencies import get_current_active_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationSettings(BaseModel):
    reminders_enabled: bool
    reminder_lead_minutes: int

    class Config:
        from_attributes = True


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's notification settings.
    
    Args:
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        The user's notification settings
    """
    # Refresh user from database to get latest settings
    db.refresh(current_user)
    
    return NotificationSettings(
        reminders_enabled=current_user.reminders_enabled if current_user.reminders_enabled is not None else True,
        reminder_lead_minutes=current_user.reminder_lead_minutes if current_user.reminder_lead_minutes is not None else 30
    )


@router.put("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's notification settings.
    
    Args:
        settings: The new notification settings
        current_user: The current authenticated user
        db: Database session
        
    Returns:
        The updated notification settings
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate reminder_lead_minutes
    if settings.reminder_lead_minutes < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reminder lead time must be a positive number"
        )
    
    # Update user settings
    current_user.reminders_enabled = settings.reminders_enabled
    current_user.reminder_lead_minutes = settings.reminder_lead_minutes
    
    db.commit()
    db.refresh(current_user)
    
    return NotificationSettings(
        reminders_enabled=current_user.reminders_enabled,
        reminder_lead_minutes=current_user.reminder_lead_minutes
    )

