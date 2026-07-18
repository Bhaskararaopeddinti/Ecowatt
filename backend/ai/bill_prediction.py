"""
AI Module 3: Electricity Bill Prediction
Predicts tomorrow's, weekly, and monthly electricity bills
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class BillPredictor:
    """Predicts electricity bills based on historical consumption patterns"""
    
    def __init__(self):
        self.daily_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.weekly_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.monthly_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Electricity rate (can be configured)
        self.electricity_rate = 6.0  # ₹ per kWh
        
    def prepare_features(self, energy_data: List[Dict]) -> np.ndarray:
        """
        Prepare features for ML model
        
        Args:
            energy_data: List of energy data dictionaries
            
        Returns:
            Feature matrix
        """
        if not energy_data:
            return np.array([])
        
        df = pd.DataFrame(energy_data)
        
        # Extract features
        features = []
        
        # Time-based features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            
            features.extend(['hour', 'day_of_week', 'day_of_month', 'month'])
        
        # Energy features
        if 'power' in df.columns:
            features.append('power')
        if 'energy' in df.columns:
            features.append('energy')
        if 'current' in df.columns:
            features.append('current')
        if 'voltage' in df.columns:
            features.append('voltage')
        
        # Create rolling averages
        if 'energy' in df.columns:
            df['energy_rolling_7'] = df['energy'].rolling(window=7, min_periods=1).mean()
            df['energy_rolling_24'] = df['energy'].rolling(window=24, min_periods=1).mean()
            features.extend(['energy_rolling_7', 'energy_rolling_24'])
        
        # Select available features
        available_features = [f for f in features if f in df.columns]
        
        if not available_features:
            return np.array([])
        
        X = df[available_features].values
        return X
    
    def train_daily_model(self, X: np.ndarray, y: np.ndarray):
        """Train daily bill prediction model"""
        if len(X) > 0 and len(y) > 0:
            X_scaled = self.scaler.fit_transform(X)
            self.daily_model.fit(X_scaled, y)
    
    def train_weekly_model(self, X: np.ndarray, y: np.ndarray):
        """Train weekly bill prediction model"""
        if len(X) > 0 and len(y) > 0:
            X_scaled = self.scaler.fit_transform(X)
            self.weekly_model.fit(X_scaled, y)
    
    def train_monthly_model(self, X: np.ndarray, y: np.ndarray):
        """Train monthly bill prediction model"""
        if len(X) > 0 and len(y) > 0:
            X_scaled = self.scaler.fit_transform(X)
            self.monthly_model.fit(X_scaled, y)
    
    def predict_daily_bill(self, energy_data: List[Dict], current_bill: float = 0) -> Dict:
        """
        Predict tomorrow's electricity bill
        
        Args:
            energy_data: Historical energy data
            current_bill: Current month's bill so far
            
        Returns:
            Dictionary with prediction details
        """
        if not energy_data:
            return self._fallback_prediction('daily', current_bill)
        
        # Calculate average daily consumption
        df = pd.DataFrame(energy_data)
        
        if 'energy' in df.columns:
            avg_daily_energy = df['energy'].mean()
            
            # Predict tomorrow's consumption based on recent trend
            recent_data = df.tail(7) if len(df) >= 7 else df
            recent_avg = recent_data['energy'].mean()
            
            # Apply trend factor
            trend_factor = recent_avg / avg_daily_energy if avg_daily_energy > 0 else 1.0
            predicted_energy = recent_avg * trend_factor
            
            predicted_cost = predicted_energy * self.electricity_rate
            
            # Calculate confidence based on data consistency
            std_energy = df['energy'].std()
            confidence = max(0.5, min(0.95, 1.0 - (std_energy / avg_daily_energy) if avg_daily_energy > 0 else 0.7))
            
            reason = f"Based on recent consumption trend ({trend_factor:.2f}x average)"
            
            return {
                'prediction_type': 'daily',
                'predicted_amount': predicted_cost,
                'current_amount': current_bill,
                'confidence': confidence,
                'reason': reason,
                'predicted_energy': predicted_energy
            }
        
        return self._fallback_prediction('daily', current_bill)
    
    def predict_weekly_bill(self, energy_data: List[Dict], current_bill: float = 0) -> Dict:
        """
        Predict weekly electricity bill
        
        Args:
            energy_data: Historical energy data
            current_bill: Current month's bill so far
            
        Returns:
            Dictionary with prediction details
        """
        if not energy_data:
            return self._fallback_prediction('weekly', current_bill)
        
        df = pd.DataFrame(energy_data)
        
        if 'energy' in df.columns:
            # Calculate daily totals
            df['date'] = pd.to_datetime(df['timestamp']).dt.date if 'timestamp' in df.columns else pd.to_datetime('today').date()
            daily_totals = df.groupby('date')['energy'].sum()
            
            if len(daily_totals) >= 7:
                avg_daily = daily_totals.tail(7).mean()
            else:
                avg_daily = daily_totals.mean()
            
            # Predict weekly consumption
            predicted_weekly_energy = avg_daily * 7
            predicted_cost = predicted_weekly_energy * self.electricity_rate
            
            # Calculate confidence
            if len(daily_totals) >= 7:
                std_daily = daily_totals.tail(7).std()
                confidence = max(0.6, min(0.95, 1.0 - (std_daily / avg_daily) if avg_daily > 0 else 0.7))
            else:
                confidence = 0.6
            
            reason = f"Based on {len(daily_totals)} days of data"
            
            return {
                'prediction_type': 'weekly',
                'predicted_amount': predicted_cost,
                'current_amount': current_bill,
                'confidence': confidence,
                'reason': reason,
                'predicted_energy': predicted_weekly_energy
            }
        
        return self._fallback_prediction('weekly', current_bill)
    
    def predict_monthly_bill(self, energy_data: List[Dict], current_bill: float = 0, days_in_month: int = 30) -> Dict:
        """
        Predict monthly electricity bill
        
        Args:
            energy_data: Historical energy data
            current_bill: Current month's bill so far
            days_in_month: Number of days in the current month
            
        Returns:
            Dictionary with prediction details
        """
        if not energy_data:
            return self._fallback_prediction('monthly', current_bill)
        
        df = pd.DataFrame(energy_data)
        
        if 'energy' in df.columns:
            # Calculate daily totals
            df['date'] = pd.to_datetime(df['timestamp']).dt.date if 'timestamp' in df.columns else pd.to_datetime('today').date()
            daily_totals = df.groupby('date')['energy'].sum()
            
            days_so_far = len(daily_totals)
            
            if days_so_far == 0:
                return self._fallback_prediction('monthly', current_bill)
            
            avg_daily = daily_totals.mean()
            
            # Predict monthly consumption
            predicted_monthly_energy = avg_daily * days_in_month
            predicted_cost = predicted_monthly_energy * self.electricity_rate
            
            # Calculate confidence
            std_daily = daily_totals.std()
            confidence = max(0.7, min(0.95, 1.0 - (std_daily / avg_daily) if avg_daily > 0 else 0.8))
            
            # Adjust confidence based on how much data we have
            confidence *= min(1.0, days_so_far / 15)
            
            reason = f"Based on {days_so_far} days of data in current month"
            
            return {
                'prediction_type': 'monthly',
                'predicted_amount': predicted_cost,
                'current_amount': current_bill,
                'confidence': confidence,
                'reason': reason,
                'predicted_energy': predicted_monthly_energy
            }
        
        return self._fallback_prediction('monthly', current_bill)
    
    def _fallback_prediction(self, prediction_type: str, current_bill: float) -> Dict:
        """
        Fallback prediction when insufficient data is available
        
        Args:
            prediction_type: Type of prediction (daily, weekly, monthly)
            current_bill: Current bill amount
            
        Returns:
            Dictionary with fallback prediction
        """
        base_predictions = {
            'daily': 50.0,
            'weekly': 350.0,
            'monthly': 1500.0
        }
        
        return {
            'prediction_type': prediction_type,
            'predicted_amount': base_predictions.get(prediction_type, 100.0),
            'current_amount': current_bill,
            'confidence': 0.3,
            'reason': 'Insufficient historical data for accurate prediction'
        }
    
    def set_electricity_rate(self, rate: float):
        """Set the electricity rate per kWh"""
        self.electricity_rate = rate


# Singleton instance
bill_predictor = BillPredictor()
