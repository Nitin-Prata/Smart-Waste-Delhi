"""
Data Collection Script for Smart Waste & Air Quality Management
Fetches free public datasets for Delhi
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Collects data from various free public sources"""
    
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Delhi coordinates (approximate center)
        self.delhi_coords = {
            "latitude": 28.7041,
            "longitude": 77.1025,
            "radius": 50  # km radius around Delhi
        }
    
    def fetch_openaq_data(self, days: int = 30) -> pd.DataFrame:
        """
        Fetch air quality data from OpenAQ API (free)
        """
        logger.info("Fetching OpenAQ data for Delhi...")
        
        # OpenAQ API endpoint
        url = "https://api.openaq.org/v2/measurements"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "city": "Delhi",
            "limit": 1000,
            "order_by": "datetime",
            "sort": "desc",
            "date_from": start_date.strftime("%Y-%m-%d"),
            "date_to": end_date.strftime("%Y-%m-%d")
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.warning("No OpenAQ data found, generating synthetic data")
                return self._generate_synthetic_air_quality_data(days)
            
            # Process the data
            processed_data = []
            for result in results:
                processed_data.append({
                    "timestamp": result.get("date", {}).get("utc"),
                    "location": result.get("location"),
                    "parameter": result.get("parameter"),
                    "value": result.get("value"),
                    "unit": result.get("unit"),
                    "latitude": result.get("coordinates", {}).get("latitude"),
                    "longitude": result.get("coordinates", {}).get("longitude"),
                    "country": result.get("country"),
                    "city": result.get("city")
                })
            
            df = pd.DataFrame(processed_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Save to CSV
            filename = f"openaq_delhi_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False)
            logger.info(f"Saved OpenAQ data to {filepath}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OpenAQ data: {e}")
            logger.info("Generating synthetic air quality data instead")
            return self._generate_synthetic_air_quality_data(days)
    
    def _generate_synthetic_air_quality_data(self, days: int = 30) -> pd.DataFrame:
        """
        Generate realistic synthetic air quality data for Delhi
        """
        logger.info("Generating synthetic air quality data...")
        
        # Delhi air quality monitoring stations
        stations = [
            {"name": "Delhi Secretariat", "lat": 28.6139, "lon": 77.2090},
            {"name": "Anand Vihar", "lat": 28.6504, "lon": 77.3152},
            {"name": "Punjabi Bagh", "lat": 28.6692, "lon": 77.1197},
            {"name": "R K Puram", "lat": 28.5689, "lon": 77.1677},
            {"name": "Shadipur", "lat": 28.6517, "lon": 77.2219},
            {"name": "Dwarka", "lat": 28.5927, "lon": 77.0597},
            {"name": "Rohini", "lat": 28.7434, "lon": 77.0677},
            {"name": "Pitampura", "lat": 28.6991, "lon": 77.1197}
        ]
        
        # Generate data for each station
        all_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for station in stations:
            current_date = start_date
            
            while current_date <= end_date:
                # Generate hourly readings
                for hour in range(24):
                    timestamp = current_date + timedelta(hours=hour)
                    
                    # Base AQI values based on time of day and season
                    base_aqi = self._get_base_aqi(timestamp)
                    
                    # Add realistic variations
                    aqi = max(50, min(400, base_aqi + np.random.normal(0, 20)))
                    
                    # Calculate pollutant levels based on AQI
                    pm25 = aqi * 0.6 + np.random.normal(0, 5)
                    pm10 = aqi * 0.8 + np.random.normal(0, 8)
                    no2 = aqi * 0.3 + np.random.normal(0, 3)
                    so2 = aqi * 0.2 + np.random.normal(0, 2)
                    co = aqi * 0.1 + np.random.normal(0, 1)
                    o3 = max(0, aqi * 0.4 + np.random.normal(0, 5))
                    
                    # Weather conditions
                    temperature = 25 + np.random.normal(0, 5) + 10 * np.sin(2 * np.pi * hour / 24)
                    humidity = 60 + np.random.normal(0, 15)
                    wind_speed = np.random.uniform(0, 15)
                    wind_direction = np.random.uniform(0, 360)
                    
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
                    
                    all_data.append({
                        "timestamp": timestamp,
                        "station_name": station["name"],
                        "latitude": station["lat"],
                        "longitude": station["lon"],
                        "aqi": round(aqi, 1),
                        "aqi_category": category,
                        "pm25": round(pm25, 1),
                        "pm10": round(pm10, 1),
                        "no2": round(no2, 1),
                        "so2": round(so2, 1),
                        "co": round(co, 1),
                        "o3": round(o3, 1),
                        "temperature": round(temperature, 1),
                        "humidity": round(humidity, 1),
                        "wind_speed": round(wind_speed, 1),
                        "wind_direction": round(wind_direction, 1),
                        "source": "synthetic"
                    })
                
                current_date += timedelta(days=1)
        
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        filename = f"synthetic_air_quality_delhi_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved synthetic air quality data to {filepath}")
        
        return df
    
    def _get_base_aqi(self, timestamp: datetime) -> float:
        """
        Get base AQI value based on time and season
        """
        hour = timestamp.hour
        month = timestamp.month
        
        # Seasonal variations (winter months have higher pollution)
        if month in [11, 12, 1, 2]:  # Winter
            base = 180
        elif month in [3, 4, 5]:  # Spring
            base = 150
        elif month in [6, 7, 8, 9]:  # Monsoon
            base = 120
        else:  # Autumn
            base = 140
        
        # Diurnal variations (rush hours have higher pollution)
        if 6 <= hour <= 9:  # Morning rush
            base += 30
        elif 17 <= hour <= 20:  # Evening rush
            base += 40
        elif 22 <= hour or hour <= 5:  # Night
            base -= 20
        
        return base
    
    def generate_waste_management_data(self, days: int = 30) -> pd.DataFrame:
        """
        Generate synthetic waste management data for Delhi
        """
        logger.info("Generating synthetic waste management data...")
        
        # Delhi waste collection zones
        zones = [
            {"name": "Connaught Place", "lat": 28.6315, "lon": 77.2167, "population": 50000},
            {"name": "Khan Market", "lat": 28.6000, "lon": 77.2275, "population": 35000},
            {"name": "Lajpat Nagar", "lat": 28.5677, "lon": 77.2437, "population": 75000},
            {"name": "Saket", "lat": 28.5276, "lon": 77.2186, "population": 60000},
            {"name": "Dwarka", "lat": 28.5927, "lon": 77.0597, "population": 80000},
            {"name": "Rohini", "lat": 28.7434, "lon": 77.0677, "population": 90000},
            {"name": "Pitampura", "lat": 28.6991, "lon": 77.1197, "population": 70000},
            {"name": "Janakpuri", "lat": 28.6292, "lon": 77.0817, "population": 65000}
        ]
        
        # Generate waste bins for each zone
        all_bins = []
        bin_id_counter = 1
        
        for zone in zones:
            # Number of bins based on population
            num_bins = max(5, zone["population"] // 10000)
            
            for i in range(num_bins):
                # Distribute bins around the zone center
                lat_offset = np.random.uniform(-0.01, 0.01)
                lon_offset = np.random.uniform(-0.01, 0.01)
                
                bin_data = {
                    "bin_id": f"WB{bin_id_counter:03d}",
                    "name": f"{zone['name']} Bin {i+1}",
                    "location": f"{zone['name']}, Delhi",
                    "latitude": zone["lat"] + lat_offset,
                    "longitude": zone["lon"] + lon_offset,
                    "capacity": np.random.choice([500, 800, 1000, 1200, 1500]),
                    "bin_type": np.random.choice(["general", "recyclable", "organic"]),
                    "zone": zone["name"],
                    "population_density": zone["population"]
                }
                all_bins.append(bin_data)
                bin_id_counter += 1
        
        # Generate daily readings for each bin
        all_readings = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for bin_data in all_bins:
            current_date = start_date
            current_fill = np.random.uniform(0.1, 0.3)  # Start with some waste
            
            while current_date <= end_date:
                # Generate 4 readings per day (every 6 hours)
                for reading_hour in [0, 6, 12, 18]:
                    timestamp = current_date + timedelta(hours=reading_hour)
                    
                    # Simulate waste accumulation
                    # More waste during peak hours
                    if 8 <= reading_hour <= 10 or 18 <= reading_hour <= 20:
                        waste_increase = np.random.uniform(0.02, 0.05)
                    else:
                        waste_increase = np.random.uniform(0.005, 0.02)
                    
                    current_fill = min(1.0, current_fill + waste_increase)
                    
                    # Calculate weight based on fill level and capacity
                    weight = current_fill * bin_data["capacity"] * 0.8  # 0.8 kg/liter density
                    
                    # Other sensor readings
                    temperature = 25 + np.random.uniform(-3, 8)  # Waste can be warmer
                    humidity = 70 + np.random.uniform(-10, 10)
                    methane_level = current_fill * np.random.uniform(0, 40)
                    battery_level = max(0, 100 - np.random.uniform(0, 0.1))  # Gradual battery drain
                    signal_strength = 90 + np.random.uniform(-10, 5)
                    
                    # Determine if collection is needed
                    needs_collection = current_fill >= 0.8
                    collection_priority = "high" if current_fill >= 0.9 else "normal" if current_fill >= 0.8 else "low"
                    
                    reading = {
                        "timestamp": timestamp,
                        "bin_id": bin_data["bin_id"],
                        "bin_name": bin_data["name"],
                        "location": bin_data["location"],
                        "latitude": bin_data["latitude"],
                        "longitude": bin_data["longitude"],
                        "fill_level": round(current_fill, 3),
                        "weight": round(weight, 2),
                        "temperature": round(temperature, 1),
                        "humidity": round(humidity, 1),
                        "methane_level": round(methane_level, 1),
                        "battery_level": round(battery_level, 1),
                        "signal_strength": round(signal_strength, 1),
                        "needs_collection": needs_collection,
                        "collection_priority": collection_priority,
                        "capacity": bin_data["capacity"],
                        "bin_type": bin_data["bin_type"],
                        "zone": bin_data["zone"],
                        "source": "synthetic"
                    }
                    
                    all_readings.append(reading)
                
                # Reset fill level if collection occurred (simulate collection)
                if current_fill >= 0.9 and np.random.random() < 0.3:  # 30% chance of collection
                    current_fill = np.random.uniform(0.0, 0.1)
                
                current_date += timedelta(days=1)
        
        # Create DataFrames
        bins_df = pd.DataFrame(all_bins)
        readings_df = pd.DataFrame(all_readings)
        
        # Save to CSV
        bins_filename = f"waste_bins_delhi_{datetime.now().strftime('%Y%m%d')}.csv"
        readings_filename = f"waste_readings_delhi_{datetime.now().strftime('%Y%m%d')}.csv"
        
        bins_filepath = os.path.join(self.data_dir, bins_filename)
        readings_filepath = os.path.join(self.data_dir, readings_filename)
        
        bins_df.to_csv(bins_filepath, index=False)
        readings_df.to_csv(readings_filepath, index=False)
        
        logger.info(f"Saved waste bins data to {bins_filepath}")
        logger.info(f"Saved waste readings data to {readings_filepath}")
        
        return bins_df, readings_df
    
    def generate_weather_data(self, days: int = 30) -> pd.DataFrame:
        """
        Generate synthetic weather data for Delhi
        """
        logger.info("Generating synthetic weather data...")
        
        weather_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        current_date = start_date
        
        while current_date <= end_date:
            # Generate hourly weather data
            for hour in range(24):
                timestamp = current_date + timedelta(hours=hour)
                month = timestamp.month
                
                # Seasonal temperature variations
                if month in [11, 12, 1, 2]:  # Winter
                    base_temp = 15
                elif month in [3, 4, 5]:  # Spring
                    base_temp = 25
                elif month in [6, 7, 8, 9]:  # Monsoon
                    base_temp = 30
                else:  # Autumn
                    base_temp = 28
                
                # Diurnal temperature variations
                temp_variation = 10 * np.sin(2 * np.pi * (hour - 6) / 24)
                temperature = base_temp + temp_variation + np.random.normal(0, 2)
                
                # Humidity (higher during monsoon)
                if month in [6, 7, 8, 9]:
                    humidity = 80 + np.random.normal(0, 10)
                else:
                    humidity = 60 + np.random.normal(0, 15)
                humidity = max(20, min(100, humidity))
                
                # Wind speed and direction
                wind_speed = np.random.uniform(0, 15)
                wind_direction = np.random.uniform(0, 360)
                
                # Pressure
                pressure = 1013 + np.random.normal(0, 10)
                
                # Weather description
                if humidity > 80:
                    description = "Humid"
                elif temperature > 35:
                    description = "Hot"
                elif temperature < 10:
                    description = "Cold"
                else:
                    description = "Pleasant"
                
                weather_data.append({
                    "timestamp": timestamp,
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "wind_speed": round(wind_speed, 1),
                    "wind_direction": round(wind_direction, 1),
                    "pressure": round(pressure, 1),
                    "description": description,
                    "latitude": self.delhi_coords["latitude"],
                    "longitude": self.delhi_coords["longitude"]
                })
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(weather_data)
        
        # Save to CSV
        filename = f"weather_delhi_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved weather data to {filepath}")
        
        return df
    
    def create_sample_datasets(self):
        """
        Create all sample datasets for the project
        """
        logger.info("Creating sample datasets for Smart Delhi project...")
        
        # Generate all datasets
        air_quality_df = self.fetch_openaq_data(days=30)
        bins_df, readings_df = self.generate_waste_management_data(days=30)
        weather_df = self.generate_weather_data(days=30)
        
        # Create a summary file
        summary = {
            "generated_at": datetime.now().isoformat(),
            "datasets": {
                "air_quality": {
                    "filename": f"synthetic_air_quality_delhi_{datetime.now().strftime('%Y%m%d')}.csv",
                    "records": len(air_quality_df),
                    "stations": air_quality_df["station_name"].nunique(),
                    "date_range": f"{air_quality_df['timestamp'].min()} to {air_quality_df['timestamp'].max()}"
                },
                "waste_bins": {
                    "filename": f"waste_bins_delhi_{datetime.now().strftime('%Y%m%d')}.csv",
                    "records": len(bins_df),
                    "zones": bins_df["zone"].nunique()
                },
                "waste_readings": {
                    "filename": f"waste_readings_delhi_{datetime.now().strftime('%Y%m%d')}.csv",
                    "records": len(readings_df),
                    "bins": readings_df["bin_id"].nunique()
                },
                "weather": {
                    "filename": f"weather_delhi_{datetime.now().strftime('%Y%m%d')}.csv",
                    "records": len(weather_df),
                    "date_range": f"{weather_df['timestamp'].min()} to {weather_df['timestamp'].max()}"
                }
            }
        }
        
        # Save summary
        summary_filepath = os.path.join(self.data_dir, "dataset_summary.json")
        with open(summary_filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Dataset summary saved to {summary_filepath}")
        logger.info("All sample datasets created successfully!")
        
        return summary

def main():
    """Main function to run data collection"""
    collector = DataCollector()
    summary = collector.create_sample_datasets()
    
    print("\n" + "="*50)
    print("DATA COLLECTION COMPLETE")
    print("="*50)
    print(f"Generated {summary['datasets']['air_quality']['records']} air quality records")
    print(f"Generated {summary['datasets']['waste_bins']['records']} waste bins")
    print(f"Generated {summary['datasets']['waste_readings']['records']} waste readings")
    print(f"Generated {summary['datasets']['weather']['records']} weather records")
    print("="*50)

if __name__ == "__main__":
    main() 