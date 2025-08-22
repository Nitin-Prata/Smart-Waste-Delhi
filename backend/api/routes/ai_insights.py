"""
AI Insights API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from utils.database import get_db
from services.ai_service import AIService
from services.data_service import DataService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/insights/air-quality")
async def get_air_quality_insights(
    station_id: Optional[str] = Query(None, description="Specific station ID"),
    hours: int = Query(24, description="Hours of data to analyze"),
    db: Session = Depends(get_db)
):
    """Get AI-generated insights about air quality trends"""
    try:
        ai_service = AIService()
        insights = await ai_service.generate_air_quality_insights(station_id, hours, db)
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating air quality insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

@router.get("/insights/waste-management")
async def get_waste_management_insights(
    bin_id: Optional[str] = Query(None, description="Specific bin ID"),
    days: int = Query(7, description="Days of data to analyze"),
    db: Session = Depends(get_db)
):
    """Get AI-generated insights about waste management patterns"""
    try:
        ai_service = AIService()
        insights = await ai_service.generate_waste_management_insights(bin_id, days, db)
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating waste management insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

@router.get("/insights/city-health")
async def get_city_health_insights(
    db: Session = Depends(get_db)
):
    """Get comprehensive city health insights combining air quality and waste data"""
    try:
        ai_service = AIService()
        insights = await ai_service.generate_city_health_insights(db)
        
        return {
            "city_health_insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating city health insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

@router.post("/alerts/generate")
async def generate_smart_alert(
    alert_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Generate intelligent alerts using AI"""
    try:
        ai_service = AIService()
        alert = await ai_service.generate_smart_alert(alert_data, db)
        
        return {
            "alert": alert,
            "message": "Smart alert generated successfully"
        }
    except Exception as e:
        logger.error(f"Error generating smart alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate alert")

@router.get("/recommendations/air-quality")
async def get_air_quality_recommendations(
    location: Optional[str] = Query(None, description="Location for recommendations"),
    aqi_level: Optional[str] = Query(None, description="Current AQI level"),
    db: Session = Depends(get_db)
):
    """Get AI-generated recommendations for air quality improvement"""
    try:
        ai_service = AIService()
        recommendations = await ai_service.generate_air_quality_recommendations(
            location, aqi_level, db
        )
        
        return {
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating air quality recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@router.get("/recommendations/waste-optimization")
async def get_waste_optimization_recommendations(
    area: Optional[str] = Query(None, description="Area for optimization"),
    db: Session = Depends(get_db)
):
    """Get AI-generated recommendations for waste management optimization"""
    try:
        ai_service = AIService()
        recommendations = await ai_service.generate_waste_optimization_recommendations(
            area, db
        )
        
        return {
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating waste optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@router.post("/predictions/air-quality")
async def predict_air_quality_trends(
    prediction_request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Predict air quality trends using AI models"""
    try:
        ai_service = AIService()
        predictions = await ai_service.predict_air_quality_trends(prediction_request, db)
        
        return {
            "predictions": predictions,
            "model_info": {
                "model_type": "LSTM",
                "version": "1.0",
                "confidence": predictions.get("confidence", 0.85)
            }
        }
    except Exception as e:
        logger.error(f"Error predicting air quality trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")

@router.post("/predictions/waste-generation")
async def predict_waste_generation(
    prediction_request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Predict waste generation patterns using AI models"""
    try:
        ai_service = AIService()
        predictions = await ai_service.predict_waste_generation(prediction_request, db)
        
        return {
            "predictions": predictions,
            "model_info": {
                "model_type": "Random Forest",
                "version": "1.0",
                "confidence": predictions.get("confidence", 0.82)
            }
        }
    except Exception as e:
        logger.error(f"Error predicting waste generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")

from fastapi import Body

@router.get("/visualizations/generate")
async def generate_ai_visualization(
    visualization_type: str = Query(..., description="Type of visualization to generate"),
    data_params: Optional[Dict[str, Any]] = Body(None, description="Parameters for visualization"),
    db: Session = Depends(get_db)
):
    """Generate AI-powered visualizations"""
    try:
        ai_service = AIService()
        visualization = await ai_service.generate_visualization(visualization_type, data_params, db)
        
        return {
            "visualization": visualization,
            "type": visualization_type,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate visualization")

@router.post("/voice-alerts")
async def generate_voice_alert(
    alert_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Generate voice alerts using AI text-to-speech"""
    try:
        ai_service = AIService()
        voice_alert = await ai_service.generate_voice_alert(alert_data, db)
        
        return {
            "voice_alert": voice_alert,
            "message": "Voice alert generated successfully"
        }
    except Exception as e:
        logger.error(f"Error generating voice alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice alert")

@router.get("/anomaly-detection")
async def detect_anomalies(
    data_type: str = Query(..., description="Type of data to analyze (air_quality, waste)"),
    time_range: int = Query(24, description="Hours to analyze for anomalies"),
    db: Session = Depends(get_db)
):
    """Detect anomalies in air quality or waste data using AI"""
    try:
        ai_service = AIService()
        anomalies = await ai_service.detect_anomalies(data_type, time_range, db)
        
        return {
            "anomalies": anomalies,
            "data_type": data_type,
            "time_range_hours": time_range,
            "detected_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")

@router.get("/correlation-analysis")
async def analyze_correlations(
    variables: List[str] = Query(..., description="Variables to analyze"),
    time_period: int = Query(30, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """Analyze correlations between different environmental variables"""
    try:
        ai_service = AIService()
        correlations = await ai_service.analyze_correlations(variables, time_period, db)
        
        return {
            "correlations": correlations,
            "variables": variables,
            "time_period_days": time_period,
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing correlations: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze correlations")

@router.get("/trend-analysis")
async def analyze_trends(
    metric: str = Query(..., description="Metric to analyze (aqi, waste_generation, etc.)"),
    trend_period: str = Query("weekly", description="Period for trend analysis"),
    db: Session = Depends(get_db)
):
    """Analyze trends in environmental metrics"""
    try:
        ai_service = AIService()
        trends = await ai_service.analyze_trends(metric, trend_period, db)
        
        return {
            "trends": trends,
            "metric": metric,
            "trend_period": trend_period,
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze trends")

@router.post("/optimization/suggestions")
async def get_optimization_suggestions(
    optimization_request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Get AI-powered optimization suggestions for city operations"""
    try:
        ai_service = AIService()
        suggestions = await ai_service.generate_optimization_suggestions(optimization_request, db)
        
        return {
            "optimization_suggestions": suggestions,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")

@router.get("/ai-status")
async def get_ai_service_status():
    """Get the status of AI services and models"""
    try:
        ai_service = AIService()
        status = await ai_service.get_service_status()
        
        return {
            "ai_service_status": status,
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking AI service status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check AI service status") 