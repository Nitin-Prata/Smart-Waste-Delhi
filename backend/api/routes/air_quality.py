"""
Air Quality API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import numpy as np
from tensorflow.keras.models import load_model
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

from utils.database import get_db
from models.air_quality import AirQualityStation, AirQualityReading, AirQualityAlert, AirQualityForecast
from services.ai_service import AIService
from services.data_service import DataService

router = APIRouter()
logger = logging.getLogger(__name__)

# AQI prediction endpoint
@router.post("/predict")
async def predict_aqi(
    input_data: Dict[str, Any] = Body(...)
):
    """Predict AQI using trained LSTM model"""
    try:
        import tensorflow as tf
        import pandas as pd
        # Load the trained model
        model = tf.keras.models.load_model("models/aqi_lstm_model.h5")
        # Prepare input data as DataFrame
        df = pd.DataFrame([input_data])
        # Preprocess if needed (assume already scaled for now)
        prediction = model.predict(df)[0][0]
        return {"predicted_aqi": float(prediction)}
    except Exception as e:
        logger.error(f"Error in AQI prediction: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# --- LSTM AQI Prediction Endpoint ---
@router.get("/api/aqi/predict")
def predict_aqi_lstm():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../models/aqi_lstm_model.h5'))
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/delhi_aqi_clean.csv'))
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found.")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data file not found.")
    model = load_model(model_path)
    df = pd.read_csv(data_path)
    values = df['pm2_5'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled_values = scaler.fit_transform(values)
    SEQ_LEN = 24
    if len(scaled_values) < SEQ_LEN:
        raise HTTPException(status_code=400, detail="Not enough data for prediction.")
    last_seq = scaled_values[-SEQ_LEN:]
    last_seq = np.expand_dims(last_seq, axis=0)
    pred_scaled = model.predict(last_seq)
    pred = scaler.inverse_transform(pred_scaled)[0][0]
    return {"predicted_pm2_5": float(pred)}

@router.get("/stations")
async def get_air_quality_stations(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Return only active stations")
):
    """Get all air quality monitoring stations"""
    try:
        query = db.query(AirQualityStation)
        if active_only:
            query = query.filter(AirQualityStation.is_active == True)
        
        stations = query.all()
        return {
            "stations": [
                {
                    "id": station.id,
                    "name": station.name,
                    "location": station.location,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "station_type": station.station_type,
                    "is_active": station.is_active
                }
                for station in stations
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching air quality stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stations")

@router.get("/stations/{station_id}")
async def get_station_details(
    station_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific station"""
    try:
        station = db.query(AirQualityStation).filter(AirQualityStation.id == station_id).first()
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Get latest reading
        latest_reading = db.query(AirQualityReading).filter(
            AirQualityReading.station_id == station_id
        ).order_by(AirQualityReading.timestamp.desc()).first()
        
        return {
            "station": {
                "id": station.id,
                "name": station.name,
                "location": station.location,
                "latitude": station.latitude,
                "longitude": station.longitude,
                "station_type": station.station_type,
                "is_active": station.is_active,
                "created_at": station.created_at
            },
            "latest_reading": {
                "aqi": latest_reading.aqi if latest_reading else None,
                "aqi_category": latest_reading.aqi_category if latest_reading else None,
                "pm25": latest_reading.pm25 if latest_reading else None,
                "pm10": latest_reading.pm10 if latest_reading else None,
                "timestamp": latest_reading.timestamp if latest_reading else None
            } if latest_reading else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching station details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch station details")

@router.get("/readings")
async def get_air_quality_readings(
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    start_time: Optional[datetime] = Query(None, description="Start time for readings"),
    end_time: Optional[datetime] = Query(None, description="End time for readings"),
    limit: int = Query(100, description="Number of readings to return"),
    db: Session = Depends(get_db)
):
    """Get air quality readings with optional filters"""
    try:
        query = db.query(AirQualityReading)
        
        if station_id:
            query = query.filter(AirQualityReading.station_id == station_id)
        
        if start_time:
            query = query.filter(AirQualityReading.timestamp >= start_time)
        
        if end_time:
            query = query.filter(AirQualityReading.timestamp <= end_time)
        
        readings = query.order_by(AirQualityReading.timestamp.desc()).limit(limit).all()
        
        return {
            "readings": [
                {
                    "id": reading.id,
                    "station_id": reading.station_id,
                    "timestamp": reading.timestamp,
                    "aqi": reading.aqi,
                    "aqi_category": reading.aqi_category,
                    "pm25": reading.pm25,
                    "pm10": reading.pm10,
                    "no2": reading.no2,
                    "so2": reading.so2,
                    "co": reading.co,
                    "o3": reading.o3,
                    "temperature": reading.temperature,
                    "humidity": reading.humidity,
                    "source": reading.source
                }
                for reading in readings
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching air quality readings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch readings")

@router.get("/current")
async def get_current_air_quality(
    db: Session = Depends(get_db)
):
    """Get current air quality for all active stations"""
    try:
        # Get all active stations
        stations = db.query(AirQualityStation).filter(AirQualityStation.is_active == True).all()
        
        current_readings = []
        for station in stations:
            # Get latest reading for each station
            latest = db.query(AirQualityReading).filter(
                AirQualityReading.station_id == station.id
            ).order_by(AirQualityReading.timestamp.desc()).first()
            
            if latest:
                current_readings.append({
                    "station_id": station.id,
                    "station_name": station.name,
                    "location": station.location,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "aqi": latest.aqi,
                    "aqi_category": latest.aqi_category,
                    "pm25": latest.pm25,
                    "pm10": latest.pm10,
                    "timestamp": latest.timestamp
                })
        
        return {"current_readings": current_readings}
    except Exception as e:
        logger.error(f"Error fetching current air quality: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch current air quality")

@router.get("/forecast/{station_id}")
async def get_air_quality_forecast(
    station_id: str,
    hours: int = Query(24, description="Number of hours to forecast"),
    db: Session = Depends(get_db)
):
    """Get air quality forecast for a specific station"""
    try:
        # Check if station exists
        station = db.query(AirQualityStation).filter(AirQualityStation.id == station_id).first()
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Get existing forecasts
        forecasts = db.query(AirQualityForecast).filter(
            AirQualityForecast.station_id == station_id,
            AirQualityForecast.forecast_date >= datetime.now()
        ).order_by(AirQualityForecast.forecast_date).limit(hours).all()
        
        # If no forecasts exist, generate new ones
        if not forecasts:
            ai_service = AIService()
            forecasts = await ai_service.generate_air_quality_forecast(station_id, hours, db)
        
        return {
            "station_id": station_id,
            "station_name": station.name,
            "forecasts": [
                {
                    "forecast_date": forecast.forecast_date,
                    "forecast_hour": forecast.forecast_hour,
                    "predicted_aqi": forecast.predicted_aqi,
                    "predicted_pm25": forecast.predicted_pm25,
                    "predicted_pm10": forecast.predicted_pm10,
                    "confidence_lower": forecast.confidence_lower,
                    "confidence_upper": forecast.confidence_upper,
                    "model_version": forecast.model_version
                }
                for forecast in forecasts
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching air quality forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecast")

@router.get("/alerts")
async def get_air_quality_alerts(
    active_only: bool = Query(True, description="Return only active alerts"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    db: Session = Depends(get_db)
):
    """Get air quality alerts"""
    try:
        query = db.query(AirQualityAlert)
        
        if active_only:
            query = query.filter(AirQualityAlert.is_active == True)
        
        if severity:
            query = query.filter(AirQualityAlert.severity == severity)
        
        alerts = query.order_by(AirQualityAlert.triggered_at.desc()).all()
        
        return {
            "alerts": [
                {
                    "id": alert.id,
                    "station_id": alert.station_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "aqi_threshold": alert.aqi_threshold,
                    "current_aqi": alert.current_aqi,
                    "triggered_at": alert.triggered_at,
                    "is_active": alert.is_active,
                    "acknowledged": alert.acknowledged
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching air quality alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(..., description="Name of person acknowledging"),
    db: Session = Depends(get_db)
):
    """Acknowledge an air quality alert"""
    try:
        alert = db.query(AirQualityAlert).filter(AirQualityAlert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()
        
        db.commit()
        
        return {"message": "Alert acknowledged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")

@router.get("/summary")
async def get_air_quality_summary(
    db: Session = Depends(get_db)
):
    """Get air quality summary statistics"""
    try:
        # Get current AQI distribution
        current_readings = db.query(AirQualityReading).filter(
            AirQualityReading.timestamp >= datetime.now() - timedelta(hours=1)
        ).all()
        
        aqi_categories = {
            "Good": 0,
            "Moderate": 0,
            "Unhealthy for Sensitive Groups": 0,
            "Unhealthy": 0,
            "Very Unhealthy": 0,
            "Hazardous": 0
        }
        
        total_aqi = 0
        count = 0
        
        for reading in current_readings:
            if reading.aqi:
                total_aqi += reading.aqi
                count += 1
                
                if reading.aqi_category:
                    aqi_categories[reading.aqi_category] = aqi_categories.get(reading.aqi_category, 0) + 1
        
        avg_aqi = total_aqi / count if count > 0 else 0
        
        # Get active alerts count
        active_alerts = db.query(AirQualityAlert).filter(AirQualityAlert.is_active == True).count()
        
        return {
            "summary": {
                "average_aqi": round(avg_aqi, 1),
                "total_stations": len(current_readings),
                "active_alerts": active_alerts,
                "aqi_distribution": aqi_categories
            }
        }
    except Exception as e:
        logger.error(f"Error fetching air quality summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch summary") 