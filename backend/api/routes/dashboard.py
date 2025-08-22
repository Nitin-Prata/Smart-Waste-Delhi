"""
Dashboard API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from utils.database import get_db
from models.air_quality import AirQualityStation, AirQualityReading, AirQualityAlert
from models.waste_bin import WasteBin, WasteCollection
from services.ai_service import AIService
from services.data_service import DataService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview"""
    try:
        # Get current air quality summary
        current_aqi_readings = db.query(AirQualityReading).filter(
            AirQualityReading.timestamp >= datetime.now() - timedelta(hours=1)
        ).all()
        
        avg_aqi = 0
        if current_aqi_readings:
            avg_aqi = sum(r.aqi for r in current_aqi_readings if r.aqi) / len(current_aqi_readings)
        
        # Get waste management summary
        total_bins = db.query(WasteBin).filter(WasteBin.is_active == True).count()
        bins_needing_collection = db.query(WasteBin).filter(
            WasteBin.needs_collection == True,
            WasteBin.is_active == True
        ).count()
        
        # Get today's collections
        today = datetime.now().date()
        today_collections = db.query(WasteCollection).filter(
            WasteCollection.collection_date >= today
        ).count()
        
        # Get active alerts
        active_alerts = db.query(AirQualityAlert).filter(AirQualityAlert.is_active == True).count()
        
        return {
            "overview": {
                "current_aqi": round(avg_aqi, 1),
                "total_monitoring_stations": len(current_aqi_readings),
                "total_waste_bins": total_bins,
                "bins_needing_collection": bins_needing_collection,
                "today_collections": today_collections,
                "active_alerts": active_alerts,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch overview")

@router.get("/city-health")
async def get_city_health_dashboard(
    db: Session = Depends(get_db)
):
    """Get city health dashboard with combined metrics"""
    try:
        # Air Quality Health Score
        aqi_readings = db.query(AirQualityReading).filter(
            AirQualityReading.timestamp >= datetime.now() - timedelta(hours=24)
        ).all()
        
        aqi_scores = []
        for reading in aqi_readings:
            if reading.aqi:
                if reading.aqi <= 50:
                    aqi_scores.append(100)  # Excellent
                elif reading.aqi <= 100:
                    aqi_scores.append(80)   # Good
                elif reading.aqi <= 150:
                    aqi_scores.append(60)   # Moderate
                elif reading.aqi <= 200:
                    aqi_scores.append(40)   # Poor
                elif reading.aqi <= 300:
                    aqi_scores.append(20)   # Very Poor
                else:
                    aqi_scores.append(0)    # Hazardous
        
        air_quality_health = sum(aqi_scores) / len(aqi_scores) if aqi_scores else 0
        
        # Waste Management Health Score
        bins = db.query(WasteBin).filter(WasteBin.is_active == True).all()
        waste_scores = []
        for bin in bins:
            if bin.current_fill_level <= 0.5:
                waste_scores.append(100)  # Excellent
            elif bin.current_fill_level <= 0.75:
                waste_scores.append(75)   # Good
            elif bin.current_fill_level <= 0.9:
                waste_scores.append(50)   # Moderate
            else:
                waste_scores.append(25)   # Poor
        
        waste_management_health = sum(waste_scores) / len(waste_scores) if waste_scores else 0
        
        # Overall City Health Score
        overall_health = (air_quality_health + waste_management_health) / 2
        
        return {
            "city_health": {
                "overall_health_score": round(overall_health, 1),
                "air_quality_health": round(air_quality_health, 1),
                "waste_management_health": round(waste_management_health, 1),
                "health_status": "Excellent" if overall_health >= 80 else "Good" if overall_health >= 60 else "Moderate" if overall_health >= 40 else "Poor",
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching city health dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch city health")

@router.get("/real-time-map")
async def get_real_time_map_data(
    db: Session = Depends(get_db)
):
    """Get real-time data for map visualization"""
    try:
        # Get air quality stations with current readings
        stations = db.query(AirQualityStation).filter(AirQualityStation.is_active == True).all()
        air_quality_data = []
        
        for station in stations:
            latest_reading = db.query(AirQualityReading).filter(
                AirQualityReading.station_id == station.id
            ).order_by(AirQualityReading.timestamp.desc()).first()
            
            if latest_reading:
                air_quality_data.append({
                    "type": "air_quality",
                    "id": station.id,
                    "name": station.name,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "aqi": latest_reading.aqi,
                    "aqi_category": latest_reading.aqi_category,
                    "timestamp": latest_reading.timestamp.isoformat()
                })
        
        # Get waste bins with current status
        bins = db.query(WasteBin).filter(WasteBin.is_active == True).all()
        waste_data = []
        
        for bin in bins:
            waste_data.append({
                "type": "waste_bin",
                "id": bin.id,
                "name": bin.name,
                "latitude": bin.latitude,
                "longitude": bin.longitude,
                "fill_level": bin.current_fill_level,
                "needs_collection": bin.needs_collection,
                "priority": bin.collection_priority,
                "last_updated": bin.last_updated.isoformat()
            })
        
        return {
            "map_data": {
                "air_quality_stations": air_quality_data,
                "waste_bins": waste_data,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching real-time map data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch map data")

@router.get("/trends")
async def get_dashboard_trends(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get trend data for dashboard charts"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Air Quality Trends
        aqi_trends = db.query(AirQualityReading).filter(
            AirQualityReading.timestamp >= start_date,
            AirQualityReading.timestamp <= end_date
        ).order_by(AirQualityReading.timestamp).all()
        
        aqi_data = []
        for reading in aqi_trends:
            if reading.aqi:
                aqi_data.append({
                    "timestamp": reading.timestamp.isoformat(),
                    "aqi": reading.aqi,
                    "pm25": reading.pm25,
                    "pm10": reading.pm10
                })
        
        # Waste Collection Trends
        collection_trends = db.query(WasteCollection).filter(
            WasteCollection.collection_date >= start_date,
            WasteCollection.collection_date <= end_date
        ).order_by(WasteCollection.collection_date).all()
        
        waste_data = []
        for collection in collection_trends:
            waste_data.append({
                "date": collection.collection_date.isoformat(),
                "waste_collected": collection.waste_collected,
                "collection_duration": collection.collection_duration
            })
        
        return {
            "trends": {
                "air_quality": aqi_data,
                "waste_collection": waste_data,
                "period_days": days
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trends")

@router.get("/alerts-summary")
async def get_alerts_summary(
    db: Session = Depends(get_db)
):
    """Get summary of all active alerts"""
    try:
        # Air Quality Alerts
        air_quality_alerts = db.query(AirQualityAlert).filter(
            AirQualityAlert.is_active == True
        ).order_by(AirQualityAlert.triggered_at.desc()).all()
        
        # Waste Collection Alerts (bins needing collection)
        waste_alerts = db.query(WasteBin).filter(
            WasteBin.needs_collection == True,
            WasteBin.is_active == True
        ).all()
        
        return {
            "alerts_summary": {
                "air_quality_alerts": [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at.isoformat(),
                        "acknowledged": alert.acknowledged
                    }
                    for alert in air_quality_alerts
                ],
                "waste_collection_alerts": [
                    {
                        "bin_id": bin.id,
                        "bin_name": bin.name,
                        "location": bin.location,
                        "fill_level": bin.current_fill_level,
                        "priority": bin.collection_priority,
                        "last_updated": bin.last_updated.isoformat()
                    }
                    for bin in waste_alerts
                ],
                "total_air_quality_alerts": len(air_quality_alerts),
                "total_waste_alerts": len(waste_alerts),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching alerts summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts summary")

@router.get("/performance-metrics")
async def get_performance_metrics(
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    try:
        # Collection Efficiency
        today = datetime.now().date()
        today_collections = db.query(WasteCollection).filter(
            WasteCollection.collection_date >= today
        ).all()
        
        total_collection_time = sum(c.collection_duration for c in today_collections if c.collection_duration)
        total_waste_collected = sum(c.waste_collected for c in today_collections if c.waste_collected)
        
        efficiency_score = 0
        if total_collection_time > 0:
            efficiency_score = (total_waste_collected / total_collection_time) * 100
        
        # Air Quality Monitoring Coverage
        active_stations = db.query(AirQualityStation).filter(AirQualityStation.is_active == True).count()
        total_stations = db.query(AirQualityStation).count()
        coverage_percentage = (active_stations / total_stations * 100) if total_stations > 0 else 0
        
        # Response Time (average time from alert to acknowledgment)
        acknowledged_alerts = db.query(AirQualityAlert).filter(
            AirQualityAlert.acknowledged == True,
            AirQualityAlert.acknowledged_at.isnot(None)
        ).all()
        
        response_times = []
        for alert in acknowledged_alerts:
            if alert.acknowledged_at and alert.triggered_at:
                response_time = (alert.acknowledged_at - alert.triggered_at).total_seconds() / 60  # minutes
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "performance_metrics": {
                "collection_efficiency_score": round(efficiency_score, 2),
                "air_quality_coverage_percentage": round(coverage_percentage, 2),
                "average_response_time_minutes": round(avg_response_time, 2),
                "today_collections": len(today_collections),
                "total_waste_collected_today_kg": round(total_waste_collected, 2),
                "active_monitoring_stations": active_stations,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance metrics")

@router.get("/citizen-view")
async def get_citizen_dashboard(
    location: Optional[str] = Query(None, description="Citizen's location"),
    db: Session = Depends(get_db)
):
    """Get citizen-friendly dashboard view"""
    try:
        # Get nearest air quality station
        nearest_station = None
        if location:
            # Simplified logic - in real app, would use geocoding
            stations = db.query(AirQualityStation).filter(AirQualityStation.is_active == True).all()
            if stations:
                nearest_station = stations[0]  # Simplified - would calculate actual nearest
        
        current_aqi = None
        if nearest_station:
            latest_reading = db.query(AirQualityReading).filter(
                AirQualityReading.station_id == nearest_station.id
            ).order_by(AirQualityReading.timestamp.desc()).first()
            
            if latest_reading:
                current_aqi = {
                    "aqi": latest_reading.aqi,
                    "category": latest_reading.aqi_category,
                    "health_impact": get_health_impact(latest_reading.aqi),
                    "recommendations": get_aqi_recommendations(latest_reading.aqi)
                }
        
        # Get nearby waste collection schedule
        nearby_bins = db.query(WasteBin).filter(
            WasteBin.is_active == True
        ).limit(5).all()  # Simplified - would filter by actual proximity
        
        return {
            "citizen_dashboard": {
                "current_air_quality": current_aqi,
                "nearby_waste_bins": [
                    {
                        "name": bin.name,
                        "location": bin.location,
                        "fill_level": bin.current_fill_level,
                        "next_collection": "Today" if bin.needs_collection else "Tomorrow"
                    }
                    for bin in nearby_bins
                ],
                "health_tips": get_daily_health_tips(),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching citizen dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch citizen dashboard")

def get_health_impact(aqi):
    """Get health impact description based on AQI"""
    if aqi <= 50:
        return "Good air quality. No health impacts expected."
    elif aqi <= 100:
        return "Moderate air quality. Unusually sensitive people may experience respiratory symptoms."
    elif aqi <= 150:
        return "Unhealthy for sensitive groups. People with heart or lung disease may experience symptoms."
    elif aqi <= 200:
        return "Unhealthy. Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very unhealthy. Health warnings of emergency conditions."
    else:
        return "Hazardous. Health alert: everyone may experience more serious health effects."

def get_aqi_recommendations(aqi):
    """Get recommendations based on AQI level"""
    if aqi <= 50:
        return ["Enjoy outdoor activities", "Good time for outdoor exercise"]
    elif aqi <= 100:
        return ["Sensitive individuals should limit outdoor activities", "Consider indoor exercise"]
    elif aqi <= 150:
        return ["Limit outdoor activities", "Use air purifiers indoors", "Avoid strenuous exercise"]
    elif aqi <= 200:
        return ["Avoid outdoor activities", "Stay indoors with air purifiers", "Wear masks if going outside"]
    elif aqi <= 300:
        return ["Stay indoors", "Use air purifiers", "Avoid all outdoor activities"]
    else:
        return ["Emergency conditions - stay indoors", "Use air purifiers", "Consider evacuation if possible"]

def get_daily_health_tips():
    """Get daily health tips for citizens"""
    return [
        "Check air quality before outdoor activities",
        "Use public transport to reduce pollution",
        "Properly segregate waste for better recycling",
        "Stay hydrated to help your body cope with pollution",
        "Consider using air purifiers at home"
    ] 