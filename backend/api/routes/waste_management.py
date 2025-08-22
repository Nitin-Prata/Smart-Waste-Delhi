"""
Waste Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from utils.database import get_db
from models.waste_bin import (
    WasteBin, WasteBinReading, WasteCollection, 
    CollectionRoute, RouteBin, WastePrediction
)
from services.ai_service import AIService
from services.data_service import DataService

router = APIRouter()
logger = logging.getLogger(__name__)

# Waste prediction endpoint
@router.post("/predict")
async def predict_waste_fill_level(
    input_data: Dict[str, Any] = Body(...)
):
    """Predict waste bin fill level using trained model"""
    try:
        import joblib
        import pandas as pd
        # Load the trained model
        model = joblib.load("models/waste_best_model_Random_Forest.joblib")
        # Prepare input data as DataFrame
        df = pd.DataFrame([input_data])
        # Predict
        prediction = model.predict(df)[0]
        return {"predicted_fill_level": float(prediction)}
    except Exception as e:
        logger.error(f"Error in waste fill level prediction: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@router.get("/bins")
async def get_waste_bins(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Return only active bins"),
    needs_collection: Optional[bool] = Query(None, description="Filter by collection need")
):
    """Get all waste bins"""
    try:
        query = db.query(WasteBin)
        
        if active_only:
            query = query.filter(WasteBin.is_active == True)
        
        if needs_collection is not None:
            query = query.filter(WasteBin.needs_collection == needs_collection)
        
        bins = query.all()
        
        return {
            "bins": [
                {
                    "id": bin.id,
                    "bin_id": bin.bin_id,
                    "name": bin.name,
                    "location": bin.location,
                    "latitude": bin.latitude,
                    "longitude": bin.longitude,
                    "capacity": bin.capacity,
                    "bin_type": bin.bin_type,
                    "current_fill_level": bin.current_fill_level,
                    "needs_collection": bin.needs_collection,
                    "collection_priority": bin.collection_priority,
                    "sensor_status": bin.sensor_status,
                    "last_updated": bin.last_updated
                }
                for bin in bins
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching waste bins: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bins")

@router.get("/bins/{bin_id}")
async def get_bin_details(
    bin_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific waste bin"""
    try:
        bin = db.query(WasteBin).filter(WasteBin.id == bin_id).first()
        if not bin:
            raise HTTPException(status_code=404, detail="Bin not found")
        
        # Get recent readings
        recent_readings = db.query(WasteBinReading).filter(
            WasteBinReading.bin_id == bin_id
        ).order_by(WasteBinReading.timestamp.desc()).limit(10).all()
        
        # Get recent collections
        recent_collections = db.query(WasteCollection).filter(
            WasteCollection.bin_id == bin_id
        ).order_by(WasteCollection.collection_date.desc()).limit(5).all()
        
        return {
            "bin": {
                "id": bin.id,
                "bin_id": bin.bin_id,
                "name": bin.name,
                "location": bin.location,
                "latitude": bin.latitude,
                "longitude": bin.longitude,
                "capacity": bin.capacity,
                "bin_type": bin.bin_type,
                "current_fill_level": bin.current_fill_level,
                "needs_collection": bin.needs_collection,
                "collection_priority": bin.collection_priority,
                "sensor_status": bin.sensor_status,
                "installation_date": bin.installation_date,
                "last_updated": bin.last_updated
            },
            "recent_readings": [
                {
                    "timestamp": reading.timestamp,
                    "fill_level": reading.fill_level,
                    "weight": reading.weight,
                    "temperature": reading.temperature,
                    "humidity": reading.humidity,
                    "battery_level": reading.battery_level
                }
                for reading in recent_readings
            ],
            "recent_collections": [
                {
                    "collection_date": collection.collection_date,
                    "waste_collected": collection.waste_collected,
                    "fill_level_before": collection.fill_level_before,
                    "fill_level_after": collection.fill_level_after,
                    "status": collection.status
                }
                for collection in recent_collections
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bin details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bin details")

@router.get("/bins/{bin_id}/readings")
async def get_bin_readings(
    bin_id: str,
    start_time: Optional[datetime] = Query(None, description="Start time for readings"),
    end_time: Optional[datetime] = Query(None, description="End time for readings"),
    limit: int = Query(100, description="Number of readings to return"),
    db: Session = Depends(get_db)
):
    """Get sensor readings for a specific waste bin"""
    try:
        query = db.query(WasteBinReading).filter(WasteBinReading.bin_id == bin_id)
        
        if start_time:
            query = query.filter(WasteBinReading.timestamp >= start_time)
        
        if end_time:
            query = query.filter(WasteBinReading.timestamp <= end_time)
        
        readings = query.order_by(WasteBinReading.timestamp.desc()).limit(limit).all()
        
        return {
            "readings": [
                {
                    "id": reading.id,
                    "timestamp": reading.timestamp,
                    "fill_level": reading.fill_level,
                    "weight": reading.weight,
                    "temperature": reading.temperature,
                    "humidity": reading.humidity,
                    "methane_level": reading.methane_level,
                    "battery_level": reading.battery_level,
                    "signal_strength": reading.signal_strength,
                    "reading_quality": reading.reading_quality
                }
                for reading in readings
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching bin readings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch readings")

@router.post("/bins/{bin_id}/readings")
async def add_bin_reading(
    bin_id: str,
    reading_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Add a new sensor reading for a waste bin"""
    try:
        # Check if bin exists
        bin = db.query(WasteBin).filter(WasteBin.id == bin_id).first()
        if not bin:
            raise HTTPException(status_code=404, detail="Bin not found")
        
        # Create new reading
        reading = WasteBinReading(
            bin_id=bin_id,
            fill_level=reading_data.get("fill_level", 0.0),
            weight=reading_data.get("weight"),
            temperature=reading_data.get("temperature"),
            humidity=reading_data.get("humidity"),
            methane_level=reading_data.get("methane_level"),
            battery_level=reading_data.get("battery_level"),
            signal_strength=reading_data.get("signal_strength"),
            sensor_id=reading_data.get("sensor_id"),
            reading_quality=reading_data.get("reading_quality", "good")
        )
        
        db.add(reading)
        
        # Update bin's current fill level
        bin.current_fill_level = reading_data.get("fill_level", bin.current_fill_level)
        bin.last_updated = datetime.now()
        
        # Check if collection is needed
        if bin.current_fill_level >= 0.8:  # 80% threshold
            bin.needs_collection = True
            bin.collection_priority = "high" if bin.current_fill_level >= 0.9 else "normal"
        
        db.commit()
        
        return {"message": "Reading added successfully", "reading_id": reading.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding bin reading: {e}")
        raise HTTPException(status_code=500, detail="Failed to add reading")

@router.get("/routes")
async def get_collection_routes(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Return only active routes")
):
    """Get all collection routes"""
    try:
        query = db.query(CollectionRoute)
        
        if active_only:
            query = query.filter(CollectionRoute.is_active == True)
        
        routes = query.all()
        
        return {
            "routes": [
                {
                    "id": route.id,
                    "route_name": route.route_name,
                    "route_type": route.route_type,
                    "start_location": route.start_location,
                    "end_location": route.end_location,
                    "estimated_duration": route.estimated_duration,
                    "total_distance": route.total_distance,
                    "optimization_score": route.optimization_score,
                    "scheduled_time": route.scheduled_time,
                    "is_active": route.is_active
                }
                for route in routes
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching collection routes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch routes")

@router.post("/routes/optimize")
async def optimize_collection_route(
    bin_ids: List[str] = Body(...),
    db: Session = Depends(get_db)
):
    """Optimize collection route for given bins"""
    try:
        ai_service = AIService()
        optimized_route = await ai_service.optimize_waste_collection_route(bin_ids, db)
        
        return {
            "optimized_route": optimized_route,
            "message": "Route optimized successfully"
        }
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize route")

@router.get("/collections")
async def get_waste_collections(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by collection status"),
    start_date: Optional[datetime] = Query(None, description="Start date for collections"),
    end_date: Optional[datetime] = Query(None, description="End date for collections")
):
    """Get waste collection records"""
    try:
        query = db.query(WasteCollection)
        
        if status:
            query = query.filter(WasteCollection.status == status)
        
        if start_date:
            query = query.filter(WasteCollection.collection_date >= start_date)
        
        if end_date:
            query = query.filter(WasteCollection.collection_date <= end_date)
        
        collections = query.order_by(WasteCollection.collection_date.desc()).all()
        
        return {
            "collections": [
                {
                    "id": collection.id,
                    "bin_id": collection.bin_id,
                    "route_id": collection.route_id,
                    "collection_date": collection.collection_date,
                    "collected_by": collection.collected_by,
                    "vehicle_id": collection.vehicle_id,
                    "waste_collected": collection.waste_collected,
                    "fill_level_before": collection.fill_level_before,
                    "fill_level_after": collection.fill_level_after,
                    "collection_duration": collection.collection_duration,
                    "status": collection.status,
                    "notes": collection.notes
                }
                for collection in collections
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching waste collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collections")

@router.post("/collections")
async def create_collection_record(
    collection_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new waste collection record"""
    try:
        collection = WasteCollection(
            bin_id=collection_data["bin_id"],
            route_id=collection_data.get("route_id"),
            collected_by=collection_data.get("collected_by"),
            vehicle_id=collection_data.get("vehicle_id"),
            waste_collected=collection_data.get("waste_collected"),
            fill_level_before=collection_data.get("fill_level_before"),
            fill_level_after=collection_data.get("fill_level_after"),
            collection_duration=collection_data.get("collection_duration"),
            status=collection_data.get("status", "completed"),
            notes=collection_data.get("notes")
        )
        
        db.add(collection)
        
        # Update bin status
        bin = db.query(WasteBin).filter(WasteBin.id == collection_data["bin_id"]).first()
        if bin:
            bin.needs_collection = False
            bin.collection_priority = "normal"
            bin.current_fill_level = collection_data.get("fill_level_after", 0.0)
        
        db.commit()
        
        return {"message": "Collection record created successfully", "collection_id": collection.id}
    except Exception as e:
        logger.error(f"Error creating collection record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create collection record")

@router.get("/predictions")
async def get_waste_predictions(
    bin_id: Optional[str] = Query(None, description="Filter by bin ID"),
    db: Session = Depends(get_db)
):
    """Get waste generation predictions"""
    try:
        query = db.query(WastePrediction)
        
        if bin_id:
            query = query.filter(WastePrediction.bin_id == bin_id)
        
        predictions = query.order_by(WastePrediction.prediction_date.desc()).all()
        
        return {
            "predictions": [
                {
                    "id": prediction.id,
                    "bin_id": prediction.bin_id,
                    "prediction_date": prediction.prediction_date,
                    "predicted_fill_level": prediction.predicted_fill_level,
                    "predicted_weight": prediction.predicted_weight,
                    "collection_needed": prediction.collection_needed,
                    "model_version": prediction.model_version,
                    "confidence_score": prediction.confidence_score
                }
                for prediction in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching waste predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch predictions")

@router.get("/summary")
async def get_waste_management_summary(
    db: Session = Depends(get_db)
):
    """Get waste management summary statistics"""
    try:
        # Get total bins
        total_bins = db.query(WasteBin).filter(WasteBin.is_active == True).count()
        
        # Get bins needing collection
        bins_needing_collection = db.query(WasteBin).filter(
            WasteBin.needs_collection == True,
            WasteBin.is_active == True
        ).count()
        
        # Get today's collections
        today = datetime.now().date()
        today_collections = db.query(WasteCollection).filter(
            WasteCollection.collection_date >= today
        ).count()
        
        # Get total waste collected today
        total_waste_today = db.query(WasteCollection).filter(
            WasteCollection.collection_date >= today,
            WasteCollection.waste_collected.isnot(None)
        ).with_entities(db.func.sum(WasteCollection.waste_collected)).scalar() or 0
        
        # Get fill level distribution
        bins = db.query(WasteBin).filter(WasteBin.is_active == True).all()
        fill_levels = {
            "empty": 0,      # 0-25%
            "low": 0,        # 25-50%
            "medium": 0,     # 50-75%
            "high": 0,       # 75-90%
            "full": 0        # 90-100%
        }
        
        for bin in bins:
            if bin.current_fill_level <= 0.25:
                fill_levels["empty"] += 1
            elif bin.current_fill_level <= 0.5:
                fill_levels["low"] += 1
            elif bin.current_fill_level <= 0.75:
                fill_levels["medium"] += 1
            elif bin.current_fill_level <= 0.9:
                fill_levels["high"] += 1
            else:
                fill_levels["full"] += 1
        
        return {
            "summary": {
                "total_bins": total_bins,
                "bins_needing_collection": bins_needing_collection,
                "today_collections": today_collections,
                "total_waste_today_kg": round(total_waste_today, 2),
                "fill_level_distribution": fill_levels
            }
        }
    except Exception as e:
        logger.error(f"Error fetching waste management summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch summary") 