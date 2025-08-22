"""
Smart Waste & Air Quality Management for Delhi
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Dict, Any
import os
from datetime import datetime, timedelta

# Import our modules
from api.routes import air_quality, waste_management, ai_insights, dashboard
from services.data_service import DataService
from services.ai_service import AIService
from utils.config import Settings
from utils.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Smart Waste & Air Quality Management System...")
    await init_db()
    logger.info("Database initialized successfully")
    
    # Initialize services
    app.state.data_service = DataService()
    app.state.ai_service = AIService()
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Smart Waste & Air Quality Management for Delhi",
    description="GenAI-powered platform for waste management and air quality monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(air_quality.router, prefix="/api/air-quality", tags=["Air Quality"])
app.include_router(waste_management.router, prefix="/api/waste", tags=["Waste Management"])
app.include_router(ai_insights.router, prefix="/api/ai", tags=["AI Insights"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Waste & Air Quality Management for Delhi",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "ai_service": "ready",
            "data_service": "ready"
        }
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        data_service = app.state.data_service
        stats = await data_service.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")

@app.post("/api/alert")
async def send_alert(background_tasks: BackgroundTasks, alert_data: Dict[str, Any]):
    """Send alert to citizens"""
    try:
        background_tasks.add_task(app.state.ai_service.send_alert, alert_data)
        return {"message": "Alert sent successfully"}
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to send alert")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 