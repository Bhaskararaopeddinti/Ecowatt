"""
AI Module 2: Energy Leak Detection
Detects phantom load, high standby power, energy spikes, faulty appliances
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class EnergyLeakDetector:
    """Detects energy leaks and anomalies in consumption patterns"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Thresholds for different leak types
        self.thresholds = {
            'phantom_load': 10.0,  # Watts
            'standby_power': 50.0,  # Watts
            'spike_multiplier': 3.0,  # Times average
            'long_running_hours': 24,  # Hours
            'abnormal_usage_percent': 30.0  # Percent deviation
        }
        
    def detect_phantom_load(self, power_readings: List[float]) -> Dict:
        """
        Detect phantom load (devices consuming power when supposedly off)
        
        Args:
            power_readings: List of power readings in watts
            
        Returns:
            Dictionary with phantom load detection result
        """
        if not power_readings:
            return None
        
        min_power = np.min(power_readings)
        avg_power = np.mean(power_readings)
        
        if min_power > self.thresholds['phantom_load']:
            return {
                'leak_type': 'phantom_load',
                'severity': 'medium' if min_power < 30 else 'high',
                'message': f'Phantom load detected: {min_power:.1f}W consumed when devices should be off',
                'appliance': 'Multiple Devices',
                'value': min_power,
                'threshold': self.thresholds['phantom_load']
            }
        
        return None
    
    def detect_standby_power(self, power_readings: List[float]) -> Dict:
        """
        Detect high standby power consumption
        
        Args:
            power_readings: List of power readings in watts
            
        Returns:
            Dictionary with standby power detection result
        """
        if not power_readings:
            return None
        
        # Find the minimum sustained power (likely standby)
        sorted_readings = sorted(power_readings)
        bottom_10_percent = sorted_readings[:max(1, len(sorted_readings) // 10)]
        avg_standby = np.mean(bottom_10_percent)
        
        if avg_standby > self.thresholds['standby_power']:
            return {
                'leak_type': 'standby_power',
                'severity': 'medium' if avg_standby < 100 else 'high',
                'message': f'High standby power detected: {avg_standby:.1f}W in standby mode',
                'appliance': 'Multiple Devices',
                'value': avg_standby,
                'threshold': self.thresholds['standby_power']
            }
        
        return None
    
    def detect_energy_spikes(self, power_readings: List[float]) -> List[Dict]:
        """
        Detect sudden energy spikes
        
        Args:
            power_readings: List of power readings in watts
            
        Returns:
            List of spike detection results
        """
        if not power_readings:
            return []
        
        alerts = []
        avg_power = np.mean(power_readings)
        std_power = np.std(power_readings)
        
        spike_threshold = avg_power * self.thresholds['spike_multiplier']
        
        for i, power in enumerate(power_readings):
            if power > spike_threshold:
                alerts.append({
                    'leak_type': 'energy_spike',
                    'severity': 'high',
                    'message': f'Energy spike detected: {power:.1f}W (avg: {avg_power:.1f}W)',
                    'appliance': 'Unknown',
                    'value': power,
                    'threshold': spike_threshold
                })
        
        return alerts
    
    def detect_faulty_appliance(self, appliance_data: Dict) -> Dict:
        """
        Detect if an appliance is consuming abnormal power
        
        Args:
            appliance_data: Dictionary with appliance info including current_power, expected_power
            
        Returns:
            Dictionary with faulty appliance detection result
        """
        current_power = appliance_data.get('current_power', 0)
        expected_power = appliance_data.get('expected_power', 0)
        appliance_name = appliance_data.get('name', 'Unknown')
        
        if expected_power == 0:
            return None
        
        deviation_percent = abs(current_power - expected_power) / expected_power * 100
        
        if deviation_percent > self.thresholds['abnormal_usage_percent']:
            severity = 'high' if deviation_percent > 50 else 'medium'
            return {
                'leak_type': 'faulty_appliance',
                'severity': severity,
                'message': f'{appliance_name} is consuming {deviation_percent:.1f}% more electricity than normal',
                'appliance': appliance_name,
                'value': current_power,
                'threshold': expected_power * (1 + self.thresholds['abnormal_usage_percent'] / 100)
            }
        
        return None
    
    def detect_long_running_device(self, appliance_usage: Dict) -> Dict:
        """
        Detect devices running longer than expected
        
        Args:
            appliance_usage: Dictionary with appliance usage info
            
        Returns:
            Dictionary with long-running device detection result
        """
        appliance_name = appliance_usage.get('name', 'Unknown')
        running_hours = appliance_usage.get('running_hours', 0)
        expected_hours = appliance_usage.get('expected_hours', 8)
        
        if running_hours > self.thresholds['long_running_hours']:
            return {
                'leak_type': 'long_running_device',
                'severity': 'medium',
                'message': f'{appliance_name} has been running for {running_hours:.1f} hours continuously',
                'appliance': appliance_name,
                'value': running_hours,
                'threshold': self.thresholds['long_running_hours']
            }
        
        return None
    
    def detect_abnormal_usage(self, current_usage: float, historical_usage: List[float]) -> Dict:
        """
        Detect abnormal usage patterns compared to historical data
        
        Args:
            current_usage: Current usage value
            historical_usage: List of historical usage values
            
        Returns:
            Dictionary with abnormal usage detection result
        """
        if not historical_usage:
            return None
        
        avg_historical = np.mean(historical_usage)
        std_historical = np.std(historical_usage)
        
        if std_historical == 0:
            std_historical = 1  # Avoid division by zero
        
        z_score = abs(current_usage - avg_historical) / std_historical
        
        if z_score > 2:  # More than 2 standard deviations
            severity = 'high' if z_score > 3 else 'medium'
            deviation_percent = abs(current_usage - avg_historical) / avg_historical * 100
            return {
                'leak_type': 'abnormal_usage',
                'severity': severity,
                'message': f'Abnormal usage detected: {deviation_percent:.1f}% deviation from normal',
                'appliance': 'Overall',
                'value': current_usage,
                'threshold': avg_historical + 2 * std_historical
            }
        
        return None
    
    def analyze_all_leaks(self, power_readings: List[float], appliances: List[Dict] = None) -> List[Dict]:
        """
        Run all leak detection algorithms
        
        Args:
            power_readings: List of power readings in watts
            appliances: Optional list of appliance data
            
        Returns:
            List of all detected leaks
        """
        leaks = []
        
        # Detect phantom load
        phantom_load = self.detect_phantom_load(power_readings)
        if phantom_load:
            leaks.append(phantom_load)
        
        # Detect standby power
        standby_power = self.detect_standby_power(power_readings)
        if standby_power:
            leaks.append(standby_power)
        
        # Detect energy spikes
        spikes = self.detect_energy_spikes(power_readings)
        leaks.extend(spikes)
        
        # Check appliances for faults
        if appliances:
            for appliance in appliances:
                faulty = self.detect_faulty_appliance(appliance)
                if faulty:
                    leaks.append(faulty)
        
        return leaks
    
    def train_anomaly_detector(self, X: np.ndarray):
        """Train the isolation forest anomaly detector"""
        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
    
    def detect_anomalies(self, power_readings: List[float]) -> List[int]:
        """
        Detect anomalies using isolation forest
        
        Args:
            power_readings: List of power readings
            
        Returns:
            List of indices where anomalies were detected
        """
        if not power_readings or self.isolation_forest is None:
            return []
        
        X = np.array(power_readings).reshape(-1, 1)
        X_scaled = self.scaler.transform(X)
        predictions = self.isolation_forest.predict(X_scaled)
        
        # Return indices where prediction is -1 (anomaly)
        anomalies = [i for i, pred in enumerate(predictions) if pred == -1]
        return anomalies


# Singleton instance
leak_detector = EnergyLeakDetector()
