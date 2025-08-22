"""
Seed demo data for Smart Waste Delhi backend (AQI, waste bins, alerts)
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import get_db
from models.air_quality import AirQualityStation, AirQualityReading, AirQualityAlert
from models.waste_bin import WasteBin, WasteCollection

# This script should be run from within a FastAPI shell or as a standalone script


def seed_demo_data(db: Session):
    # Add AQI stations
    stations = [
        AirQualityStation(name='Connaught Place', location='Connaught Place', latitude=28.6315, longitude=77.2167, is_active=True),
        AirQualityStation(name='Karol Bagh', location='Karol Bagh', latitude=28.6516, longitude=77.1906, is_active=True),
        AirQualityStation(name='South Delhi', location='South Delhi', latitude=28.5245, longitude=77.1855, is_active=True),
    ]
    db.add_all(stations)
    db.commit()

    # Add AQI readings for last 7 days
    for station in stations:
        for i in range(7):
            ts = datetime.now() - timedelta(days=i)
            aqi = 50 + i*20
            db.add(AirQualityReading(
                station_id=station.id,
                aqi=aqi,
                pm25=aqi*0.6,
                pm10=aqi*0.8,
                no2=aqi*0.2,
                so2=aqi*0.1,
                co=aqi*0.05,
                o3=aqi*0.03,
                timestamp=ts,
                aqi_category='Good' if aqi < 100 else 'Moderate' if aqi < 150 else 'Unhealthy',
                temperature=30.0,
                humidity=60.0,
                wind_speed=2.0,
                wind_direction=180.0,
                source='station',
                confidence=1.0
            ))
    db.commit()

    # Add waste bins
    bins = [
        WasteBin(bin_id='23', name='Bin #23', location='Karol Bagh', latitude=28.6516, longitude=77.1906, capacity=100.0, bin_type='general', current_fill_level=0.95, needs_collection=True, is_active=True, collection_priority='Full', last_updated=datetime.now()),
        WasteBin(bin_id='11', name='Bin #11', location='Connaught Place', latitude=28.6315, longitude=77.2167, capacity=100.0, bin_type='general', current_fill_level=0.6, needs_collection=False, is_active=True, collection_priority='Partial', last_updated=datetime.now()),
        WasteBin(bin_id='7', name='Bin #7', location='South Delhi', latitude=28.5245, longitude=77.1855, capacity=100.0, bin_type='general', current_fill_level=0.2, needs_collection=False, is_active=True, collection_priority='Empty', last_updated=datetime.now()),
    ]
    db.add_all(bins)
    db.commit()

    # Add waste collections for last 7 days
    for bin in bins:
        for i in range(7):
            ts = datetime.now() - timedelta(days=i)
            db.add(WasteCollection(
                bin_id=bin.id,
                collection_date=ts,
                waste_collected=100 + i*10,
                fill_level_before=bin.current_fill_level,
                fill_level_after=0.1,
                collection_duration=30 + i*5,
                status='completed'
            ))
    db.commit()

    # Add alerts
    db.add(AirQualityAlert(
        station_id=stations[0].id,
        alert_type='AQI',
        severity='critical',
        message='AQI exceeded safe levels in Connaught Place.',
        aqi_threshold=150,
        current_aqi=180,
        triggered_at=datetime.now()-timedelta(hours=2),
        is_active=True,
        acknowledged=False
    ))
    db.commit()

if __name__ == "__main__":
    import sys
    from .database import SessionLocal
    db = SessionLocal()
    seed_demo_data(db)
    db.close()
    print("Demo data seeded.")
