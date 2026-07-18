"""
Database models for EcoWatt AI
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    energy_data = relationship("EnergyData", back_populates="user")
    appliances = relationship("Appliance", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    reports = relationship("Report", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    settings = relationship("Settings", back_populates="user", uselist=False)


class EnergyData(Base):
    """Smart meter energy data"""
    __tablename__ = "energy_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    voltage = Column(Float)  # Volts
    current = Column(Float)  # Amperes
    power = Column(Float)  # Watts
    energy = Column(Float)  # kWh
    frequency = Column(Float)  # Hz
    power_factor = Column(Float)

    # Relationships
    user = relationship("User", back_populates="energy_data")


class Appliance(Base):
    """Appliance information and consumption"""
    __tablename__ = "appliances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # AC, Fan, Lights, TV, etc.
    power_rating = Column(Float)  # Watts
    avg_daily_usage = Column(Float)  # Hours
    monthly_energy = Column(Float)  # kWh
    monthly_cost = Column(Float)
    percentage = Column(Float)
    status = Column(String, default="normal")  # normal, warning, faulty
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="appliances")


class Alert(Base):
    """Energy leak and anomaly alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # phantom_load, standby_power, spike, faulty, etc.
    severity = Column(String, default="medium")  # low, medium, high
    message = Column(Text, nullable=False)
    appliance = Column(String)
    value = Column(Float)
    threshold = Column(Float)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="alerts")


class Prediction(Base):
    """Bill predictions"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_type = Column(String, nullable=False)  # daily, weekly, monthly
    predicted_amount = Column(Float, nullable=False)
    current_amount = Column(Float)
    confidence = Column(Float)
    reason = Column(Text)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="predictions")


class Recommendation(Base):
    """AI-generated recommendations"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)  # appliance, behavior, upgrade
    estimated_savings = Column(Float)
    priority = Column(Integer, default=0)
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recommendations")


class Report(Base):
    """Generated PDF reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String, nullable=False)  # monthly, weekly, custom
    file_path = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_energy = Column(Float)
    total_cost = Column(Float)
    carbon_footprint = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")


class ChatHistory(Base):
    """AI Chatbot conversation history"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    context = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_history")


class Settings(Base):
    """User settings and preferences"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    electricity_rate = Column(Float, default=6.0)  # Rate per kWh
    currency = Column(String, default="₹")
    theme = Column(String, default="light")  # light, dark
    notifications_enabled = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=False)
    sms_alerts = Column(Boolean, default=False)
    carbon_factor = Column(Float, default=0.85)  # kg CO2 per kWh
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")
