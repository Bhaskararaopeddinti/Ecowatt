"""
Settings Router
Handles user settings and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User, Settings
from schemas import SettingsCreate, SettingsUpdate, SettingsResponse
from utils.auth import get_current_active_user

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.post("/", response_model=SettingsResponse, status_code=status.HTTP_201_CREATED)
def create_settings(
    settings: SettingsCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create settings for the current user"""
    # Check if settings already exist
    existing_settings = db.query(Settings).filter(
        Settings.user_id == current_user.id
    ).first()
    
    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settings already exist. Use PUT to update."
        )
    
    new_settings = Settings(
        user_id=current_user.id,
        electricity_rate=settings.electricity_rate,
        currency=settings.currency,
        theme=settings.theme,
        notifications_enabled=settings.notifications_enabled,
        email_alerts=settings.email_alerts,
        sms_alerts=settings.sms_alerts,
        carbon_factor=settings.carbon_factor
    )
    
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    
    return new_settings


@router.get("/", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get settings for the current user"""
    settings = db.query(Settings).filter(
        Settings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        new_settings = Settings(user_id=current_user.id)
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
        return new_settings
    
    return settings


@router.put("/", response_model=SettingsResponse)
def update_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update settings for the current user"""
    settings = db.query(Settings).filter(
        Settings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create settings if they don't exist
        new_settings = Settings(
            user_id=current_user.id,
            electricity_rate=settings_update.electricity_rate if settings_update.electricity_rate is not None else 6.0,
            currency=settings_update.currency if settings_update.currency is not None else "₹",
            theme=settings_update.theme if settings_update.theme is not None else "light",
            notifications_enabled=settings_update.notifications_enabled if settings_update.notifications_enabled is not None else True,
            email_alerts=settings_update.email_alerts if settings_update.email_alerts is not None else False,
            sms_alerts=settings_update.sms_alerts if settings_update.sms_alerts is not None else False,
            carbon_factor=settings_update.carbon_factor if settings_update.carbon_factor is not None else 0.85
        )
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
        return new_settings
    
    if settings_update.electricity_rate is not None:
        settings.electricity_rate = settings_update.electricity_rate
    if settings_update.currency is not None:
        settings.currency = settings_update.currency
    if settings_update.theme is not None:
        settings.theme = settings_update.theme
    if settings_update.notifications_enabled is not None:
        settings.notifications_enabled = settings_update.notifications_enabled
    if settings_update.email_alerts is not None:
        settings.email_alerts = settings_update.email_alerts
    if settings_update.sms_alerts is not None:
        settings.sms_alerts = settings_update.sms_alerts
    if settings_update.carbon_factor is not None:
        settings.carbon_factor = settings_update.carbon_factor
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return settings
