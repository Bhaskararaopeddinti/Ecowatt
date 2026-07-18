"""
AI Module 5: AI Chatbot
Provides intelligent answers about energy consumption using user data as context
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class EnergyChatbot:
    """AI-powered chatbot for energy-related queries"""
    
    def __init__(self):
        # Predefined question patterns and responses
        self.qa_patterns = {
            'bill_high': [
                'why is my bill high',
                'bill increased',
                'high electricity bill',
                'expensive bill',
                'bill too high'
            ],
            'most_consuming': [
                'which appliance uses the most',
                'highest consumption',
                'most electricity',
                'biggest energy user',
                'what uses most power'
            ],
            'reduce_bill': [
                'how can i reduce',
                'save electricity',
                'lower bill',
                'reduce consumption',
                'save energy'
            ],
            'replace_first': [
                'what should i replace',
                'which appliance to replace',
                'upgrade recommendation',
                'replace first'
            ],
            'savings': [
                'how much can i save',
                'potential savings',
                'money saved',
                'save money'
            ],
            'carbon': [
                'carbon footprint',
                'co2',
                'emissions',
                'environmental impact'
            ],
            'leak': [
                'energy leak',
                'phantom load',
                'standby power',
                'wasting electricity'
            ]
        }
        
        self.responses = {
            'bill_high': self._explain_high_bill,
            'most_consuming': self._identify_top_consumer,
            'reduce_bill': self._suggest_savings,
            'replace_first': self._recommend_replacement,
            'savings': self._calculate_savings,
            'carbon': self._explain_carbon,
            'leak': self._explain_leaks,
            'default': self._default_response
        }
    
    def _classify_question(self, question: str) -> str:
        """
        Classify the user's question into a category
        
        Args:
            question: User's question
            
        Returns:
            Category string
        """
        question_lower = question.lower()
        
        for category, patterns in self.qa_patterns.items():
            for pattern in patterns:
                if pattern in question_lower:
                    return category
        
        return 'default'
    
    def _explain_high_bill(self, context: Dict) -> str:
        """Explain why the bill might be high"""
        appliances = context.get('appliances', [])
        alerts = context.get('alerts', [])
        monthly_usage = context.get('monthly_usage', 0)
        
        response = "Your bill may be high due to several factors:\n\n"
        
        # Check for high-consumption appliances
        if appliances:
            top_appliance = max(appliances, key=lambda x: x.get('monthly_cost', 0))
            response += f"• Your {top_appliance.get('name', 'top appliance')} is consuming ₹{top_appliance.get('monthly_cost', 0):.2f}/month\n"
        
        # Check for alerts
        if alerts:
            response += f"• You have {len(alerts)} active alerts indicating potential energy waste\n"
        
        # General usage
        if monthly_usage > 300:
            response += f"• Your monthly usage of {monthly_usage:.1f} kWh is above average\n"
        
        response += "\nI recommend checking the Analysis page for detailed breakdown and following the recommendations to reduce consumption."
        return response
    
    def _identify_top_consumer(self, context: Dict) -> str:
        """Identify the appliance consuming the most electricity"""
        appliances = context.get('appliances', [])
        
        if not appliances:
            return "I don't have enough data to identify your top consuming appliance yet. Please wait for more energy data to be collected."
        
        # Sort by monthly cost
        sorted_appliances = sorted(appliances, key=lambda x: x.get('monthly_cost', 0), reverse=True)
        top_appliance = sorted_appliances[0]
        
        response = f"Your top electricity consumer is **{top_appliance.get('name', 'Unknown')}**:\n\n"
        response += f"• Monthly Cost: ₹{top_appliance.get('monthly_cost', 0):.2f}\n"
        response += f"• Power: {top_appliance.get('power', 0):.1f}W\n"
        response += f"• Percentage: {top_appliance.get('percentage', 0):.1f}%\n"
        
        if len(sorted_appliances) > 1:
            second_appliance = sorted_appliances[1]
            response += f"\nYour second highest consumer is {second_appliance.get('name', 'Unknown')} at ₹{second_appliance.get('monthly_cost', 0):.2f}/month"
        
        return response
    
    def _suggest_savings(self, context: Dict) -> str:
        """Suggest ways to reduce the electricity bill"""
        recommendations = context.get('recommendations', [])
        
        if not recommendations:
            return "Here are some general ways to reduce your electricity bill:\n\n• Increase AC temperature by 1-2°C\n• Turn off devices when not in use\n• Use LED bulbs\n• Run appliances during off-peak hours\n• Maintain your appliances regularly"
        
        # Get top 3 recommendations
        top_recommendations = recommendations[:3]
        
        response = "Here are the top ways to reduce your electricity bill:\n\n"
        for i, rec in enumerate(top_recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n"
            response += f"   Estimated Savings: ₹{rec['estimated_savings']:.2f}/month\n\n"
        
        total_savings = sum(rec['estimated_savings'] for rec in recommendations)
        response += f"**Total Potential Savings: ₹{total_savings:.2f}/month**"
        
        return response
    
    def _recommend_replacement(self, context: Dict) -> str:
        """Recommend which appliance to replace first"""
        appliances = context.get('appliances', [])
        
        if not appliances:
            return "I need more appliance data to make a replacement recommendation. Please ensure your appliances are being monitored."
        
        # Find appliances with high cost or faulty status
        high_cost_appliances = [a for a in appliances if a.get('monthly_cost', 0) > 300]
        faulty_appliances = [a for a in appliances if a.get('status') == 'faulty']
        
        if faulty_appliances:
            faulty = faulty_appliances[0]
            response = f"I recommend replacing or repairing **{faulty.get('name', 'Unknown')}** first:\n\n"
            response += f"• This appliance is showing abnormal consumption patterns\n"
            response += f"• Current monthly cost: ₹{faulty.get('monthly_cost', 0):.2f}\n"
            response += f"• Status: Faulty\n\n"
            response += "This should be addressed immediately to prevent further energy waste."
            return response
        
        if high_cost_appliances:
            high_cost = max(high_cost_appliances, key=lambda x: x.get('monthly_cost', 0))
            response = f"I recommend upgrading **{high_cost.get('name', 'Unknown')}** first:\n\n"
            response += f"• Current monthly cost: ₹{high_cost.get('monthly_cost', 0):.2f}\n"
            response += f"• Power consumption: {high_cost.get('power', 0):.1f}W\n\n"
            
            appliance_type = high_cost.get('type', '').lower()
            if 'ac' in appliance_type or 'air conditioner' in appliance_type:
                response += "Consider replacing with a 5-star rated inverter AC for up to 40% savings."
            elif 'refrigerator' in appliance_type:
                response += "Consider replacing with a 5-star rated refrigerator for up to 50% savings."
            else:
                response += "Consider replacing with a more energy-efficient model."
            
            return response
        
        # Default to highest consumer
        top_appliance = max(appliances, key=lambda x: x.get('monthly_cost', 0))
        return f"Based on current data, **{top_appliance.get('name', 'Unknown')}** has the highest consumption at ₹{top_appliance.get('monthly_cost', 0):.2f}/month. Consider upgrading to a more efficient model."
    
    def _calculate_savings(self, context: Dict) -> str:
        """Calculate potential savings"""
        recommendations = context.get('recommendations', [])
        current_bill = context.get('current_bill', 0)
        
        if not recommendations:
            return f"Based on your current bill of ₹{current_bill:.2f}, you could potentially save 10-20% by following general energy-saving practices."
        
        total_savings = sum(rec['estimated_savings'] for rec in recommendations)
        savings_percentage = (total_savings / current_bill * 100) if current_bill > 0 else 0
        
        response = f"**Potential Savings Analysis**\n\n"
        response += f"Current Monthly Bill: ₹{current_bill:.2f}\n"
        response += f"Potential Monthly Savings: ₹{total_savings:.2f}\n"
        response += f"Savings Percentage: {savings_percentage:.1f}%\n"
        response += f"Projected Monthly Bill: ₹{current_bill - total_savings:.2f}\n\n"
        response += f"**Annual Savings: ₹{total_savings * 12:.2f}**"
        
        return response
    
    def _explain_carbon(self, context: Dict) -> str:
        """Explain carbon footprint"""
        carbon_footprint = context.get('carbon_footprint', 0)
        monthly_usage = context.get('monthly_usage', 0)
        carbon_factor = context.get('carbon_factor', 0.85)
        
        # Calculate trees needed to offset
        trees_needed = carbon_footprint / 21  # Average tree absorbs ~21 kg CO2/year
        
        response = f"**Carbon Footprint Analysis**\n\n"
        response += f"Monthly CO₂ Emissions: {carbon_footprint:.2f} kg\n"
        response += f"Annual CO₂ Emissions: {carbon_footprint * 12:.2f} kg\n"
        response += f"Based on your electricity usage of {monthly_usage:.1f} kWh/month\n\n"
        response += f"To offset your carbon footprint, you would need to plant approximately **{trees_needed:.1f} trees**.\n\n"
        response += "Tips to reduce your carbon footprint:\n"
        response += "• Use renewable energy sources\n"
        response += "• Reduce overall consumption\n"
        response += "• Switch to energy-efficient appliances\n"
        response += "• Use natural light and ventilation"
        
        return response
    
    def _explain_leaks(self, context: Dict) -> str:
        """Explain energy leaks"""
        alerts = context.get('alerts', [])
        
        if not alerts:
            return "No energy leaks have been detected in your home. Great job! Continue monitoring to ensure efficient energy usage."
        
        leak_alerts = [a for a in alerts if a.get('type') in ['phantom_load', 'standby_power', 'energy_spike', 'faulty_appliance']]
        
        if not leak_alerts:
            return "No energy leaks have been detected. Your alerts are for other types of issues."
        
        response = f"**Energy Leak Detection**\n\n"
        response += f"Found {len(leak_alerts)} potential energy leaks:\n\n"
        
        for alert in leak_alerts:
            response += f"• **{alert.get('type', 'Unknown').replace('_', ' ').title()}**\n"
            response += f"  {alert.get('message', 'No details')}\n"
            response += f"  Severity: {alert.get('severity', 'medium').title()}\n\n"
        
        response += "Recommendations:\n"
        response += "• Unplug devices when not in use\n"
        response += "• Use smart power strips\n"
        response += "• Check for faulty appliances\n"
        response += "• Address high-severity alerts immediately"
        
        return response
    
    def _default_response(self, context: Dict) -> str:
        """Default response for unrecognized questions"""
        return "I can help you with questions about:\n\n• Why your electricity bill is high\n• Which appliances use the most electricity\n• How to reduce your electricity bill\n• Which appliances to replace first\n• How much money you can save\n• Your carbon footprint\n• Energy leaks and phantom loads\n\nPlease ask a specific question, and I'll provide personalized answers based on your energy data."
    
    def get_answer(self, question: str, context: Dict) -> str:
        """
        Get an answer to the user's question using their data as context
        
        Args:
            question: User's question
            context: Dictionary with user's energy data (appliances, alerts, recommendations, etc.)
            
        Returns:
            Answer string
        """
        category = self._classify_question(question)
        response_func = self.responses.get(category, self.responses['default'])
        
        return response_func(context)
    
    def get_conversation_context(self, user_id: int, db) -> Dict:
        """
        Build context from database for the chatbot
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Context dictionary with user's energy data
        """
        from models import EnergyData, Appliance, Alert, Recommendation, Prediction
        
        context = {}
        
        # Get recent energy data
        recent_energy = db.query(EnergyData).filter(
            EnergyData.user_id == user_id
        ).order_by(EnergyData.timestamp.desc()).limit(100).all()
        
        if recent_energy:
            df = pd.DataFrame([{
                'timestamp': e.timestamp,
                'power': e.power,
                'energy': e.energy
            } for e in recent_energy])
            
            if 'energy' in df.columns:
                context['monthly_usage'] = df['energy'].sum() * (30 / len(df)) if len(df) > 0 else 0
                context['today_usage'] = df['energy'].sum()
        
        # Get appliances
        appliances = db.query(Appliance).filter(Appliance.user_id == user_id).all()
        context['appliances'] = [{
            'name': a.name,
            'type': a.type,
            'power': a.power_rating,
            'monthly_cost': a.monthly_cost,
            'percentage': a.percentage,
            'status': a.status
        } for a in appliances]
        
        # Get alerts
        alerts = db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_resolved == False
        ).all()
        context['alerts'] = [{
            'type': a.type,
            'severity': a.severity,
            'message': a.message,
            'appliance': a.appliance
        } for a in alerts]
        
        # Get recommendations
        recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.is_implemented == False
        ).order_by(Recommendation.priority.desc()).limit(10).all()
        context['recommendations'] = [{
            'title': r.title,
            'description': r.description,
            'category': r.category,
            'estimated_savings': r.estimated_savings,
            'priority': r.priority
        } for r in recommendations]
        
        # Get predictions
        prediction = db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.prediction_type == 'monthly'
        ).order_by(Prediction.prediction_date.desc()).first()
        
        if prediction:
            context['predicted_bill'] = prediction.predicted_amount
            context['current_bill'] = prediction.current_amount or 0
        
        # Calculate carbon footprint
        monthly_usage = context.get('monthly_usage', 0)
        context['carbon_footprint'] = monthly_usage * 0.85  # kg CO2 per kWh
        context['carbon_factor'] = 0.85
        
        return context


# Singleton instance
chatbot = EnergyChatbot()
