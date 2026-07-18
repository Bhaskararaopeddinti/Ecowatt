"""
Recommendations Router
Handles AI-generated energy-saving recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import User, Recommendation, EnergyData, Appliance, Alert
from schemas import RecommendationCreate, RecommendationResponse
from utils.auth import get_current_active_user
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    recommendation: RecommendationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new recommendation"""
    new_recommendation = Recommendation(
        user_id=current_user.id,
        title=recommendation.title,
        description=recommendation.description,
        category=recommendation.category,
        estimated_savings=recommendation.estimated_savings,
        priority=recommendation.priority
    )
    
    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)
    
    return new_recommendation


@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    skip: int = 0,
    limit: int = 20,
    unimplemented_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for the current user"""
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    
    if unimplemented_only:
        query = query.filter(Recommendation.is_implemented == False)
    
    recommendations = query.order_by(
        Recommendation.priority.desc(),
        Recommendation.estimated_savings.desc()
    ).offset(skip).limit(limit).all()
    
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation


@router.put("/{recommendation_id}/implement", response_model=RecommendationResponse)
def implement_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as implemented"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.is_implemented = True
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    db.delete(recommendation)
    db.commit()
    
    return None


@router.post("/generate", response_model=List[dict])
def generate_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate personalized recommendations using AI"""
    # Get energy data
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id
    ).order_by(EnergyData.timestamp.desc()).limit(500).all()
    
    # Get appliances
    appliances = db.query(Appliance).filter(Appliance.user_id == current_user.id).all()
    
    # Get alerts
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False
    ).all()
    
    # Convert to dict format
    energy_list = [{
        'timestamp': e.timestamp,
        'energy': e.energy,
        'power': e.power
    } for e in energy_data]
    
    appliance_list = [{
        'name': a.name,
        'type': a.type,
        'power_rating': a.power_rating,
        'monthly_cost': a.monthly_cost,
        'status': a.status
    } for a in appliances]
    
    alert_list = [{
        'type': a.type,
        'severity': a.severity,
        'message': a.message,
        'appliance': a.appliance
    } for a in alerts]
    
    # Generate recommendations
    recommendations = recommendation_engine.generate_recommendations(
        energy_list,
        appliance_list,
        alert_list
    )
    
    # Save recommendations to database
    for rec in recommendations:
        existing_rec = db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id,
            Recommendation.title == rec['title']
        ).first()
        
        if not existing_rec:
            new_rec = Recommendation(
                user_id=current_user.id,
                title=rec['title'],
                description=rec['description'],
                category=rec.get('category'),
                estimated_savings=rec.get('estimated_savings'),
                priority=rec.get('priority', 0)
            )
            db.add(new_rec)
    
    db.commit()
    
    return recommendations
