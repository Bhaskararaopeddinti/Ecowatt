"""
Alerts Router
Handles energy leak and anomaly alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import User, Alert, EnergyData
from schemas import AlertCreate, AlertResponse
from utils.auth import get_current_active_user
from ai.energy_leak_detection import leak_detector

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    new_alert = Alert(
        user_id=current_user.id,
        type=alert.type,
        severity=alert.severity,
        message=alert.message,
        appliance=alert.appliance,
        value=alert.value,
        threshold=alert.threshold
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return new_alert


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 50,
    unresolved_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alerts for the current user"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if unresolved_only:
        query = query.filter(Alert.is_resolved == False)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None


@router.post("/detect", response_model=List[dict])
def detect_energy_leaks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Detect energy leaks from energy data using AI"""
    # Get recent energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(200).all()
    
    if not energy_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient energy data for leak detection"
        )
    
    # Extract power readings
    power_readings = [e.power for e in energy_data if e.power is not None]
    
    if not power_readings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No power readings available"
        )
    
    # Detect leaks
    leaks = leak_detector.analyze_all_leaks(power_readings)
    
    # Create alerts for detected leaks
    for leak in leaks:
        existing_alert = db.query(Alert).filter(
            Alert.user_id == current_user.id,
            Alert.type == leak['leak_type'],
            Alert.is_resolved == False
        ).first()
        
        if not existing_alert:
            new_alert = Alert(
                user_id=current_user.id,
                type=leak['leak_type'],
                severity=leak['severity'],
                message=leak['message'],
                appliance=leak.get('appliance'),
                value=leak.get('value'),
                threshold=leak.get('threshold')
            )
            db.add(new_alert)
    
    db.commit()
    
    return leaks
