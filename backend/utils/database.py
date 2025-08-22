"""
Database configuration and initialization
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import logging
from typing import Optional
import asyncio

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client: Optional[redis.Redis] = None

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL)
    return redis_client

async def init_db():
    """Initialize database"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize Redis
        redis_client = get_redis()
        redis_client.ping()
        logger.info("Redis connection established")
        
        # Load initial data if needed
        await load_initial_data()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def load_initial_data():
    """Load initial sample data"""
    try:
        from models.air_quality import AirQualityStation
        from models.waste_bin import WasteBin
        from services.data_service import DataService
        
        db = SessionLocal()
        data_service = DataService()
        
        # Check if data already exists
        station_count = db.query(AirQualityStation).count()
        bin_count = db.query(WasteBin).count()
        
        if station_count == 0:
            await data_service.load_sample_air_quality_stations(db)
            logger.info("Sample air quality stations loaded")
            
        if bin_count == 0:
            await data_service.load_sample_waste_bins(db)
            logger.info("Sample waste bins loaded")
            
        db.close()
        
    except Exception as e:
        logger.error(f"Error loading initial data: {e}")

def close_db():
    """Close database connections"""
    global redis_client
    if redis_client:
        redis_client.close()
    engine.dispose() 