"""
AI Module 1: Appliance Detection
Estimates which appliance is consuming electricity using total power consumption
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Dict
import joblib
import os


class ApplianceDetector:
    """Detects appliances based on power consumption patterns"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.appliance_signatures = {
            'Air Conditioner': {'power_range': (1500, 3500), 'pattern': 'continuous_high'},
            'Water Heater': {'power_range': (2000, 4500), 'pattern': 'burst'},
            'Microwave': {'power_range': (600, 1200), 'pattern': 'burst'},
            'Washing Machine': {'power_range': (300, 500), 'pattern': 'cyclic'},
            'Refrigerator': {'power_range': (100, 400), 'pattern': 'cyclic'},
            'Motor': {'power_range': (500, 1500), 'pattern': 'continuous_medium'},
            'TV': {'power_range': (50, 200), 'pattern': 'continuous_low'},
            'Laptop': {'power_range': (30, 100), 'pattern': 'continuous_low'},
            'Fan': {'power_range': (40, 100), 'pattern': 'continuous_low'},
            'Lights': {'power_range': (10, 100), 'pattern': 'continuous_low'}
        }
        
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the appliance detection model"""
        X_scaled = self.scaler.fit_transform(X)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
    def detect_appliance(self, power: float, duration: float = 1.0) -> Dict:
        """
        Detect appliance based on power consumption
        
        Args:
            power: Power consumption in watts
            duration: Duration in hours
            
        Returns:
            Dictionary with appliance information
        """
        # Find matching appliance based on power range
        best_match = None
        best_score = 0
        
        for appliance, signature in self.appliance_signatures.items():
            min_power, max_power = signature['power_range']
            
            # Calculate score based on how close power is to the range
            if min_power <= power <= max_power:
                score = 1.0 - (abs(power - (min_power + max_power) / 2) / (max_power - min_power))
            else:
                # Calculate distance from range
                if power < min_power:
                    distance = min_power - power
                else:
                    distance = power - max_power
                score = max(0, 1.0 - distance / 1000)
            
            if score > best_score:
                best_score = score
                best_match = appliance
        
        if best_match is None:
            best_match = 'Unknown'
        
        # Calculate energy and cost
        energy = power * duration / 1000  # kWh
        monthly_energy = energy * 30  # Assuming daily usage
        monthly_cost = monthly_energy * 6.0  # Assuming ₹6 per kWh
        
        # Determine status
        status = 'normal'
        if best_score < 0.5:
            status = 'warning'
        
        return {
            'appliance': best_match,
            'power': power,
            'energy': energy,
            'monthly_cost': monthly_cost,
            'percentage': best_score * 100,
            'status': status
        }
    
    def analyze_total_consumption(self, power_readings: List[float], electricity_rate: float = 6.0) -> List[Dict]:
        """
        Analyze total power consumption and break down by appliance
        
        Args:
            power_readings: List of power readings in watts
            electricity_rate: Electricity rate per kWh
            
        Returns:
            List of appliance breakdowns
        """
        if not power_readings:
            return []
        
        avg_power = np.mean(power_readings)
        max_power = np.max(power_readings)
        min_power = np.min(power_readings)
        std_power = np.std(power_readings)
        
        # Detect multiple appliances based on power levels
        appliances = []
        
        # Base load (always on)
        base_load = min_power
        if base_load > 50:
            appliances.append(self.detect_appliance(base_load))
        
        # Variable loads
        power_levels = np.percentile(power_readings, [25, 50, 75, 90])
        
        for level in power_levels:
            if level > base_load + 50:
                detected = self.detect_appliance(level - base_load)
                if detected['appliance'] != 'Unknown':
                    appliances.append(detected)
        
        # Calculate percentages
        total_power = sum(a['power'] for a in appliances)
        for appliance in appliances:
            if total_power > 0:
                appliance['percentage'] = (appliance['power'] / total_power) * 100
            appliance['monthly_cost'] = (appliance['power'] * 24 * 30 / 1000) * electricity_rate
        
        # Sort by power consumption
        appliances.sort(key=lambda x: x['power'], reverse=True)
        
        return appliances
    
    def save_model(self, path: str):
        """Save the trained model"""
        if self.model:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, path)
    
    def load_model(self, path: str):
        """Load a trained model"""
        if os.path.exists(path):
            data = joblib.load(path)
            self.model = data['model']
            self.scaler = data['scaler']


# Singleton instance
detector = ApplianceDetector()
