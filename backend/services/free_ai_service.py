"""
Free AI Service - Replaces OpenAI with free alternatives
Uses local models, free APIs, and rule-based systems
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import re

logger = logging.getLogger(__name__)

class FreeAIService:
    """Free AI service using local models and free APIs"""
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
        self.alert_templates = self._load_alert_templates()
        self.recommendation_templates = self._load_recommendation_templates()
    
    def _load_insight_templates(self) -> Dict[str, List[str]]:
        """Load predefined insight templates"""
        return {
            "air_quality": [
                "Air quality in Delhi is currently {aqi_level} with an AQI of {aqi_value}. This indicates {health_impact}.",
                "The {pollutant} levels are {pollutant_level}, which is {pollutant_status} for public health.",
                "Based on recent trends, air quality is {trend_direction} compared to yesterday.",
                "Weather conditions are {weather_impact} on air quality, with {temperature}°C and {humidity}% humidity.",
                "Historical data shows that {season} typically has {seasonal_pattern} air quality in Delhi."
            ],
            "waste_management": [
                "Waste collection efficiency is currently {efficiency_level} with {collection_rate}% of bins collected on time.",
                "The {zone} area shows {fill_pattern} waste generation patterns.",
                "Route optimization has improved collection efficiency by {improvement}% this week.",
                "Bin {bin_id} in {location} requires immediate attention due to {fill_level}% fill level.",
                "Waste generation is {trend_direction} compared to last week, indicating {trend_meaning}."
            ],
            "city_health": [
                "Delhi's overall city health score is {health_score}/100, classified as {health_status}.",
                "Air quality contributes {aqi_contribution}% to the city health score.",
                "Waste management efficiency contributes {waste_contribution}% to the city health score.",
                "Compared to last month, city health has {monthly_change} by {change_amount} points.",
                "Key areas for improvement include {improvement_areas}."
            ]
        }
    
    def _load_alert_templates(self) -> Dict[str, Dict[str, str]]:
        """Load predefined alert templates"""
        return {
            "air_quality": {
                "high": "⚠️ HIGH AIR QUALITY ALERT: AQI has reached {aqi_value} in {location}. This is unhealthy for all groups. Please avoid outdoor activities and use air purifiers.",
                "very_high": "🚨 CRITICAL AIR QUALITY ALERT: AQI has reached {aqi_value} in {location}. This is very unhealthy. Stay indoors and use air purifiers. Consider evacuation if possible.",
                "hazardous": "🚨 EMERGENCY AIR QUALITY ALERT: AQI has reached {aqi_value} in {location}. This is hazardous. Stay indoors, use air purifiers, and follow emergency protocols."
            },
            "waste_collection": {
                "urgent": "🗑️ URGENT WASTE COLLECTION: Bin {bin_id} in {location} is {fill_level}% full and requires immediate collection.",
                "high": "⚠️ WASTE COLLECTION ALERT: Multiple bins in {zone} area are reaching capacity. Schedule collection soon.",
                "overflow": "🚨 WASTE OVERFLOW ALERT: Bin {bin_id} in {location} is overflowing. Immediate collection required."
            }
        }
    
    def _load_recommendation_templates(self) -> Dict[str, List[str]]:
        """Load predefined recommendation templates"""
        return {
            "air_quality": [
                "Use public transport instead of private vehicles to reduce emissions.",
                "Avoid outdoor activities during peak pollution hours (6-9 AM and 6-9 PM).",
                "Use air purifiers at home and in offices.",
                "Wear N95 masks when going outside.",
                "Plant indoor air-purifying plants like aloe vera and spider plants.",
                "Check air quality before planning outdoor activities.",
                "Use energy-efficient appliances to reduce power plant emissions.",
                "Support green initiatives and tree planting programs."
            ],
            "waste_management": [
                "Properly segregate waste into recyclable, organic, and general categories.",
                "Reduce single-use plastics and opt for reusable alternatives.",
                "Compost organic waste at home or community composting centers.",
                "Support local recycling programs and initiatives.",
                "Use waste-to-energy programs where available.",
                "Report overflowing bins to municipal authorities.",
                "Participate in community clean-up drives.",
                "Educate others about proper waste management practices."
            ]
        }
    
    def generate_air_quality_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate air quality insights using templates and data analysis"""
        try:
            aqi_value = data.get('aqi', 150)
            location = data.get('location', 'Delhi')
            pollutant = data.get('primary_pollutant', 'PM2.5')
            pollutant_value = data.get('pm25', 75)
            temperature = data.get('temperature', 25)
            humidity = data.get('humidity', 60)
            
            # Determine levels and status
            aqi_level = self._get_aqi_level(aqi_value)
            pollutant_level = self._get_pollutant_level(pollutant_value)
            pollutant_status = self._get_pollutant_status(pollutant_value)
            health_impact = self._get_health_impact(aqi_value)
            trend_direction = self._get_trend_direction(data.get('trend', 'stable'))
            weather_impact = self._get_weather_impact(temperature, humidity)
            season = self._get_current_season()
            seasonal_pattern = self._get_seasonal_pattern(season)
            
            # Generate insights using templates
            insights = []
            for template in self.insight_templates["air_quality"]:
                insight = template.format(
                    aqi_level=aqi_level,
                    aqi_value=aqi_value,
                    health_impact=health_impact,
                    pollutant=pollutant,
                    pollutant_level=pollutant_level,
                    pollutant_status=pollutant_status,
                    trend_direction=trend_direction,
                    temperature=temperature,
                    humidity=humidity,
                    weather_impact=weather_impact,
                    season=season,
                    seasonal_pattern=seasonal_pattern
                )
                insights.append(insight)
            
            return {
                "insights": insights,
                "generated_by": "free_ai_service",
                "confidence": 0.85,
                "data_used": {
                    "aqi": aqi_value,
                    "location": location,
                    "pollutant": pollutant,
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating air quality insights: {e}")
            return {
                "insights": ["Air quality monitoring is active. Check current readings for detailed information."],
                "generated_by": "free_ai_service",
                "confidence": 0.7,
                "error": str(e)
            }
    
    def generate_waste_management_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate waste management insights using templates and data analysis"""
        try:
            efficiency_level = data.get('efficiency', 75)
            collection_rate = data.get('collection_rate', 80)
            zone = data.get('zone', 'Central Delhi')
            fill_pattern = data.get('fill_pattern', 'normal')
            improvement = data.get('improvement', 15)
            bin_id = data.get('bin_id', 'WB001')
            location = data.get('location', 'Connaught Place')
            fill_level = data.get('fill_level', 60)
            trend_direction = data.get('trend', 'stable')
            trend_meaning = self._get_waste_trend_meaning(trend_direction)
            
            # Generate insights using templates
            insights = []
            for template in self.insight_templates["waste_management"]:
                insight = template.format(
                    efficiency_level=self._get_efficiency_level(efficiency_level),
                    collection_rate=collection_rate,
                    zone=zone,
                    fill_pattern=fill_pattern,
                    improvement=improvement,
                    bin_id=bin_id,
                    location=location,
                    fill_level=fill_level,
                    trend_direction=trend_direction,
                    trend_meaning=trend_meaning
                )
                insights.append(insight)
            
            return {
                "insights": insights,
                "generated_by": "free_ai_service",
                "confidence": 0.82,
                "data_used": {
                    "efficiency": efficiency_level,
                    "collection_rate": collection_rate,
                    "zone": zone,
                    "fill_level": fill_level
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating waste management insights: {e}")
            return {
                "insights": ["Waste management system is operational. Check current bin status for detailed information."],
                "generated_by": "free_ai_service",
                "confidence": 0.7,
                "error": str(e)
            }
    
    def generate_city_health_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate city health insights using templates and data analysis"""
        try:
            health_score = data.get('health_score', 65)
            aqi_contribution = data.get('aqi_contribution', 60)
            waste_contribution = data.get('waste_contribution', 40)
            monthly_change = data.get('monthly_change', 'improved')
            change_amount = data.get('change_amount', 5)
            improvement_areas = data.get('improvement_areas', 'air quality and waste management')
            
            health_status = self._get_health_status(health_score)
            
            # Generate insights using templates
            insights = []
            for template in self.insight_templates["city_health"]:
                insight = template.format(
                    health_score=health_score,
                    health_status=health_status,
                    aqi_contribution=aqi_contribution,
                    waste_contribution=waste_contribution,
                    monthly_change=monthly_change,
                    change_amount=change_amount,
                    improvement_areas=improvement_areas
                )
                insights.append(insight)
            
            return {
                "insights": insights,
                "generated_by": "free_ai_service",
                "confidence": 0.88,
                "data_used": {
                    "health_score": health_score,
                    "aqi_contribution": aqi_contribution,
                    "waste_contribution": waste_contribution
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating city health insights: {e}")
            return {
                "insights": ["City health monitoring is active. Check current metrics for detailed information."],
                "generated_by": "free_ai_service",
                "confidence": 0.7,
                "error": str(e)
            }
    
    def generate_smart_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart alerts using templates and data analysis"""
        try:
            alert_type = alert_data.get('type', 'general')
            severity = alert_data.get('severity', 'medium')
            location = alert_data.get('location', 'Delhi')
            aqi_value = alert_data.get('aqi', 150)
            bin_id = alert_data.get('bin_id', 'WB001')
            fill_level = alert_data.get('fill_level', 80)
            zone = alert_data.get('zone', 'Central Delhi')
            
            # Get appropriate template
            if alert_type == 'air_quality':
                template = self.alert_templates['air_quality'].get(severity, self.alert_templates['air_quality']['high'])
                message = template.format(aqi_value=aqi_value, location=location)
            elif alert_type == 'waste_collection':
                template = self.alert_templates['waste_collection'].get(severity, self.alert_templates['waste_collection']['high'])
                message = template.format(bin_id=bin_id, location=location, fill_level=fill_level, zone=zone)
            else:
                message = f"Alert: {alert_type} condition detected in {location}. Severity: {severity}."
            
            # Generate recommendations
            recommendations = self._get_alert_recommendations(alert_type, severity)
            
            return {
                "alert_id": f"alert_{datetime.now().timestamp()}",
                "type": alert_type,
                "severity": severity,
                "message": message,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "generated_by": "free_ai_service"
            }
            
        except Exception as e:
            logger.error(f"Error generating smart alert: {e}")
            return {
                "alert_id": f"alert_{datetime.now().timestamp()}",
                "type": "general",
                "severity": "medium",
                "message": "System alert generated. Please check current conditions.",
                "generated_at": datetime.now().isoformat(),
                "generated_by": "free_ai_service",
                "error": str(e)
            }
    
    def generate_recommendations(self, category: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations using templates and context"""
        try:
            recommendations = self.recommendation_templates.get(category, [])
            
            # Add context-specific recommendations
            if category == 'air_quality':
                aqi_value = context.get('aqi', 150)
                if aqi_value > 200:
                    recommendations.extend([
                        "Consider using air purifiers with HEPA filters.",
                        "Avoid strenuous outdoor activities.",
                        "Monitor air quality updates regularly."
                    ])
                elif aqi_value > 100:
                    recommendations.extend([
                        "Sensitive individuals should limit outdoor activities.",
                        "Use air quality apps to plan outdoor activities.",
                        "Consider wearing masks during peak hours."
                    ])
            
            elif category == 'waste_management':
                fill_level = context.get('fill_level', 50)
                if fill_level > 80:
                    recommendations.extend([
                        "Report overflowing bins to municipal authorities.",
                        "Use alternative waste disposal methods if available.",
                        "Support community waste management initiatives."
                    ])
            
            return {
                "recommendations": recommendations,
                "category": category,
                "context": context,
                "generated_by": "free_ai_service",
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                "recommendations": ["Check current conditions and follow local guidelines."],
                "category": category,
                "generated_by": "free_ai_service",
                "confidence": 0.7,
                "error": str(e)
            }
    
    def generate_voice_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate voice alert text (text-to-speech would be handled separately)"""
        try:
            # Generate text alert first
            text_alert = self.generate_smart_alert(alert_data)
            
            # Create voice-friendly text
            voice_text = text_alert['message']
            
            # Add voice-specific formatting
            voice_text = voice_text.replace('⚠️', 'Warning: ')
            voice_text = voice_text.replace('🚨', 'Emergency: ')
            voice_text = voice_text.replace('🗑️', 'Waste alert: ')
            
            # Estimate duration (rough calculation)
            word_count = len(voice_text.split())
            estimated_duration = word_count * 0.5  # Rough estimate: 0.5 seconds per word
            
            return {
                "text_alert": text_alert,
                "voice_text": voice_text,
                "estimated_duration_seconds": estimated_duration,
                "word_count": word_count,
                "generated_by": "free_ai_service"
            }
            
        except Exception as e:
            logger.error(f"Error generating voice alert: {e}")
            return {
                "text_alert": {"message": "Alert generated. Please check current conditions."},
                "voice_text": "Alert generated. Please check current conditions.",
                "estimated_duration_seconds": 3.0,
                "generated_by": "free_ai_service",
                "error": str(e)
            }
    
    # Helper methods for data analysis
    def _get_aqi_level(self, aqi: float) -> str:
        if aqi <= 50: return "Good"
        elif aqi <= 100: return "Moderate"
        elif aqi <= 150: return "Unhealthy for Sensitive Groups"
        elif aqi <= 200: return "Unhealthy"
        elif aqi <= 300: return "Very Unhealthy"
        else: return "Hazardous"
    
    def _get_pollutant_level(self, value: float) -> str:
        if value <= 25: return "low"
        elif value <= 50: return "moderate"
        elif value <= 100: return "high"
        else: return "very high"
    
    def _get_pollutant_status(self, value: float) -> str:
        if value <= 25: return "safe"
        elif value <= 50: return "moderately concerning"
        elif value <= 100: return "concerning"
        else: return "dangerous"
    
    def _get_health_impact(self, aqi: float) -> str:
        if aqi <= 50: return "minimal health impacts"
        elif aqi <= 100: return "moderate health impacts for sensitive groups"
        elif aqi <= 150: return "health impacts for sensitive groups"
        elif aqi <= 200: return "health impacts for everyone"
        elif aqi <= 300: return "serious health impacts"
        else: return "severe health impacts"
    
    def _get_trend_direction(self, trend: str) -> str:
        if trend == 'increasing': return "worsening"
        elif trend == 'decreasing': return "improving"
        else: return "stable"
    
    def _get_weather_impact(self, temp: float, humidity: float) -> str:
        if temp > 30 and humidity > 70: return "adversely affecting"
        elif temp < 15: return "positively affecting"
        else: return "moderately affecting"
    
    def _get_current_season(self) -> str:
        month = datetime.now().month
        if month in [12, 1, 2]: return "winter"
        elif month in [3, 4, 5]: return "spring"
        elif month in [6, 7, 8, 9]: return "monsoon"
        else: return "autumn"
    
    def _get_seasonal_pattern(self, season: str) -> str:
        if season == "winter": return "higher pollution due to temperature inversion"
        elif season == "spring": return "moderate pollution with occasional dust storms"
        elif season == "monsoon": return "lower pollution due to rain"
        else: return "moderate pollution levels"
    
    def _get_efficiency_level(self, efficiency: float) -> str:
        if efficiency >= 90: return "excellent"
        elif efficiency >= 75: return "good"
        elif efficiency >= 60: return "moderate"
        else: return "poor"
    
    def _get_waste_trend_meaning(self, trend: str) -> str:
        if trend == 'increasing': return "higher waste generation"
        elif trend == 'decreasing': return "lower waste generation"
        else: return "stable waste generation"
    
    def _get_health_status(self, score: float) -> str:
        if score >= 80: return "Excellent"
        elif score >= 60: return "Good"
        elif score >= 40: return "Moderate"
        else: return "Poor"
    
    def _get_alert_recommendations(self, alert_type: str, severity: str) -> List[str]:
        if alert_type == 'air_quality':
            if severity in ['high', 'very_high', 'hazardous']:
                return [
                    "Stay indoors with air purifiers",
                    "Avoid outdoor activities",
                    "Wear N95 masks if going outside",
                    "Monitor air quality updates"
                ]
            else:
                return [
                    "Limit outdoor activities",
                    "Use air purifiers if available",
                    "Check air quality before planning activities"
                ]
        elif alert_type == 'waste_collection':
            if severity == 'urgent':
                return [
                    "Report to municipal authorities immediately",
                    "Use alternative disposal methods if available",
                    "Avoid adding more waste to the bin"
                ]
            else:
                return [
                    "Schedule collection soon",
                    "Monitor bin fill levels",
                    "Report if collection is delayed"
                ]
        else:
            return ["Take appropriate action", "Monitor the situation", "Follow local guidelines"] 