"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Energy Data Schemas
class EnergyDataBase(BaseModel):
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    energy: Optional[float] = None
    frequency: Optional[float] = None
    power_factor: Optional[float] = None


class EnergyDataCreate(EnergyDataBase):
    timestamp: Optional[datetime] = None


class EnergyDataResponse(EnergyDataBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Appliance Schemas
class ApplianceBase(BaseModel):
    name: str
    type: str
    power_rating: Optional[float] = None
    avg_daily_usage: Optional[float] = None


class ApplianceCreate(ApplianceBase):
    pass


class ApplianceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    power_rating: Optional[float] = None
    avg_daily_usage: Optional[float] = None


class ApplianceResponse(ApplianceBase):
    id: int
    user_id: int
    monthly_energy: Optional[float] = None
    monthly_cost: Optional[float] = None
    percentage: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    type: str
    severity: str = "medium"
    message: str
    appliance: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    user_id: int
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Prediction Schemas
class PredictionBase(BaseModel):
    prediction_type: str
    predicted_amount: float
    current_amount: Optional[float] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    target_date: Optional[datetime] = None


class PredictionCreate(PredictionBase):
    pass


class PredictionResponse(PredictionBase):
    id: int
    user_id: int
    prediction_date: datetime

    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationBase(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    estimated_savings: Optional[float] = None
    priority: int = 0


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationResponse(RecommendationBase):
    id: int
    user_id: int
    is_implemented: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Report Schemas
class ReportBase(BaseModel):
    report_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: int
    user_id: int
    file_path: Optional[str] = None
    total_energy: Optional[float] = None
    total_cost: Optional[float] = None
    carbon_footprint: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Chat History Schemas
class ChatHistoryBase(BaseModel):
    question: str
    answer: str
    context: Optional[str] = None


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryResponse(ChatHistoryBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Settings Schemas
class SettingsBase(BaseModel):
    electricity_rate: float = 6.0
    currency: str = "₹"
    theme: str = "light"
    notifications_enabled: bool = True
    email_alerts: bool = False
    sms_alerts: bool = False
    carbon_factor: float = 0.85


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    electricity_rate: Optional[float] = None
    currency: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_alerts: Optional[bool] = None
    sms_alerts: Optional[bool] = None
    carbon_factor: Optional[float] = None


class SettingsResponse(SettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Summary Schema
class DashboardSummary(BaseModel):
    today_usage: float
    monthly_usage: float
    current_bill: float
    predicted_bill: float
    carbon_footprint: float
    energy_score: int
    money_saved: float
    active_alerts: int


# Appliance Detection Result Schema
class ApplianceDetectionResult(BaseModel):
    appliance: str
    power: float
    energy: float
    monthly_cost: float
    percentage: float
    status: str


# Energy Leak Detection Result Schema
class EnergyLeakResult(BaseModel):
    leak_type: str
    severity: str
    message: str
    appliance: Optional[str] = None
    value: float
    threshold: float
