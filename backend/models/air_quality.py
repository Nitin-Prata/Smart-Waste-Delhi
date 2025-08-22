"""
Air Quality Data Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from utils.database import Base

class AirQualityStation(Base):
    """Air Quality Monitoring Station"""
    __tablename__ = "air_quality_stations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    station_type = Column(String(50), default="government")  # government, private, mobile
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    readings = relationship("AirQualityReading", back_populates="station")
    
    def __repr__(self):
        return f"<AirQualityStation(name='{self.name}', location='{self.location}')>"

class AirQualityReading(Base):
    """Air Quality Reading from a station"""
    __tablename__ = "air_quality_readings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String(36), ForeignKey("air_quality_stations.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    
    # Air Quality Parameters
    pm25 = Column(Float)  # Particulate Matter 2.5
    pm10 = Column(Float)  # Particulate Matter 10
    no2 = Column(Float)   # Nitrogen Dioxide
    so2 = Column(Float)   # Sulfur Dioxide
    co = Column(Float)    # Carbon Monoxide
    o3 = Column(Float)    # Ozone
    
    # Calculated AQI
    aqi = Column(Integer)
    aqi_category = Column(String(50))  # Good, Moderate, Unhealthy, etc.
    
    # Weather conditions
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    
    # Metadata
    source = Column(String(100), default="station")  # station, api, prediction
    confidence = Column(Float, default=1.0)  # Confidence in the reading
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    station = relationship("AirQualityStation", back_populates="readings")
    
    def __repr__(self):
        return f"<AirQualityReading(station='{self.station_id}', aqi={self.aqi}, timestamp='{self.timestamp}')>"

class AirQualityAlert(Base):
    """Air Quality Alerts"""
    __tablename__ = "air_quality_alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String(36), ForeignKey("air_quality_stations.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # warning, critical, emergency
    severity = Column(String(20), nullable=False)    # low, medium, high, critical
    message = Column(Text, nullable=False)
    aqi_threshold = Column(Integer, nullable=False)
    current_aqi = Column(Integer, nullable=False)
    
    # Alert status
    is_active = Column(Boolean, default=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    
    # Timing
    triggered_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    
    # Relationships
    station = relationship("AirQualityStation")
    
    def __repr__(self):
        return f"<AirQualityAlert(type='{self.alert_type}', severity='{self.severity}')>"

class AirQualityForecast(Base):
    """Air Quality Forecasts"""
    __tablename__ = "air_quality_forecasts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String(36), ForeignKey("air_quality_stations.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    forecast_hour = Column(Integer, nullable=False)  # 0-23
    
    # Predicted values
    predicted_aqi = Column(Integer, nullable=False)
    predicted_pm25 = Column(Float)
    predicted_pm10 = Column(Float)
    predicted_no2 = Column(Float)
    predicted_so2 = Column(Float)
    predicted_co = Column(Float)
    predicted_o3 = Column(Float)
    
    # Confidence intervals
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    
    # Model metadata
    model_version = Column(String(50), default="lstm_v1")
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    station = relationship("AirQualityStation")
    
    def __repr__(self):
        return f"<AirQualityForecast(station='{self.station_id}', date='{self.forecast_date}', aqi={self.predicted_aqi})>" 