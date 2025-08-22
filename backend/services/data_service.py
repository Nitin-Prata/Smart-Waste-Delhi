"""
Data Service for Smart Waste & Air Quality Management
Handles external data sources, IoT sensors, and data processing
"""

import logging
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import random

from utils.config import settings
from models.air_quality import AirQualityStation, AirQualityReading
from models.waste_bin import WasteBin, WasteBinReading

logger = logging.getLogger(__name__)

class DataService:
    """Data Service for handling external data sources and IoT sensors"""
    
    def __init__(self):
        self.session = None
        self.iot_simulator_running = False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            return {
                "total_stations": 0,  # Would query database
                "total_bins": 0,      # Would query database
                "active_sensors": 0,   # Would query database
                "data_points_today": 0, # Would query database
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": "Failed to get system stats"}
    
    async def fetch_openaq_data(self, city: str = "Delhi", limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch air quality data from OpenAQ API"""
        try:
            url = f"{settings.OPENAQ_API_URL}/measurements"
            params = {
                "city": city,
                "limit": limit,
                "order_by": "datetime",
                "sort": "desc"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        logger.error(f"OpenAQ API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching OpenAQ data: {e}")
            return []
    
    async def fetch_cpcb_data(self, station_id: str) -> Optional[Dict[str, Any]]:
        """Fetch air quality data from Central Pollution Control Board"""
        try:
            # This would be the actual CPCB API endpoint
            url = f"{settings.CPCB_API_URL}/station/{station_id}/current"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"CPCB API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching CPCB data: {e}")
            return None
    
    async def load_sample_air_quality_stations(self, db: Session):
        """Load sample air quality monitoring stations"""
        try:
            # Sample Delhi air quality stations
            sample_stations = [
                {
                    "name": "Delhi Secretariat",
                    "location": "Delhi Secretariat, New Delhi",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "station_type": "government"
                },
                {
                    "name": "Anand Vihar",
                    "location": "Anand Vihar, Delhi",
                    "latitude": 28.6504,
                    "longitude": 77.3152,
                    "station_type": "government"
                },
                {
                    "name": "Punjabi Bagh",
                    "location": "Punjabi Bagh, Delhi",
                    "latitude": 28.6692,
                    "longitude": 77.1197,
                    "station_type": "government"
                },
                {
                    "name": "R K Puram",
                    "location": "R K Puram, New Delhi",
                    "latitude": 28.5689,
                    "longitude": 77.1677,
                    "station_type": "government"
                },
                {
                    "name": "Shadipur",
                    "location": "Shadipur, Delhi",
                    "latitude": 28.6517,
                    "longitude": 77.2219,
                    "station_type": "government"
                }
            ]
            
            for station_data in sample_stations:
                station = AirQualityStation(**station_data)
                db.add(station)
            
            db.commit()
            logger.info(f"Loaded {len(sample_stations)} sample air quality stations")
            
        except Exception as e:
            logger.error(f"Error loading sample air quality stations: {e}")
            db.rollback()
    
    async def load_sample_waste_bins(self, db: Session):
        """Load sample waste bins with IoT sensors"""
        try:
            # Sample waste bins across Delhi
            sample_bins = [
                {
                    "bin_id": "WB001",
                    "name": "Connaught Place Main",
                    "location": "Connaught Place, New Delhi",
                    "latitude": 28.6315,
                    "longitude": 77.2167,
                    "capacity": 1000,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB002",
                    "name": "Khan Market",
                    "location": "Khan Market, New Delhi",
                    "latitude": 28.6000,
                    "longitude": 77.2275,
                    "capacity": 800,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB003",
                    "name": "Lajpat Nagar",
                    "location": "Lajpat Nagar, Delhi",
                    "latitude": 28.5677,
                    "longitude": 77.2437,
                    "capacity": 1200,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB004",
                    "name": "Saket Mall",
                    "location": "Saket, Delhi",
                    "latitude": 28.5276,
                    "longitude": 77.2186,
                    "capacity": 1500,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB005",
                    "name": "Dwarka Sector 12",
                    "location": "Dwarka, Delhi",
                    "latitude": 28.5927,
                    "longitude": 77.0597,
                    "capacity": 1000,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB006",
                    "name": "Rohini Sector 3",
                    "location": "Rohini, Delhi",
                    "latitude": 28.7434,
                    "longitude": 77.0677,
                    "capacity": 900,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB007",
                    "name": "Pitampura",
                    "location": "Pitampura, Delhi",
                    "latitude": 28.6991,
                    "longitude": 77.1197,
                    "capacity": 1100,
                    "bin_type": "general"
                },
                {
                    "bin_id": "WB008",
                    "name": "Janakpuri",
                    "location": "Janakpuri, Delhi",
                    "latitude": 28.6292,
                    "longitude": 77.0817,
                    "capacity": 950,
                    "bin_type": "general"
                }
            ]
            
            for bin_data in sample_bins:
                bin = WasteBin(**bin_data)
                db.add(bin)
            
            db.commit()
            logger.info(f"Loaded {len(sample_bins)} sample waste bins")
            
        except Exception as e:
            logger.error(f"Error loading sample waste bins: {e}")
            db.rollback()
    
    async def generate_sample_air_quality_data(self, db: Session, hours: int = 24):
        """Generate sample air quality readings for demonstration"""
        try:
            stations = db.query(AirQualityStation).all()
            
            for station in stations:
                # Generate readings for the last N hours
                for i in range(hours):
                    timestamp = datetime.now() - timedelta(hours=i)
                    
                    # Generate realistic AQI values based on time of day
                    hour = timestamp.hour
                    if 6 <= hour <= 9:  # Morning rush
                        base_aqi = 150
                    elif 17 <= hour <= 20:  # Evening rush
                        base_aqi = 180
                    else:
                        base_aqi = 120
                    
                    # Add some randomness
                    aqi = max(50, min(300, base_aqi + random.randint(-30, 30)))
                    
                    # Calculate other parameters based on AQI
                    pm25 = aqi * 0.6 + random.randint(-10, 10)
                    pm10 = aqi * 0.8 + random.randint(-15, 15)
                    no2 = aqi * 0.3 + random.randint(-5, 5)
                    so2 = aqi * 0.2 + random.randint(-3, 3)
                    co = aqi * 0.1 + random.randint(-2, 2)
                    o3 = max(0, aqi * 0.4 + random.randint(-10, 10))
                    
                    # Weather conditions
                    temperature = 25 + random.randint(-5, 5)
                    humidity = 60 + random.randint(-20, 20)
                    wind_speed = random.uniform(0, 15)
                    wind_direction = random.uniform(0, 360)
                    
                    # Determine AQI category
                    if aqi <= 50:
                        category = "Good"
                    elif aqi <= 100:
                        category = "Moderate"
                    elif aqi <= 150:
                        category = "Unhealthy for Sensitive Groups"
                    elif aqi <= 200:
                        category = "Unhealthy"
                    elif aqi <= 300:
                        category = "Very Unhealthy"
                    else:
                        category = "Hazardous"
                    
                    reading = AirQualityReading(
                        station_id=station.id,
                        timestamp=timestamp,
                        pm25=pm25,
                        pm10=pm10,
                        no2=no2,
                        so2=so2,
                        co=co,
                        o3=o3,
                        aqi=aqi,
                        aqi_category=category,
                        temperature=temperature,
                        humidity=humidity,
                        wind_speed=wind_speed,
                        wind_direction=wind_direction,
                        source="simulated"
                    )
                    
                    db.add(reading)
            
            db.commit()
            logger.info(f"Generated sample air quality data for {len(stations)} stations")
            
        except Exception as e:
            logger.error(f"Error generating sample air quality data: {e}")
            db.rollback()
    
    async def generate_sample_waste_data(self, db: Session, days: int = 7):
        """Generate sample waste bin sensor data for demonstration"""
        try:
            bins = db.query(WasteBin).all()
            
            for bin in bins:
                # Generate readings for the last N days
                for day in range(days):
                    for hour in range(24):
                        timestamp = datetime.now() - timedelta(days=day, hours=hour)
                        
                        # Simulate waste accumulation over time
                        base_fill = 0.3 + (day * 0.1) + (hour * 0.02)
                        
                        # Add some randomness and daily patterns
                        if 8 <= hour <= 10 or 18 <= hour <= 20:  # Peak usage times
                            base_fill += 0.05
                        
                        fill_level = min(1.0, max(0.0, base_fill + random.uniform(-0.05, 0.05)))
                        
                        # Calculate weight based on fill level
                        weight = fill_level * bin.capacity * 0.8  # 0.8 kg/liter average density
                        
                        # Other sensor readings
                        temperature = 25 + random.uniform(-5, 10)  # Waste can be warmer
                        humidity = 70 + random.uniform(-20, 20)
                        methane_level = fill_level * random.uniform(0, 50)  # Higher for fuller bins
                        battery_level = 85 + random.uniform(-10, 5)
                        signal_strength = 90 + random.uniform(-15, 10)
                        
                        reading = WasteBinReading(
                            bin_id=bin.id,
                            timestamp=timestamp,
                            fill_level=fill_level,
                            weight=weight,
                            temperature=temperature,
                            humidity=humidity,
                            methane_level=methane_level,
                            battery_level=battery_level,
                            signal_strength=signal_strength,
                            sensor_id=f"sensor_{bin.bin_id}",
                            reading_quality="good"
                        )
                        
                        db.add(reading)
                        
                        # Update bin's current status
                        if timestamp > bin.last_updated:
                            bin.current_fill_level = fill_level
                            bin.last_updated = timestamp
                            bin.needs_collection = fill_level >= 0.8
                            bin.collection_priority = "high" if fill_level >= 0.9 else "normal"
            
            db.commit()
            logger.info(f"Generated sample waste data for {len(bins)} bins")
            
        except Exception as e:
            logger.error(f"Error generating sample waste data: {e}")
            db.rollback()
    
    async def start_iot_simulator(self, db: Session):
        """Start IoT sensor data simulator"""
        if self.iot_simulator_running:
            return
        
        self.iot_simulator_running = True
        logger.info("Starting IoT sensor simulator")
        
        try:
            while self.iot_simulator_running:
                # Simulate air quality sensor readings
                await self._simulate_air_quality_sensors(db)
                
                # Simulate waste bin sensor readings
                await self._simulate_waste_bin_sensors(db)
                
                # Wait for 5 minutes before next simulation
                await asyncio.sleep(300)
                
        except Exception as e:
            logger.error(f"Error in IoT simulator: {e}")
        finally:
            self.iot_simulator_running = False
    
    async def stop_iot_simulator(self):
        """Stop IoT sensor data simulator"""
        self.iot_simulator_running = False
        logger.info("Stopping IoT sensor simulator")
    
    async def _simulate_air_quality_sensors(self, db: Session):
        """Simulate air quality sensor readings"""
        try:
            stations = db.query(AirQualityStation).filter(AirQualityStation.is_active == True).all()
            
            for station in stations:
                # Get current conditions
                current_time = datetime.now()
                hour = current_time.hour
                
                # Base AQI based on time of day
                if 6 <= hour <= 9:  # Morning rush
                    base_aqi = 150
                elif 17 <= hour <= 20:  # Evening rush
                    base_aqi = 180
                elif 22 <= hour or hour <= 5:  # Night
                    base_aqi = 100
                else:
                    base_aqi = 120
                
                # Add realistic variations
                aqi = max(50, min(300, base_aqi + random.randint(-20, 20)))
                
                # Calculate other parameters
                pm25 = aqi * 0.6 + random.randint(-5, 5)
                pm10 = aqi * 0.8 + random.randint(-8, 8)
                no2 = aqi * 0.3 + random.randint(-3, 3)
                so2 = aqi * 0.2 + random.randint(-2, 2)
                co = aqi * 0.1 + random.randint(-1, 1)
                o3 = max(0, aqi * 0.4 + random.randint(-5, 5))
                
                # Weather conditions
                temperature = 25 + random.randint(-3, 3)
                humidity = 60 + random.randint(-10, 10)
                wind_speed = random.uniform(0, 12)
                wind_direction = random.uniform(0, 360)
                
                # Determine category
                if aqi <= 50:
                    category = "Good"
                elif aqi <= 100:
                    category = "Moderate"
                elif aqi <= 150:
                    category = "Unhealthy for Sensitive Groups"
                elif aqi <= 200:
                    category = "Unhealthy"
                elif aqi <= 300:
                    category = "Very Unhealthy"
                else:
                    category = "Hazardous"
                
                reading = AirQualityReading(
                    station_id=station.id,
                    timestamp=current_time,
                    pm25=pm25,
                    pm10=pm10,
                    no2=no2,
                    so2=so2,
                    co=co,
                    o3=o3,
                    aqi=aqi,
                    aqi_category=category,
                    temperature=temperature,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    wind_direction=wind_direction,
                    source="iot_sensor"
                )
                
                db.add(reading)
            
            db.commit()
            logger.debug(f"Simulated air quality readings for {len(stations)} stations")
            
        except Exception as e:
            logger.error(f"Error simulating air quality sensors: {e}")
            db.rollback()
    
    async def _simulate_waste_bin_sensors(self, db: Session):
        """Simulate waste bin sensor readings"""
        try:
            bins = db.query(WasteBin).filter(WasteBin.is_active == True).all()
            
            for bin in bins:
                current_time = datetime.now()
                hour = current_time.hour
                
                # Simulate waste accumulation
                current_fill = bin.current_fill_level
                
                # Add waste based on time of day
                if 8 <= hour <= 10 or 18 <= hour <= 20:  # Peak usage
                    waste_increase = random.uniform(0.01, 0.03)
                else:
                    waste_increase = random.uniform(0.001, 0.01)
                
                new_fill_level = min(1.0, current_fill + waste_increase)
                
                # Calculate weight
                weight = new_fill_level * bin.capacity * 0.8
                
                # Other sensor readings
                temperature = 25 + random.uniform(-3, 8)  # Waste can be warmer
                humidity = 70 + random.uniform(-10, 10)
                methane_level = new_fill_level * random.uniform(0, 40)
                battery_level = max(0, bin.readings[-1].battery_level - random.uniform(0, 0.1)) if bin.readings else 85
                signal_strength = 90 + random.uniform(-10, 5)
                
                reading = WasteBinReading(
                    bin_id=bin.id,
                    timestamp=current_time,
                    fill_level=new_fill_level,
                    weight=weight,
                    temperature=temperature,
                    humidity=humidity,
                    methane_level=methane_level,
                    battery_level=battery_level,
                    signal_strength=signal_strength,
                    sensor_id=f"sensor_{bin.bin_id}",
                    reading_quality="good"
                )
                
                db.add(reading)
                
                # Update bin status
                bin.current_fill_level = new_fill_level
                bin.last_updated = current_time
                bin.needs_collection = new_fill_level >= 0.8
                bin.collection_priority = "high" if new_fill_level >= 0.9 else "normal"
            
            db.commit()
            logger.debug(f"Simulated waste bin readings for {len(bins)} bins")
            
        except Exception as e:
            logger.error(f"Error simulating waste bin sensors: {e}")
            db.rollback()
    
    async def fetch_weather_data(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Fetch weather data for a location"""
        try:
            # This would use a weather API like OpenWeatherMap
            # For demo purposes, return simulated data
            return {
                "temperature": 25 + random.uniform(-5, 5),
                "humidity": 60 + random.uniform(-20, 20),
                "wind_speed": random.uniform(0, 15),
                "wind_direction": random.uniform(0, 360),
                "pressure": 1013 + random.uniform(-10, 10),
                "description": "Partly cloudy"
            }
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    async def process_external_data(self, data_source: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process external data from various sources"""
        try:
            if data_source == "openaq":
                return await self._process_openaq_data(data)
            elif data_source == "cpcb":
                return await self._process_cpcb_data(data)
            elif data_source == "weather":
                return await self._process_weather_data(data)
            else:
                return {"error": f"Unknown data source: {data_source}"}
                
        except Exception as e:
            logger.error(f"Error processing external data: {e}")
            return {"error": "Failed to process data"}
    
    async def _process_openaq_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAQ data"""
        try:
            results = data.get("results", [])
            processed_data = []
            
            for result in results:
                processed_data.append({
                    "location": result.get("location"),
                    "parameter": result.get("parameter"),
                    "value": result.get("value"),
                    "unit": result.get("unit"),
                    "timestamp": result.get("date", {}).get("utc"),
                    "latitude": result.get("coordinates", {}).get("latitude"),
                    "longitude": result.get("coordinates", {}).get("longitude")
                })
            
            return {
                "source": "openaq",
                "records_processed": len(processed_data),
                "data": processed_data
            }
            
        except Exception as e:
            logger.error(f"Error processing OpenAQ data: {e}")
            return {"error": "Failed to process OpenAQ data"}
    
    async def _process_cpcb_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process CPCB data"""
        try:
            # Process Central Pollution Control Board data
            return {
                "source": "cpcb",
                "records_processed": 1,
                "data": data
            }
        except Exception as e:
            logger.error(f"Error processing CPCB data: {e}")
            return {"error": "Failed to process CPCB data"}
    
    async def _process_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather data"""
        try:
            return {
                "source": "weather",
                "records_processed": 1,
                "data": data
            }
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return {"error": "Failed to process weather data"} 