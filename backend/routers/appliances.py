"""
Appliances Router
Handles appliance management and detection
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import User, Appliance, EnergyData
from schemas import ApplianceCreate, ApplianceUpdate, ApplianceResponse
from utils.auth import get_current_active_user
from ai.appliance_detection import detector

router = APIRouter(prefix="/api/appliances", tags=["Appliances"])


@router.post("/", response_model=ApplianceResponse, status_code=status.HTTP_201_CREATED)
def create_appliance(
    appliance: ApplianceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new appliance"""
    new_appliance = Appliance(
        user_id=current_user.id,
        name=appliance.name,
        type=appliance.type,
        power_rating=appliance.power_rating,
        avg_daily_usage=appliance.avg_daily_usage
    )
    
    # Calculate monthly energy and cost
    if new_appliance.power_rating and new_appliance.avg_daily_usage:
        new_appliance.monthly_energy = (new_appliance.power_rating * new_appliance.avg_daily_usage * 30) / 1000
        new_appliance.monthly_cost = new_appliance.monthly_energy * 6.0  # Default rate
    
    db.add(new_appliance)
    db.commit()
    db.refresh(new_appliance)
    
    return new_appliance


@router.get("/", response_model=List[ApplianceResponse])
def get_appliances(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all appliances for the current user"""
    appliances = db.query(Appliance).filter(
        Appliance.user_id == current_user.id
    ).all()
    
    return appliances


@router.get("/{appliance_id}", response_model=ApplianceResponse)
def get_appliance(
    appliance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific appliance"""
    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id,
        Appliance.user_id == current_user.id
    ).first()
    
    if not appliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appliance not found"
        )
    
    return appliance


@router.put("/{appliance_id}", response_model=ApplianceResponse)
def update_appliance(
    appliance_id: int,
    appliance_update: ApplianceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an appliance"""
    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id,
        Appliance.user_id == current_user.id
    ).first()
    
    if not appliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appliance not found"
        )
    
    if appliance_update.name is not None:
        appliance.name = appliance_update.name
    if appliance_update.type is not None:
        appliance.type = appliance_update.type
    if appliance_update.power_rating is not None:
        appliance.power_rating = appliance_update.power_rating
    if appliance_update.avg_daily_usage is not None:
        appliance.avg_daily_usage = appliance_update.avg_daily_usage
    
    # Recalculate monthly energy and cost
    if appliance.power_rating and appliance.avg_daily_usage:
        appliance.monthly_energy = (appliance.power_rating * appliance.avg_daily_usage * 30) / 1000
        appliance.monthly_cost = appliance.monthly_energy * 6.0
    
    appliance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appliance)
    
    return appliance


@router.delete("/{appliance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appliance(
    appliance_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an appliance"""
    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id,
        Appliance.user_id == current_user.id
    ).first()
    
    if not appliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appliance not found"
        )
    
    db.delete(appliance)
    db.commit()
    
    return None


@router.post("/detect", response_model=List[dict])
def detect_appliances(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Detect appliances from energy data using AI"""
    # Get recent energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(100).all()
    
    if not energy_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient energy data for detection"
        )
    
    # Extract power readings
    power_readings = [e.power for e in energy_data if e.power is not None]
    
    if not power_readings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No power readings available"
        )
    
    # Detect appliances
    detected = detector.analyze_total_consumption(power_readings)
    
    return detected
