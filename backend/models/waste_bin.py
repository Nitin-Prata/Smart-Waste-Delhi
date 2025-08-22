"""
Waste Management Data Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from utils.database import Base

class WasteBin(Base):
    """Waste Bin with IoT sensors"""
    __tablename__ = "waste_bins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bin_id = Column(String(50), unique=True, nullable=False)  # Physical bin identifier
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Bin specifications
    capacity = Column(Float, nullable=False)  # in liters
    bin_type = Column(String(50), default="general")  # general, recyclable, organic, hazardous
    installation_date = Column(DateTime, default=func.now())
    
    # IoT sensor data
    current_fill_level = Column(Float, default=0.0)  # 0.0 to 1.0
    last_updated = Column(DateTime, default=func.now())
    sensor_status = Column(String(20), default="active")  # active, inactive, error
    
    # Status
    is_active = Column(Boolean, default=True)
    needs_collection = Column(Boolean, default=False)
    collection_priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    readings = relationship("WasteBinReading", back_populates="bin")
    collections = relationship("WasteCollection", back_populates="bin")
    
    def __repr__(self):
        return f"<WasteBin(bin_id='{self.bin_id}', location='{self.location}', fill_level={self.current_fill_level})>"

class WasteBinReading(Base):
    """Waste Bin Sensor Readings"""
    __tablename__ = "waste_bin_readings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bin_id = Column(String(36), ForeignKey("waste_bins.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    
    # Sensor readings
    fill_level = Column(Float, nullable=False)  # 0.0 to 1.0
    weight = Column(Float)  # in kg
    temperature = Column(Float)  # in Celsius
    humidity = Column(Float)  # percentage
    
    # Additional sensors
    methane_level = Column(Float)  # for organic waste
    battery_level = Column(Float)  # sensor battery percentage
    signal_strength = Column(Float)  # IoT signal strength
    
    # Metadata
    sensor_id = Column(String(50))
    reading_quality = Column(String(20), default="good")  # good, poor, error
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    bin = relationship("WasteBin", back_populates="readings")
    
    def __repr__(self):
        return f"<WasteBinReading(bin='{self.bin_id}', fill_level={self.fill_level}, timestamp='{self.timestamp}')>"

class WasteCollection(Base):
    """Waste Collection Records"""
    __tablename__ = "waste_collections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bin_id = Column(String(36), ForeignKey("waste_bins.id"), nullable=False)
    route_id = Column(String(36), ForeignKey("collection_routes.id"))
    
    # Collection details
    collection_date = Column(DateTime, nullable=False, default=func.now())
    collected_by = Column(String(100))
    vehicle_id = Column(String(50))
    
    # Collection metrics
    waste_collected = Column(Float)  # in kg
    fill_level_before = Column(Float)
    fill_level_after = Column(Float)
    collection_duration = Column(Integer)  # in minutes
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    bin = relationship("WasteBin", back_populates="collections")
    route = relationship("CollectionRoute", back_populates="collections")
    
    def __repr__(self):
        return f"<WasteCollection(bin='{self.bin_id}', date='{self.collection_date}', status='{self.status}')>"

class CollectionRoute(Base):
    """Waste Collection Routes"""
    __tablename__ = "collection_routes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_name = Column(String(255), nullable=False)
    route_type = Column(String(50), default="daily")  # daily, weekly, on_demand
    
    # Route details
    start_location = Column(String(255))
    end_location = Column(String(255))
    estimated_duration = Column(Integer)  # in minutes
    total_distance = Column(Float)  # in km
    
    # Route optimization
    optimized_sequence = Column(JSON)  # List of bin IDs in optimal order
    optimization_score = Column(Float)  # Efficiency score
    
    # Schedule
    scheduled_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    collections = relationship("WasteCollection", back_populates="route")
    bins = relationship("RouteBin", back_populates="route")
    
    def __repr__(self):
        return f"<CollectionRoute(name='{self.route_name}', type='{self.route_type}')>"

class RouteBin(Base):
    """Bins assigned to collection routes"""
    __tablename__ = "route_bins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id = Column(String(36), ForeignKey("collection_routes.id"), nullable=False)
    bin_id = Column(String(36), ForeignKey("waste_bins.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)  # Order in the route
    
    # Collection preferences
    preferred_time = Column(String(10))  # HH:MM format
    collection_frequency = Column(String(20), default="daily")  # daily, weekly, biweekly
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    route = relationship("CollectionRoute", back_populates="bins")
    bin = relationship("WasteBin")
    
    def __repr__(self):
        return f"<RouteBin(route='{self.route_id}', bin='{self.bin_id}', order={self.sequence_order})>"

class WastePrediction(Base):
    """Waste Generation Predictions"""
    __tablename__ = "waste_predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bin_id = Column(String(36), ForeignKey("waste_bins.id"), nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    
    # Predicted values
    predicted_fill_level = Column(Float, nullable=False)
    predicted_weight = Column(Float)
    collection_needed = Column(Boolean, default=False)
    
    # Model metadata
    model_version = Column(String(50), default="rf_v1")
    confidence_score = Column(Float, default=1.0)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    bin = relationship("WasteBin")
    
    def __repr__(self):
        return f"<WastePrediction(bin='{self.bin_id}', date='{self.prediction_date}', fill_level={self.predicted_fill_level})>" 