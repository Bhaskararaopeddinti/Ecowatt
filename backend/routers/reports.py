"""
Reports Router
Handles PDF report generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from database import get_db
from models import User, Report, EnergyData, Appliance, Alert, Recommendation
from schemas import ReportCreate, ReportResponse
from utils.auth import get_current_active_user
import os

router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Reports directory
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new report request"""
    new_report = Report(
        user_id=current_user.id,
        report_type=report.report_type,
        start_date=report.start_date,
        end_date=report.end_date
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get reports for the current user"""
    reports = db.query(Report).filter(
        Report.user_id == current_user.id
    ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific report"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.post("/generate/{report_type}")
def generate_report(
    report_type: str,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a PDF report"""
    # Set default date range
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get data for the report
    energy_data = db.query(EnergyData).filter(
        EnergyData.user_id == current_user.id,
        EnergyData.timestamp >= start_date,
        EnergyData.timestamp <= end_date
    ).all()
    
    appliances = db.query(Appliance).filter(Appliance.user_id == current_user.id).all()
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.created_at >= start_date
    ).all()
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).all()
    
    # Calculate totals
    total_energy = sum(e.energy or 0 for e in energy_data)
    electricity_rate = 6.0
    total_cost = total_energy * electricity_rate
    carbon_footprint = total_energy * 0.85
    
    # Generate PDF (simplified - in production use reportlab properly)
    report_filename = f"report_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_filename)
    
    with open(report_path, 'w') as f:
        f.write(f"EcoWatt AI Energy Report\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"User: {current_user.username}\n")
        f.write(f"Report Period: {start_date.date()} to {end_date.date()}\n")
        f.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"SUMMARY\n")
        f.write(f"{'-'*50}\n")
        f.write(f"Total Energy Consumption: {total_energy:.2f} kWh\n")
        f.write(f"Total Cost: ₹{total_cost:.2f}\n")
        f.write(f"Carbon Footprint: {carbon_footprint:.2f} kg CO2\n\n")
        
        f.write(f"APPLIANCES\n")
        f.write(f"{'-'*50}\n")
        for app in appliances:
            f.write(f"- {app.name} ({app.type})\n")
            f.write(f"  Power: {app.power_rating}W\n")
            f.write(f"  Monthly Cost: ₹{app.monthly_cost:.2f}\n")
            f.write(f"  Status: {app.status}\n\n")
        
        f.write(f"ACTIVE ALERTS\n")
        f.write(f"{'-'*50}\n")
        for alert in alerts[:10]:
            if not alert.is_resolved:
                f.write(f"- {alert.type}\n")
                f.write(f"  {alert.message}\n")
                f.write(f"  Severity: {alert.severity}\n\n")
        
        f.write(f"RECOMMENDATIONS\n")
        f.write(f"{'-'*50}\n")
        for rec in recommendations[:10]:
            f.write(f"- {rec.title}\n")
            f.write(f"  {rec.description}\n")
            f.write(f"  Estimated Savings: ₹{rec.estimated_savings:.2f}\n\n")
    
    # Save report to database
    new_report = Report(
        user_id=current_user.id,
        report_type=report_type,
        file_path=report_path,
        start_date=start_date,
        end_date=end_date,
        total_energy=total_energy,
        total_cost=total_cost,
        carbon_footprint=carbon_footprint
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return {
        'report_id': new_report.id,
        'file_path': report_path,
        'total_energy': total_energy,
        'total_cost': total_cost,
        'carbon_footprint': carbon_footprint
    }


@router.get("/download/{report_id}")
def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a generated report"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    return FileResponse(
        report.file_path,
        filename=os.path.basename(report.file_path),
        media_type='text/plain'
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a report"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete file if exists
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    db.delete(report)
    db.commit()
    
    return None
