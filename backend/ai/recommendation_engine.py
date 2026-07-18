"""
AI Module 4: Recommendation Engine
Generates personalized recommendations to reduce electricity costs
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime


class RecommendationEngine:
    """Generates personalized energy-saving recommendations"""
    
    def __init__(self):
        self.recommendations_db = {
            'high_usage': [
                {
                    'title': 'Reduce AC Temperature',
                    'description': 'Increase your AC temperature by 1-2°C to save significant energy',
                    'category': 'behavior',
                    'estimated_savings': 450,
                    'priority': 10
                },
                {
                    'title': 'Use AC Timer',
                    'description': 'Set AC to turn off automatically when not needed',
                    'category': 'behavior',
                    'estimated_savings': 300,
                    'priority': 8
                }
            ],
            'old_appliance': [
                {
                    'title': 'Replace Old Refrigerator',
                    'description': 'Old refrigerators consume 2-3x more energy than new 5-star rated ones',
                    'category': 'upgrade',
                    'estimated_savings': 300,
                    'priority': 9
                },
                {
                    'title': 'Upgrade to LED Bulbs',
                    'description': 'Replace incandescent bulbs with LED to save up to 80% on lighting',
                    'category': 'upgrade',
                    'estimated_savings': 120,
                    'priority': 7
                },
                {
                    'title': 'Replace Old AC',
                    'description': 'Old AC units have low efficiency. Consider a 5-star rated inverter AC',
                    'category': 'upgrade',
                    'estimated_savings': 800,
                    'priority': 10
                }
            ],
            'behavior': [
                {
                    'title': 'Turn Off Standby Devices',
                    'description': 'Unplug devices when not in use to eliminate phantom load',
                    'category': 'behavior',
                    'estimated_savings': 150,
                    'priority': 6
                },
                {
                    'title': 'Use Natural Light',
                    'description': 'Open curtains during the day to reduce artificial lighting needs',
                    'category': 'behavior',
                    'estimated_savings': 80,
                    'priority': 5
                },
                {
                    'title': 'Optimize Fan Usage',
                    'description': 'Use fans instead of AC when possible for cooling',
                    'category': 'behavior',
                    'estimated_savings': 400,
                    'priority': 7
                },
                {
                    'title': 'Run Appliances Off-Peak',
                    'description': 'Run heavy appliances during off-peak hours if applicable',
                    'category': 'behavior',
                    'estimated_savings': 200,
                    'priority': 6
                }
            ],
            'appliance': [
                {
                    'title': 'Maintain Refrigerator Coils',
                    'description': 'Clean refrigerator coils regularly to improve efficiency',
                    'category': 'appliance',
                    'estimated_savings': 100,
                    'priority': 5
                },
                {
                    'title': 'Defrost Regularly',
                    'description': 'Defrost freezer regularly to maintain efficiency',
                    'category': 'appliance',
                    'estimated_savings': 80,
                    'priority': 4
                },
                {
                    'title': 'Use Cold Water for Laundry',
                    'description': 'Wash clothes in cold water to save heating energy',
                    'category': 'appliance',
                    'estimated_savings': 150,
                    'priority': 6
                }
            ]
        }
    
    def generate_recommendations(self, energy_data: List[Dict], appliances: List[Dict], 
                                alerts: List[Dict], electricity_rate: float = 6.0) -> List[Dict]:
        """
        Generate personalized recommendations based on user data
        
        Args:
            energy_data: Historical energy data
            appliances: List of appliances with consumption data
            alerts: List of energy leak alerts
            electricity_rate: Electricity rate per kWh
            
        Returns:
            List of personalized recommendations
        """
        recommendations = []
        
        # Analyze energy consumption patterns
        if energy_data:
            df = pd.DataFrame(energy_data)
            if 'energy' in df.columns:
                avg_daily = df['energy'].mean()
                total_monthly = avg_daily * 30
                
                # High usage recommendations
                if total_monthly > 300:  # kWh per month
                    for rec in self.recommendations_db['high_usage']:
                        recommendations.append(rec.copy())
        
        # Analyze appliances
        if appliances:
            for appliance in appliances:
                appliance_type = appliance.get('type', '').lower()
                monthly_cost = appliance.get('monthly_cost', 0)
                
                # Old appliance recommendations
                if 'refrigerator' in appliance_type and monthly_cost > 500:
                    recommendations.append(self.recommendations_db['old_appliance'][0].copy())
                
                if 'ac' in appliance_type or 'air conditioner' in appliance_type:
                    recommendations.append(self.recommendations_db['high_usage'][0].copy())
                
                if 'lights' in appliance_type or 'bulb' in appliance_type:
                    recommendations.append(self.recommendations_db['old_appliance'][1].copy())
        
        # Analyze alerts
        if alerts:
            for alert in alerts:
                alert_type = alert.get('type', '')
                
                if alert_type == 'phantom_load' or alert_type == 'standby_power':
                    recommendations.append(self.recommendations_db['behavior'][0].copy())
                
                if alert_type == 'faulty_appliance':
                    faulty_rec = {
                        'title': f'Repair or Replace {alert.get("appliance", "Device")}',
                        'description': f'This appliance is consuming abnormal power and may need repair',
                        'category': 'appliance',
                        'estimated_savings': 200,
                        'priority': 9
                    }
                    recommendations.append(faulty_rec)
        
        # Add general behavior recommendations
        for rec in self.recommendations_db['behavior']:
            if not any(r['title'] == rec['title'] for r in recommendations):
                recommendations.append(rec.copy())
        
        # Add appliance maintenance recommendations
        for rec in self.recommendations_db['appliance']:
            if not any(r['title'] == rec['title'] for r in recommendations):
                recommendations.append(rec.copy())
        
        # Calculate actual savings based on electricity rate
        for rec in recommendations:
            if rec['estimated_savings']:
                rec['estimated_savings'] = rec['estimated_savings'] * (electricity_rate / 6.0)
        
        # Sort by priority and savings
        recommendations.sort(key=lambda x: (x['priority'], x['estimated_savings']), reverse=True)
        
        # Return top recommendations
        return recommendations[:10]
    
    def generate_appliance_specific_recommendation(self, appliance: Dict) -> Dict:
        """
        Generate recommendation for a specific appliance
        
        Args:
            appliance: Appliance dictionary
            
        Returns:
            Recommendation dictionary
        """
        appliance_type = appliance.get('type', '').lower()
        monthly_cost = appliance.get('monthly_cost', 0)
        status = appliance.get('status', 'normal')
        
        # Check if appliance is faulty
        if status == 'faulty':
            return {
                'title': f'Immediate Action Required: {appliance.get("name", "Appliance")}',
                'description': 'This appliance is showing abnormal consumption patterns. Please check for faults or consider replacement.',
                'category': 'appliance',
                'estimated_savings': monthly_cost * 0.3,
                'priority': 10
            }
        
        # Type-specific recommendations
        if 'ac' in appliance_type or 'air conditioner' in appliance_type:
            return {
                'title': 'Optimize AC Usage',
                'description': 'Set temperature to 24°C, use timer, and service regularly',
                'category': 'behavior',
                'estimated_savings': monthly_cost * 0.2,
                'priority': 8
            }
        
        if 'refrigerator' in appliance_type:
            return {
                'title': 'Optimize Refrigerator Usage',
                'description': 'Avoid frequent door opening, maintain proper temperature, and clean coils',
                'category': 'appliance',
                'estimated_savings': monthly_cost * 0.15,
                'priority': 6
            }
        
        if 'water heater' in appliance_type:
            return {
                'title': 'Optimize Water Heater Usage',
                'description': 'Use timer, lower temperature to 50°C, and insulate pipes',
                'category': 'behavior',
                'estimated_savings': monthly_cost * 0.25,
                'priority': 7
            }
        
        # Generic recommendation
        return {
            'title': f'Optimize {appliance.get("name", "Appliance")} Usage',
            'description': 'Use this appliance only when needed and turn off when not in use',
            'category': 'behavior',
            'estimated_savings': monthly_cost * 0.1,
            'priority': 5
        }
    
    def calculate_potential_savings(self, recommendations: List[Dict]) -> Tuple[float, Dict]:
        """
        Calculate total potential savings from recommendations
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Tuple of (total_savings, breakdown_by_category)
        """
        total_savings = 0
        breakdown = {}
        
        for rec in recommendations:
            savings = rec.get('estimated_savings', 0)
            total_savings += savings
            
            category = rec.get('category', 'other')
            if category not in breakdown:
                breakdown[category] = 0
            breakdown[category] += savings
        
        return total_savings, breakdown
    
    def rank_recommendations(self, recommendations: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """
        Rank recommendations based on user preferences and impact
        
        Args:
            recommendations: List of recommendations
            user_preferences: Optional user preferences dictionary
            
        Returns:
            Ranked list of recommendations
        """
        if user_preferences:
            preferred_category = user_preferences.get('preferred_category')
            budget = user_preferences.get('budget', float('inf'))
            
            for rec in recommendations:
                score = rec['priority']
                
                # Boost score for preferred category
                if preferred_category and rec['category'] == preferred_category:
                    score += 3
                
                # Adjust score based on budget
                if rec.get('estimated_savings', 0) > budget:
                    score -= 2
                
                rec['score'] = score
            
            recommendations.sort(key=lambda x: x['score'], reverse=True)
        else:
            recommendations.sort(key=lambda x: (x['priority'], x['estimated_savings']), reverse=True)
        
        return recommendations


# Singleton instance
recommendation_engine = RecommendationEngine()
