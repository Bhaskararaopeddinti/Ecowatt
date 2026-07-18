"""
Smart Meter Data Simulation Service
Generates realistic smart meter data for the MVP
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


class SmartMeterSimulator:
    """Simulates smart meter data with realistic patterns"""
    
    def __init__(self):
        self.base_voltage = 230.0  # Standard voltage in India
        self.base_frequency = 50.0  # Standard frequency in Hz
        
        # Appliance power profiles (in watts)
        self.appliance_profiles = {
            'Air Conditioner': {'min': 1500, 'max': 3500, 'probability': 0.3},
            'Water Heater': {'min': 2000, 'max': 4500, 'probability': 0.1},
            'Microwave': {'min': 600, 'max': 1200, 'probability': 0.05},
            'Washing Machine': {'min': 300, 'max': 500, 'probability': 0.1},
            'Refrigerator': {'min': 100, 'max': 400, 'probability': 0.8},
            'Motor': {'min': 500, 'max': 1500, 'probability': 0.15},
            'TV': {'min': 50, 'max': 200, 'probability': 0.4},
            'Laptop': {'min': 30, 'max': 100, 'probability': 0.5},
            'Fan': {'min': 40, 'max': 100, 'probability': 0.7},
            'Lights': {'min': 10, 'max': 100, 'probability': 0.9}
        }
        
        # Time-based usage patterns
        self.hourly_usage_pattern = [
            0.3, 0.2, 0.2, 0.2, 0.2, 0.3,  # 12AM-6AM (low)
            0.5, 0.7, 0.8, 0.8, 0.7, 0.6,  # 6AM-12PM (morning)
            0.6, 0.7, 0.8, 0.9, 0.9, 0.8,  # 12PM-6PM (afternoon)
            0.9, 0.95, 0.9, 0.8, 0.7, 0.5   # 6PM-12AM (evening)
        ]
    
    def generate_reading(self, timestamp: Optional[datetime] = None) -> Dict:
        """
        Generate a single smart meter reading
        
        Args:
            timestamp: Timestamp for the reading (defaults to now)
            
        Returns:
            Dictionary with smart meter data
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        hour = timestamp.hour
        
        # Calculate base load based on time of day
        time_factor = self.hourly_usage_pattern[hour]
        
        # Add random variation
        variation = random.uniform(0.9, 1.1)
        
        # Calculate voltage with small fluctuations
        voltage = self.base_voltage + random.uniform(-5, 5)
        
        # Calculate current based on active appliances
        current = 0
        power = 0
        
        # Base load (always on appliances)
        base_load = 50 + random.uniform(0, 30)
        power += base_load
        
        # Add appliances based on probability and time
        for appliance, profile in self.appliance_profiles.items():
            if random.random() < profile['probability'] * time_factor:
                appliance_power = random.uniform(profile['min'], profile['max'])
                power += appliance_power
        
        # Add random spikes occasionally
        if random.random() < 0.02:
            spike = random.uniform(500, 2000)
            power += spike
        
        # Calculate current from power and voltage
        current = power / voltage if voltage > 0 else 0
        
        # Calculate energy (kWh) - assuming 5-minute interval
        energy = (power * 5) / 60 / 1000  # kWh for 5 minutes
        
        # Calculate power factor (typically 0.85-0.95)
        power_factor = random.uniform(0.85, 0.95)
        
        # Add frequency fluctuation
        frequency = self.base_frequency + random.uniform(-0.5, 0.5)
        
        return {
            'timestamp': timestamp,
            'voltage': round(voltage, 2),
            'current': round(current, 2),
            'power': round(power, 2),
            'energy': round(energy, 4),
            'frequency': round(frequency, 2),
            'power_factor': round(power_factor, 3)
        }
    
    def generate_batch_readings(self, count: int, start_time: Optional[datetime] = None, 
                                interval_minutes: int = 5) -> List[Dict]:
        """
        Generate a batch of smart meter readings
        
        Args:
            count: Number of readings to generate
            start_time: Start timestamp (defaults to now)
            interval_minutes: Interval between readings in minutes
            
        Returns:
            List of smart meter data dictionaries
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(minutes=count * interval_minutes)
        
        readings = []
        current_time = start_time
        
        for _ in range(count):
            reading = self.generate_reading(current_time)
            readings.append(reading)
            current_time += timedelta(minutes=interval_minutes)
        
        return readings
    
    def generate_csv_data(self, days: int = 30, interval_minutes: int = 5) -> pd.DataFrame:
        """
        Generate data suitable for CSV export
        
        Args:
            days: Number of days of data to generate
            interval_minutes: Interval between readings in minutes
            
        Returns:
            DataFrame with smart meter data
        """
        readings_per_day = (24 * 60) // interval_minutes
        total_readings = readings_per_day * days
        
        readings = self.generate_batch_readings(
            count=total_readings,
            start_time=datetime.utcnow() - timedelta(days=days),
            interval_minutes=interval_minutes
        )
        
        df = pd.DataFrame(readings)
        return df
    
    def parse_csv_upload(self, csv_file_path: str) -> List[Dict]:
        """
        Parse uploaded CSV file with smart meter data
        
        Expected columns: timestamp, voltage, current, power, energy, frequency, power_factor
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            List of smart meter data dictionaries
        """
        try:
            df = pd.read_csv(csv_file_path)
            
            # Validate required columns
            required_columns = ['timestamp', 'voltage', 'current', 'power', 'energy']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert to list of dictionaries
            readings = df.to_dict('records')
            
            # Parse timestamps
            for reading in readings:
                if isinstance(reading['timestamp'], str):
                    reading['timestamp'] = pd.to_datetime(reading['timestamp'])
            
            return readings
            
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    def calculate_daily_totals(self, readings: List[Dict]) -> Dict:
        """
        Calculate daily totals from readings
        
        Args:
            readings: List of smart meter readings
            
        Returns:
            Dictionary with daily totals
        """
        if not readings:
            return {}
        
        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        daily_totals = df.groupby('date').agg({
            'energy': 'sum',
            'power': 'mean',
            'voltage': 'mean',
            'current': 'mean'
        }).to_dict('index')
        
        return daily_totals
    
    def detect_anomalies(self, readings: List[Dict], threshold_std: float = 2.0) -> List[Dict]:
        """
        Detect anomalies in the readings
        
        Args:
            readings: List of smart meter readings
            threshold_std: Number of standard deviations for anomaly threshold
            
        Returns:
            List of anomaly dictionaries
        """
        if not readings:
            return []
        
        df = pd.DataFrame(readings)
        
        anomalies = []
        
        # Check for voltage anomalies
        if 'voltage' in df.columns:
            voltage_mean = df['voltage'].mean()
            voltage_std = df['voltage'].std()
            
            voltage_anomalies = df[
                (df['voltage'] < voltage_mean - threshold_std * voltage_std) |
                (df['voltage'] > voltage_mean + threshold_std * voltage_std)
            ]
            
            for _, row in voltage_anomalies.iterrows():
                anomalies.append({
                    'type': 'voltage_anomaly',
                    'timestamp': row['timestamp'],
                    'value': row['voltage'],
                    'expected': voltage_mean,
                    'severity': 'high' if abs(row['voltage'] - voltage_mean) > 3 * voltage_std else 'medium'
                })
        
        # Check for power anomalies
        if 'power' in df.columns:
            power_mean = df['power'].mean()
            power_std = df['power'].std()
            
            power_anomalies = df[
                df['power'] > power_mean + threshold_std * power_std
            ]
            
            for _, row in power_anomalies.iterrows():
                anomalies.append({
                    'type': 'power_spike',
                    'timestamp': row['timestamp'],
                    'value': row['power'],
                    'expected': power_mean,
                    'severity': 'high' if row['power'] > power_mean + 3 * power_std else 'medium'
                })
        
        return anomalies


# Singleton instance
smart_meter_simulator = SmartMeterSimulator()
