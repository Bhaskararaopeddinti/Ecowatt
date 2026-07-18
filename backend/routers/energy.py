"""
Energy Data Router
Handles smart meter data operations
"""

import os
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from database import get_db
from models import User, EnergyData
from schemas import EnergyDataCreate, EnergyDataResponse
from utils.auth import get_current_active_user
from services.smart_meter_simulator import smart_meter_simulator

router = APIRouter(prefix="/api/energy", tags=["Energy Data"])


@router.post("/data", response_model=EnergyDataResponse, status_code=status.HTTP_201_CREATED)
def create_energy_data(
    energy_data: EnergyDataCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new energy data entry"""
    new_energy_data = EnergyData(
        user_id=current_user.id,
        timestamp=energy_data.timestamp or datetime.utcnow(),
        voltage=energy_data.voltage,
        current=energy_data.current,
        power=energy_data.power,
        energy=energy_data.energy,
        frequency=energy_data.frequency,
        power_factor=energy_data.power_factor
    )
    
    db.add(new_energy_data)
    db.commit()
    db.refresh(new_energy_data)
    
    return new_energy_data


@router.get("/data", response_model=List[EnergyDataResponse])
def get_energy_data(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get energy data for the current user"""
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).offset(skip).limit(limit).all()
    
    return energy_data


@router.get("/data/recent", response_model=List[EnergyDataResponse])
def get_recent_energy_data(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent energy data within specified hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id,
        EnergyData.timestamp >= cutoff_time
    ).order_by(EnergyData.timestamp.desc()).all()
    
    return energy_data


@router.post("/simulate", response_model=List[EnergyDataResponse])
def simulate_energy_data(
    count: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate simulated smart meter data"""
    readings = smart_meter_simulator.generate_batch_readings(count)
    
    created_data = []
    for reading in readings:
        new_energy_data = EnergyData(
            user_id=current_user.id,
            timestamp=reading['timestamp'],
            voltage=reading['voltage'],
            current=reading['current'],
            power=reading['power'],
            energy=reading['energy'],
            frequency=reading['frequency'],
            power_factor=reading['power_factor']
        )
        
        db.add(new_energy_data)
        created_data.append(new_energy_data)
    
    db.commit()
    
    for data in created_data:
        db.refresh(data)
    
    return created_data


@router.post("/upload-csv")
def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV file containing smart meter readings and store them for the current user."""
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        readings = smart_meter_simulator.parse_csv_upload(tmp_path)
        created_data = []

        for reading in readings:
            timestamp = reading.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            if isinstance(timestamp, datetime):
                ts_value = timestamp
            else:
                ts_value = datetime.utcnow()

            new_energy_data = EnergyData(
                user_id=current_user.id,
                timestamp=ts_value,
                voltage=reading.get('voltage'),
                current=reading.get('current'),
                power=reading.get('power'),
                energy=reading.get('energy'),
                frequency=reading.get('frequency'),
                power_factor=reading.get('power_factor')
            )
            db.add(new_energy_data)
            created_data.append(new_energy_data)

        db.commit()
        for data in created_data:
            db.refresh(data)

        return {"message": "CSV uploaded successfully", "count": len(created_data)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.delete("/data/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_energy_data(
    data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete energy data entry"""
    energy_data = db.query(EnergyData).filter(
        EnergyData.id == data_id,
        EnergyData.user_id == current_user.id
    ).first()
    
    if not energy_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy data not found"
        )
    
    db.delete(energy_data)
    db.commit()
    
    return None
