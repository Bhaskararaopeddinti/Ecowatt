"""
Dashboard Router
Handles dashboard summary and statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models import User, EnergyData, Alert, Prediction, Recommendation
from schemas import DashboardSummary
from utils.auth import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary statistics"""
    # Get today's usage
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_energy = db.query(func.sum(EnergyData.energy)).filter(
        EnergyData.user_id == current_user.id,
        EnergyData.timestamp >= today_start
    ).scalar() or 0
    
    # Get monthly usage
    month_start = today_start.replace(day=1)
    monthly_energy = db.query(func.sum(EnergyData.energy)).filter(
        EnergyData.user_id == current_user.id,
        EnergyData.timestamp >= month_start
    ).scalar() or 0
    
    # Calculate current bill (assuming ₹6 per kWh)
    electricity_rate = 6.0
    current_bill = monthly_energy * electricity_rate
    
    # Get predicted bill
    prediction = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.prediction_type == 'monthly'
    ).order_by(Prediction.prediction_date.desc()).first()
    
    predicted_bill = prediction.predicted_amount if prediction else current_bill * 1.1
    
    # Calculate carbon footprint (0.85 kg CO2 per kWh)
    carbon_footprint = monthly_energy * 0.85
    
    # Calculate energy score (0-100 based on efficiency)
    # Simple scoring: lower usage = higher score
    avg_daily_usage = monthly_energy / 30 if monthly_energy > 0 else 0
    energy_score = max(0, min(100, 100 - (avg_daily_usage - 10) * 2))
    
    # Calculate money saved from implemented recommendations
    implemented_savings = db.query(func.sum(Recommendation.estimated_savings)).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.is_implemented == True
    ).scalar() or 0
    
    money_saved = implemented_savings
    
    # Count active alerts
    active_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False
    ).count()
    
    return DashboardSummary(
        today_usage=round(today_energy, 2),
        monthly_usage=round(monthly_energy, 2),
        current_bill=round(current_bill, 2),
        predicted_bill=round(predicted_bill, 2),
        carbon_footprint=round(carbon_footprint, 2),
        energy_score=int(energy_score),
        money_saved=round(money_saved, 2),
        active_alerts=active_alerts
    )


@router.get("/usage-chart")
def get_usage_chart_data(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get energy usage data for chart"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily energy totals
    energy_data = db.query(
        func.date(EnergyData.timestamp).label('date'),
        func.sum(EnergyData.energy).label('total_energy'),
        func.avg(EnergyData.power).label('avg_power')
    ).filter(
        EnergyData.user_id == current_user.id,
        EnergyData.timestamp >= start_date
    ).group_by(func.date(EnergyData.timestamp)).all()
    
    chart_data = [
        {
            'date': str(row.date),
            'energy': round(row.total_energy or 0, 2),
            'power': round(row.avg_power or 0, 2)
        }
        for row in energy_data
    ]
    
    return chart_data


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent activity for the dashboard"""
    activities = []
    
    # Get recent energy readings
    recent_energy = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(limit).all()
    
    for energy in recent_energy:
        activities.append({
            'type': 'energy_reading',
            'message': f'Energy reading: {energy.energy:.4f} kWh',
            'timestamp': energy.timestamp
        })
    
    # Get recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    for alert in recent_alerts:
        activities.append({
            'type': 'alert',
            'message': f'Alert: {alert.message}',
            'timestamp': alert.created_at
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:limit]
