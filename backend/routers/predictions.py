"""
Predictions Router
Handles bill predictions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from database import get_db
from models import User, Prediction, EnergyData
from schemas import PredictionCreate, PredictionResponse
from utils.auth import get_current_active_user
from ai.bill_prediction import bill_predictor

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    prediction: PredictionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new prediction"""
    new_prediction = Prediction(
        user_id=current_user.id,
        prediction_type=prediction.prediction_type,
        predicted_amount=prediction.predicted_amount,
        current_amount=prediction.current_amount,
        confidence=prediction.confidence,
        reason=prediction.reason,
        target_date=prediction.target_date
    )
    
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    
    return new_prediction


@router.get("/", response_model=List[PredictionResponse])
def get_predictions(
    prediction_type: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get predictions for the current user"""
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)
    
    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)
    
    predictions = query.order_by(Prediction.prediction_date.desc()).limit(10).all()
    
    return predictions


@router.post("/generate/daily", response_model=dict)
def generate_daily_prediction(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate daily bill prediction using AI"""
    # Get recent energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(100).all()
    
    # Get current bill from settings or calculate
    current_bill = 0
    
    # Convert energy data to dict format
    energy_list = [{
        'timestamp': e.timestamp,
        'energy': e.energy,
        'power': e.power
    } for e in energy_data]
    
    # Generate prediction
    prediction = bill_predictor.predict_daily_bill(energy_list, current_bill)
    
    # Save prediction to database
    new_prediction = Prediction(
        user_id=current_user.id,
        prediction_type='daily',
        predicted_amount=prediction['predicted_amount'],
        current_amount=prediction.get('current_amount', current_bill),
        confidence=prediction.get('confidence'),
        reason=prediction.get('reason'),
        target_date=datetime.utcnow() + timedelta(days=1)
    )
    
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    
    return prediction


@router.post("/generate/weekly", response_model=dict)
def generate_weekly_prediction(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate weekly bill prediction using AI"""
    # Get recent energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(500).all()
    
    current_bill = 0
    
    energy_list = [{
        'timestamp': e.timestamp,
        'energy': e.energy,
        'power': e.power
    } for e in energy_data]
    
    prediction = bill_predictor.predict_weekly_bill(energy_list, current_bill)
    
    new_prediction = Prediction(
        user_id=current_user.id,
        prediction_type='weekly',
        predicted_amount=prediction['predicted_amount'],
        current_amount=prediction.get('current_amount', current_bill),
        confidence=prediction.get('confidence'),
        reason=prediction.get('reason'),
        target_date=datetime.utcnow() + timedelta(weeks=1)
    )
    
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    
    return prediction


@router.post("/generate/monthly", response_model=dict)
def generate_monthly_prediction(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate monthly bill prediction using AI"""
    # Get recent energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(2000).all()
    
    current_bill = 0
    
    energy_list = [{
        'timestamp': e.timestamp,
        'energy': e.energy,
        'power': e.power
    } for e in energy_data]
    
    prediction = bill_predictor.predict_monthly_bill(energy_list, current_bill)
    
    new_prediction = Prediction(
        user_id=current_user.id,
        prediction_type='monthly',
        predicted_amount=prediction['predicted_amount'],
        current_amount=prediction.get('current_amount', current_bill),
        confidence=prediction.get('confidence'),
        reason=prediction.get('reason'),
        target_date=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    
    return prediction
