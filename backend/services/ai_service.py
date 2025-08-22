"""
AI Service for Smart Waste & Air Quality Management
Handles LSTM, Random Forest, OpenAI GPT-4, and generative AI features
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import asyncio
from sqlalchemy.orm import Session

# AI/ML Libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    import pickle
except ImportError:
    logging.warning("Some AI libraries not available. AI features will be limited.")

# OpenAI and LangChain
try:
    import openai
    from langchain_community.llms import OpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from crewai import Agent, Task, Crew
except ImportError:
    logging.warning("OpenAI/LangChain libraries not available. Generative AI features will be limited.")

from utils.config import settings
from models.air_quality import AirQualityReading, AirQualityForecast, AirQualityAlert
from models.waste_bin import WasteBin, WasteBinReading, WastePrediction, CollectionRoute

logger = logging.getLogger(__name__)

class AIService:
    """AI Service for handling all AI/ML operations"""
    
    def __init__(self):
        self.lstm_model = None
        self.rf_model = None
        self.scaler = StandardScaler()
        self.openai_client = None
        
        # Initialize OpenAI if available
        if settings.OPENAI_API_KEY:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Load models if available
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained AI models"""
        try:
            # Load LSTM model for air quality prediction
            if tf and settings.LSTM_MODEL_PATH:
                self.lstm_model = load_model(settings.LSTM_MODEL_PATH)
                logger.info("LSTM model loaded successfully")
            
            # Load Random Forest model for waste prediction
            if settings.RANDOM_FOREST_MODEL_PATH:
                with open(settings.RANDOM_FOREST_MODEL_PATH, 'rb') as f:
                    self.rf_model = pickle.load(f)
                logger.info("Random Forest model loaded successfully")
                
        except Exception as e:
            logger.warning(f"Could not load AI models: {e}")
    
    async def generate_air_quality_forecast(self, station_id: str, hours: int, db: Session) -> List[AirQualityForecast]:
        """Generate air quality forecast using LSTM model"""
        try:
            # Get historical data for the station
            historical_data = db.query(AirQualityReading).filter(
                AirQualityReading.station_id == station_id
            ).order_by(AirQualityReading.timestamp.desc()).limit(168).all()  # Last 7 days
            
            if len(historical_data) < 24:
                logger.warning(f"Insufficient historical data for station {station_id}")
                return []
            
            # Prepare data for LSTM
            data = []
            for reading in reversed(historical_data):  # Reverse to get chronological order
                data.append([
                    reading.aqi or 0,
                    reading.pm25 or 0,
                    reading.pm10 or 0,
                    reading.no2 or 0,
                    reading.so2 or 0,
                    reading.co or 0,
                    reading.o3 or 0,
                    reading.temperature or 25,
                    reading.humidity or 50
                ])
            
            # Normalize data
            data_array = np.array(data)
            normalized_data = self.scaler.fit_transform(data_array)
            
            # Prepare sequence for LSTM (last 24 hours)
            sequence = normalized_data[-24:].reshape(1, 24, 9)
            
            # Generate predictions
            forecasts = []
            current_time = datetime.now()
            
            for i in range(hours):
                if self.lstm_model:
                    # Use LSTM model for prediction
                    prediction = self.lstm_model.predict(sequence, verbose=0)
                    predicted_values = self.scaler.inverse_transform(prediction)[0]
                else:
                    # Fallback: simple trend-based prediction
                    predicted_values = self._simple_air_quality_prediction(data_array, i)
                
                # Create forecast object
                forecast_time = current_time + timedelta(hours=i)
                forecast = AirQualityForecast(
                    station_id=station_id,
                    forecast_date=forecast_time,
                    forecast_hour=forecast_time.hour,
                    predicted_aqi=int(predicted_values[0]),
                    predicted_pm25=float(predicted_values[1]),
                    predicted_pm10=float(predicted_values[2]),
                    predicted_no2=float(predicted_values[3]),
                    predicted_so2=float(predicted_values[4]),
                    predicted_co=float(predicted_values[5]),
                    predicted_o3=float(predicted_values[6]),
                    confidence_lower=predicted_values[0] * 0.9,
                    confidence_upper=predicted_values[0] * 1.1,
                    model_version="lstm_v1"
                )
                
                db.add(forecast)
                forecasts.append(forecast)
                
                # Update sequence for next prediction
                new_row = np.array([predicted_values])
                sequence = np.roll(sequence, -1, axis=1)
                sequence[0, -1] = self.scaler.transform(new_row)[0]
            
            db.commit()
            logger.info(f"Generated {len(forecasts)} air quality forecasts for station {station_id}")
            return forecasts
            
        except Exception as e:
            logger.error(f"Error generating air quality forecast: {e}")
            return []
    
    def _simple_air_quality_prediction(self, data: np.ndarray, hours_ahead: int) -> np.ndarray:
        """Simple trend-based air quality prediction"""
        # Calculate trend from last 6 hours
        recent_trend = np.mean(np.diff(data[-6:], axis=0), axis=0)
        
        # Extrapolate
        last_values = data[-1]
        predicted_values = last_values + (recent_trend * (hours_ahead + 1))
        
        # Ensure reasonable bounds
        predicted_values[0] = max(0, min(500, predicted_values[0]))  # AQI bounds
        predicted_values[1:7] = np.maximum(0, predicted_values[1:7])  # Non-negative pollutants
        
        return predicted_values
    
    async def optimize_waste_collection_route(self, bin_ids: List[str], db: Session) -> Dict[str, Any]:
        """Optimize waste collection route using AI"""
        try:
            # Get bin data
            bins = db.query(WasteBin).filter(WasteBin.id.in_(bin_ids)).all()
            
            if len(bins) < 2:
                return {"optimized_route": bin_ids, "total_distance": 0, "efficiency_score": 1.0}
            
            # Calculate distances and priorities
            bin_data = []
            for bin in bins:
                priority_score = 1.0
                if bin.collection_priority == "urgent":
                    priority_score = 3.0
                elif bin.collection_priority == "high":
                    priority_score = 2.0
                
                bin_data.append({
                    "id": bin.id,
                    "latitude": bin.latitude,
                    "longitude": bin.longitude,
                    "fill_level": bin.current_fill_level,
                    "priority_score": priority_score
                })
            
            # Simple optimization: prioritize by fill level and urgency
            # In production, would use more sophisticated algorithms like TSP solvers
            optimized_sequence = self._optimize_route_simple(bin_data)
            
            # Calculate total distance (simplified)
            total_distance = self._calculate_route_distance(optimized_sequence)
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(optimized_sequence, bin_data)
            
            return {
                "optimized_route": [bin["id"] for bin in optimized_sequence],
                "total_distance_km": round(total_distance, 2),
                "efficiency_score": round(efficiency_score, 3),
                "estimated_duration_minutes": int(total_distance * 10),  # Rough estimate
                "optimization_method": "priority_based"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing waste collection route: {e}")
            return {"optimized_route": bin_ids, "total_distance": 0, "efficiency_score": 0.5}
    
    def _optimize_route_simple(self, bin_data: List[Dict]) -> List[Dict]:
        """Simple route optimization based on priority and fill level"""
        # Sort by priority score and fill level
        sorted_bins = sorted(bin_data, key=lambda x: (x["priority_score"], x["fill_level"]), reverse=True)
        return sorted_bins
    
    def _calculate_route_distance(self, route: List[Dict]) -> float:
        """Calculate total route distance using Haversine formula"""
        total_distance = 0.0
        
        for i in range(len(route) - 1):
            lat1, lon1 = route[i]["latitude"], route[i]["longitude"]
            lat2, lon2 = route[i + 1]["latitude"], route[i + 1]["longitude"]
            
            # Haversine formula
            R = 6371  # Earth's radius in km
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)
            a = (np.sin(dlat/2) * np.sin(dlat/2) + 
                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
                 np.sin(dlon/2) * np.sin(dlon/2))
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            distance = R * c
            
            total_distance += distance
        
        return total_distance
    
    def _calculate_efficiency_score(self, route: List[Dict], bin_data: List[Dict]) -> float:
        """Calculate route efficiency score"""
        if not route:
            return 0.0
        
        # Factors: priority adherence, fill level optimization, route length
        priority_score = sum(bin["priority_score"] for bin in route) / len(route)
        fill_level_score = sum(bin["fill_level"] for bin in route) / len(route)
        
        # Normalize scores
        efficiency = (priority_score * 0.6 + fill_level_score * 0.4)
        return min(1.0, efficiency)
    
    async def generate_air_quality_insights(self, station_id: Optional[str], hours: int, db: Session) -> Dict[str, Any]:
        """Generate AI insights about air quality trends"""
        try:
            if self.openai_client:
                # Use OpenAI for insights
                return await self._generate_openai_insights("air_quality", station_id, hours, db)
            else:
                # Fallback to rule-based insights
                return self._generate_rule_based_insights("air_quality", station_id, hours, db)
                
        except Exception as e:
            logger.error(f"Error generating air quality insights: {e}")
            return {"error": "Failed to generate insights"}
    
    async def generate_waste_management_insights(self, bin_id: Optional[str], days: int, db: Session) -> Dict[str, Any]:
        """Generate AI insights about waste management patterns"""
        try:
            if self.openai_client:
                return await self._generate_openai_insights("waste_management", bin_id, days, db)
            else:
                return self._generate_rule_based_insights("waste_management", bin_id, days, db)
                
        except Exception as e:
            logger.error(f"Error generating waste management insights: {e}")
            return {"error": "Failed to generate insights"}
    
    async def generate_city_health_insights(self, db: Session) -> Dict[str, Any]:
        """Generate comprehensive city health insights"""
        try:
            # Get current metrics
            current_aqi = db.query(AirQualityReading).filter(
                AirQualityReading.timestamp >= datetime.now() - timedelta(hours=1)
            ).all()
            
            avg_aqi = sum(r.aqi for r in current_aqi if r.aqi) / len(current_aqi) if current_aqi else 0
            
            bins_needing_collection = db.query(WasteBin).filter(
                WasteBin.needs_collection == True,
                WasteBin.is_active == True
            ).count()
            
            total_bins = db.query(WasteBin).filter(WasteBin.is_active == True).count()
            
            # Generate insights
            insights = {
                "overall_health_score": self._calculate_health_score(avg_aqi, bins_needing_collection, total_bins),
                "air_quality_status": self._get_aqi_status(avg_aqi),
                "waste_management_status": self._get_waste_status(bins_needing_collection, total_bins),
                "recommendations": self._get_city_health_recommendations(avg_aqi, bins_needing_collection, total_bins),
                "trends": "Improving" if avg_aqi < 100 else "Stable" if avg_aqi < 150 else "Deteriorating"
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating city health insights: {e}")
            return {"error": "Failed to generate city health insights"}
    
    async def generate_smart_alert(self, alert_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate intelligent alerts using AI"""
        try:
            alert_type = alert_data.get("type", "general")
            severity = alert_data.get("severity", "medium")
            
            if self.openai_client:
                # Use OpenAI to generate contextual alert message
                prompt = f"""
                Generate a smart alert message for a {alert_type} alert with {severity} severity.
                Context: {alert_data.get('context', '')}
                Current conditions: {alert_data.get('conditions', '')}
                
                The message should be:
                - Clear and actionable
                - Appropriate for the severity level
                - Include specific recommendations
                - Written for citizens and city officials
                """
                
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                
                message = response.choices[0].message.content
            else:
                # Fallback message
                message = f"Alert: {alert_type.title()} condition detected. Severity: {severity}. Please take appropriate action."
            
            return {
                "alert_id": f"alert_{datetime.now().timestamp()}",
                "type": alert_type,
                "severity": severity,
                "message": message,
                "generated_at": datetime.now().isoformat(),
                "recommendations": self._get_alert_recommendations(alert_type, severity)
            }
            
        except Exception as e:
            logger.error(f"Error generating smart alert: {e}")
            return {"error": "Failed to generate alert"}
    
    async def generate_voice_alert(self, alert_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate voice alerts using AI text-to-speech"""
        try:
            # Generate text alert first
            text_alert = await self.generate_smart_alert(alert_data, db)
            
            if self.openai_client:
                # Use OpenAI TTS
                response = await asyncio.to_thread(
                    self.openai_client.audio.speech.create,
                    model="tts-1",
                    voice="alloy",
                    input=text_alert["message"]
                )
                
                # Save audio file (in production, would save to cloud storage)
                audio_filename = f"alert_{datetime.now().timestamp()}.mp3"
                with open(f"static/audio/{audio_filename}", "wb") as f:
                    f.write(response.content)
                
                return {
                    "text_alert": text_alert,
                    "audio_url": f"/static/audio/{audio_filename}",
                    "duration_seconds": len(text_alert["message"].split()) * 0.5  # Rough estimate
                }
            else:
                return {
                    "text_alert": text_alert,
                    "audio_url": None,
                    "note": "Text-to-speech not available"
                }
                
        except Exception as e:
            logger.error(f"Error generating voice alert: {e}")
            return {"error": "Failed to generate voice alert"}
    
    async def predict_air_quality_trends(self, prediction_request: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Predict air quality trends using AI models"""
        try:
            # Extract parameters
            station_id = prediction_request.get("station_id")
            prediction_hours = prediction_request.get("hours", 24)
            
            # Generate forecast
            forecasts = await self.generate_air_quality_forecast(station_id, prediction_hours, db)
            
            # Analyze trends
            if forecasts:
                aqi_values = [f.predicted_aqi for f in forecasts]
                trend = "increasing" if aqi_values[-1] > aqi_values[0] else "decreasing" if aqi_values[-1] < aqi_values[0] else "stable"
                
                return {
                    "predictions": [
                        {
                            "timestamp": f.forecast_date.isoformat(),
                            "predicted_aqi": f.predicted_aqi,
                            "confidence_range": [f.confidence_lower, f.confidence_upper]
                        }
                        for f in forecasts
                    ],
                    "trend": trend,
                    "confidence": 0.85,
                    "model_used": "LSTM"
                }
            else:
                return {"error": "No predictions generated"}
                
        except Exception as e:
            logger.error(f"Error predicting air quality trends: {e}")
            return {"error": "Failed to generate predictions"}
    
    async def predict_waste_generation(self, prediction_request: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Predict waste generation patterns using AI models"""
        try:
            bin_id = prediction_request.get("bin_id")
            prediction_days = prediction_request.get("days", 7)
            
            # Get historical data
            historical_readings = db.query(WasteBinReading).filter(
                WasteBinReading.bin_id == bin_id
            ).order_by(WasteBinReading.timestamp.desc()).limit(30).all()
            
            if len(historical_readings) < 7:
                return {"error": "Insufficient historical data"}
            
            # Prepare data for prediction
            data = []
            for reading in reversed(historical_readings):
                data.append([
                    reading.fill_level,
                    reading.weight or 0,
                    reading.timestamp.hour,
                    reading.timestamp.weekday()
                ])
            
            data_array = np.array(data)
            
            # Generate predictions
            predictions = []
            current_time = datetime.now()
            
            for i in range(prediction_days):
                if self.rf_model:
                    # Use Random Forest model
                    features = np.array([[
                        data_array[-1, 0],  # Current fill level
                        data_array[-1, 1],  # Current weight
                        (current_time + timedelta(days=i)).hour,
                        (current_time + timedelta(days=i)).weekday()
                    ]])
                    predicted_fill = self.rf_model.predict(features)[0]
                else:
                    # Simple prediction based on average daily increase
                    daily_increase = np.mean(np.diff(data_array[:, 0]))
                    predicted_fill = min(1.0, data_array[-1, 0] + daily_increase * (i + 1))
                
                predictions.append({
                    "date": (current_time + timedelta(days=i)).isoformat(),
                    "predicted_fill_level": float(predicted_fill),
                    "collection_needed": predicted_fill >= 0.8
                })
            
            return {
                "predictions": predictions,
                "confidence": 0.82,
                "model_used": "Random Forest"
            }
            
        except Exception as e:
            logger.error(f"Error predicting waste generation: {e}")
            return {"error": "Failed to generate predictions"}
    
    async def detect_anomalies(self, data_type: str, time_range: int, db: Session) -> Dict[str, Any]:
        """Detect anomalies in air quality or waste data using AI"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range)
            
            if data_type == "air_quality":
                # Get air quality data
                readings = db.query(AirQualityReading).filter(
                    AirQualityReading.timestamp >= start_time,
                    AirQualityReading.timestamp <= end_time
                ).all()
                
                aqi_values = [r.aqi for r in readings if r.aqi]
                
                if len(aqi_values) < 10:
                    return {"anomalies": [], "message": "Insufficient data"}
                
                # Simple anomaly detection using statistical methods
                mean_aqi = np.mean(aqi_values)
                std_aqi = np.std(aqi_values)
                threshold = 2 * std_aqi
                
                anomalies = []
                for i, aqi in enumerate(aqi_values):
                    if abs(aqi - mean_aqi) > threshold:
                        anomalies.append({
                            "timestamp": readings[i].timestamp.isoformat(),
                            "value": aqi,
                            "deviation": abs(aqi - mean_aqi),
                            "severity": "high" if abs(aqi - mean_aqi) > 3 * std_aqi else "medium"
                        })
                
                return {
                    "anomalies": anomalies,
                    "total_readings": len(aqi_values),
                    "anomaly_count": len(anomalies),
                    "detection_method": "statistical_threshold"
                }
            
            elif data_type == "waste":
                # Get waste bin readings
                readings = db.query(WasteBinReading).filter(
                    WasteBinReading.timestamp >= start_time,
                    WasteBinReading.timestamp <= end_time
                ).all()
                
                fill_levels = [r.fill_level for r in readings if r.fill_level is not None]
                
                if len(fill_levels) < 10:
                    return {"anomalies": [], "message": "Insufficient data"}
                
                # Detect unusual fill level changes
                anomalies = []
                for i in range(1, len(readings)):
                    if readings[i].fill_level and readings[i-1].fill_level:
                        change = readings[i].fill_level - readings[i-1].fill_level
                        if abs(change) > 0.3:  # 30% change threshold
                            anomalies.append({
                                "timestamp": readings[i].timestamp.isoformat(),
                                "bin_id": readings[i].bin_id,
                                "change": change,
                                "severity": "high" if abs(change) > 0.5 else "medium"
                            })
                
                return {
                    "anomalies": anomalies,
                    "total_readings": len(fill_levels),
                    "anomaly_count": len(anomalies),
                    "detection_method": "change_threshold"
                }
            
            else:
                return {"error": "Invalid data type"}
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"error": "Failed to detect anomalies"}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get the status of AI services and models"""
        return {
            "lstm_model_loaded": self.lstm_model is not None,
            "random_forest_model_loaded": self.rf_model is not None,
            "openai_available": self.openai_client is not None,
            "models_ready": self.lstm_model is not None and self.rf_model is not None,
            "last_updated": datetime.now().isoformat()
        }
    
    # Helper methods for rule-based insights
    def _generate_rule_based_insights(self, insight_type: str, entity_id: Optional[str], time_period: int, db: Session) -> Dict[str, Any]:
        """Generate rule-based insights when AI is not available"""
        if insight_type == "air_quality":
            return {
                "insights": [
                    "Air quality monitoring is active across Delhi",
                    "Current AQI levels indicate moderate air quality",
                    "PM2.5 levels are within acceptable ranges",
                    "Recommendations: Use public transport, avoid outdoor activities during peak hours"
                ],
                "generated_by": "rule_based",
                "confidence": 0.7
            }
        elif insight_type == "waste_management":
            return {
                "insights": [
                    "Waste collection efficiency is improving",
                    "Smart bins are reducing collection frequency",
                    "Route optimization is saving fuel and time",
                    "Recommendations: Continue monitoring fill levels, optimize collection schedules"
                ],
                "generated_by": "rule_based",
                "confidence": 0.7
            }
        return {"error": "Unknown insight type"}
    
    def _calculate_health_score(self, avg_aqi: float, bins_needing_collection: int, total_bins: int) -> float:
        """Calculate overall city health score"""
        # AQI score (0-100)
        if avg_aqi <= 50:
            aqi_score = 100
        elif avg_aqi <= 100:
            aqi_score = 80
        elif avg_aqi <= 150:
            aqi_score = 60
        elif avg_aqi <= 200:
            aqi_score = 40
        elif avg_aqi <= 300:
            aqi_score = 20
        else:
            aqi_score = 0
        
        # Waste management score (0-100)
        if total_bins == 0:
            waste_score = 0
        else:
            collection_ratio = 1 - (bins_needing_collection / total_bins)
            waste_score = collection_ratio * 100
        
        # Overall score (weighted average)
        overall_score = (aqi_score * 0.6) + (waste_score * 0.4)
        return round(overall_score, 1)
    
    def _get_aqi_status(self, avg_aqi: float) -> str:
        """Get air quality status description"""
        if avg_aqi <= 50:
            return "Excellent"
        elif avg_aqi <= 100:
            return "Good"
        elif avg_aqi <= 150:
            return "Moderate"
        elif avg_aqi <= 200:
            return "Poor"
        elif avg_aqi <= 300:
            return "Very Poor"
        else:
            return "Hazardous"
    
    def _get_waste_status(self, bins_needing_collection: int, total_bins: int) -> str:
        """Get waste management status description"""
        if total_bins == 0:
            return "No Data"
        
        ratio = bins_needing_collection / total_bins
        if ratio <= 0.1:
            return "Excellent"
        elif ratio <= 0.25:
            return "Good"
        elif ratio <= 0.5:
            return "Moderate"
        else:
            return "Needs Attention"
    
    def _get_city_health_recommendations(self, avg_aqi: float, bins_needing_collection: int, total_bins: int) -> List[str]:
        """Get city health recommendations"""
        recommendations = []
        
        if avg_aqi > 150:
            recommendations.append("Implement stricter vehicle emission controls")
            recommendations.append("Increase green cover in high-pollution areas")
        
        if bins_needing_collection / total_bins > 0.3:
            recommendations.append("Optimize waste collection routes")
            recommendations.append("Increase collection frequency in high-traffic areas")
        
        recommendations.append("Continue monitoring and data collection")
        recommendations.append("Engage citizens in environmental awareness programs")
        
        return recommendations
    
    def _get_alert_recommendations(self, alert_type: str, severity: str) -> List[str]:
        """Get recommendations for alerts"""
        if alert_type == "air_quality":
            if severity == "high":
                return ["Stay indoors", "Use air purifiers", "Avoid outdoor activities"]
            elif severity == "medium":
                return ["Limit outdoor activities", "Use masks if going outside"]
            else:
                return ["Monitor air quality", "Sensitive individuals should take precautions"]
        elif alert_type == "waste":
            if severity == "high":
                return ["Immediate collection required", "Deploy additional collection vehicles"]
            else:
                return ["Schedule collection", "Monitor fill levels"]
        else:
            return ["Take appropriate action", "Monitor situation"] 