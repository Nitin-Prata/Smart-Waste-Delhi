
import React, { useEffect, useState } from 'react';
import { Wind, Thermometer, Eye, MapPin, TrendingUp, AlertCircle, Leaf, Activity } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import AQIChart from '../components/AQIChart.tsx';

interface AirQualityProps {
  sidebarCollapsed: boolean;
}

const getAQIStatus = (aqi: number) => {
  if (aqi <= 50) return { status: 'Good', color: 'emerald', bgColor: 'emerald-50', textColor: 'emerald-700' };
  if (aqi <= 100) return { status: 'Moderate', color: 'yellow', bgColor: 'yellow-50', textColor: 'yellow-700' };
  if (aqi <= 150) return { status: 'Unhealthy for Sensitive', color: 'orange', bgColor: 'orange-50', textColor: 'orange-700' };
  if (aqi <= 200) return { status: 'Unhealthy', color: 'red', bgColor: 'red-50', textColor: 'red-700' };
  if (aqi <= 300) return { status: 'Very Unhealthy', color: 'purple', bgColor: 'purple-50', textColor: 'purple-700' };
  return { status: 'Hazardous', color: 'red', bgColor: 'red-100', textColor: 'red-900' };
};

const getHealthRecommendations = (aqi: number) => {
  if (aqi <= 50) return [
    '🌟 Excellent air quality for all outdoor activities',
    '🏃‍♂️ Perfect time for jogging and exercise',
    '🪟 Open windows for fresh air ventilation'
  ];
  if (aqi <= 100) return [
    '⚠️ Acceptable air quality for most people',
    '😷 Sensitive individuals should limit prolonged outdoor exertion',
    '🏠 Consider air purifiers indoors'
  ];
  if (aqi <= 150) return [
    '🚨 Unhealthy for sensitive groups',
    '😷 Wear N95 masks when going outdoors',
    '🏠 Keep windows closed and use air purifiers',
    '👶 Limit outdoor activities for children and elderly'
  ];
  return [
    '🔴 Avoid all outdoor activities',
    '😷 Wear high-quality air masks (N95 or better)',
    '🏠 Stay indoors with air purification systems',
    '🚗 Avoid driving with windows down'
  ];
};

interface Station {
  id: number;
  name: string;
  aqi: number;
  aqi_category: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  pm25?: number;
  pm10?: number;
  no2?: number;
  so2?: number;
  co?: number;
  o3?: number;
}

const AirQuality: React.FC<AirQualityProps> = ({ sidebarCollapsed }) => {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);
  const [healthRecommendations, setHealthRecommendations] = useState<string[]>([]);
  const [averageAQI, setAverageAQI] = useState(0);
  const [pollutantData, setPollutantData] = useState([]);

  useEffect(() => {
    const fetchStations = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/real-time-map`);
        const data = await res.json();
        const stationsData = data.map_data?.air_quality_stations || [];
        setStations(stationsData);
        if (stationsData.length > 0) {
          const avgAQI = stationsData.reduce((sum: number, station: Station) => sum + station.aqi, 0) / stationsData.length;
          setAverageAQI(Math.round(avgAQI));
          setSelectedStation(stationsData[0]);
          setHealthRecommendations(getHealthRecommendations(avgAQI));
        }
      } catch (err) {
        // Demo data
        const demoStations = [
          { id: 1, name: 'Connaught Place', aqi: 168, aqi_category: 'Unhealthy', latitude: 28.6315, longitude: 77.2167, timestamp: new Date().toISOString(), pm25: 78, pm10: 120, no2: 45, so2: 12, co: 1.2, o3: 32 },
          { id: 2, name: 'India Gate', aqi: 145, aqi_category: 'Unhealthy for Sensitive', latitude: 28.6129, longitude: 77.2295, timestamp: new Date().toISOString(), pm25: 65, pm10: 98, no2: 38, so2: 8, co: 0.9, o3: 28 },
          { id: 3, name: 'Karol Bagh', aqi: 189, aqi_category: 'Unhealthy', latitude: 28.6519, longitude: 77.1909, timestamp: new Date().toISOString(), pm25: 89, pm10: 145, no2: 52, so2: 15, co: 1.5, o3: 41 },
          { id: 4, name: 'Lajpat Nagar', aqi: 156, aqi_category: 'Unhealthy', latitude: 28.5678, longitude: 77.2434, timestamp: new Date().toISOString(), pm25: 71, pm10: 108, no2: 42, so2: 11, co: 1.1, o3: 35 },
        ];
        setStations(demoStations);
        setAverageAQI(165);
        setSelectedStation(demoStations[0]);
        setHealthRecommendations(getHealthRecommendations(165));
        toast.error('Using demo data - API not available');
      }
      setLoading(false);
    };

    fetchStations();
  }, []);

  useEffect(() => {
    if (selectedStation) {
      setPollutantData([
        { pollutant: 'PM2.5', value: selectedStation.pm25 || 0, max: 100, unit: 'μg/m³' },
        { pollutant: 'PM10', value: selectedStation.pm10 || 0, max: 150, unit: 'μg/m³' },
        { pollutant: 'NO2', value: selectedStation.no2 || 0, max: 80, unit: 'μg/m³' },
        { pollutant: 'SO2', value: selectedStation.so2 || 0, max: 20, unit: 'μg/m³' },
        { pollutant: 'CO', value: selectedStation.co || 0, max: 4, unit: 'mg/m³' },
        { pollutant: 'O3', value: selectedStation.o3 || 0, max: 100, unit: 'μg/m³' },
      ]);
    }
  }, [selectedStation]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading air quality data...</p>
        </div>
      </div>
    );
  }

  const aqiStatus = getAQIStatus(averageAQI);

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className={`bg-gradient-to-r from-${aqiStatus.color}-500 via-blue-600 to-purple-600 rounded-3xl p-8 text-white shadow-2xl`}>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="mb-6 lg:mb-0">
            <h1 className="text-4xl lg:text-5xl font-bold mb-2 flex items-center">
              <Wind className="mr-4" />
              Air Quality Monitor
            </h1>
            <p className="text-xl opacity-90 mb-4">
              Real-time air quality data across Delhi NCR
            </p>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>{stations.length} Active Stations</span>
              </div>
              <div className="flex items-center space-x-2">
                <Thermometer className="w-4 h-4" />
                <span>Last Updated: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
          <div className="text-center lg:text-right">
            <div className="text-6xl font-bold mb-2">{averageAQI}</div>
            <div className={`text-lg font-semibold bg-white/20 px-4 py-2 rounded-full`}>
              {aqiStatus.status}
            </div>
            <div className="text-sm opacity-90 mt-2">Delhi Average AQI</div>
          </div>
        </div>
      </div>

      {/* Current Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* AQI Overview */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Eye className="mr-3 text-blue-600" />
            Live Air Quality Stations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stations.map((station) => {
              const status = getAQIStatus(station.aqi);
              return (
                <div
                  key={station.id}
                  onClick={() => setSelectedStation(station)}
                  className={`p-6 rounded-2xl cursor-pointer transition-all duration-300 border-2 ${
                    selectedStation?.id === station.id 
                      ? `border-${status.color}-500 shadow-lg transform scale-105` 
                      : 'border-gray-200 hover:border-blue-300'
                  } bg-gradient-to-br from-white to-gray-50`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-gray-900">{station.name}</h3>
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{station.latitude.toFixed(3)}, {station.longitude.toFixed(3)}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-gray-900">{station.aqi}</div>
                      <div className={`text-xs font-semibold px-2 py-1 rounded-full bg-${status.color}-100 text-${status.color}-700`}>
                        {status.status}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Updated: {new Date(station.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Health Recommendations */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Leaf className="mr-3 text-emerald-600" />
            Health Advisory
          </h2>
          <div className={`p-4 rounded-2xl bg-${aqiStatus.color}-50 border border-${aqiStatus.color}-200 mb-6`}>
            <div className="flex items-center mb-3">
              <AlertCircle className={`w-5 h-5 mr-2 text-${aqiStatus.color}-600`} />
              <span className={`font-bold text-${aqiStatus.color}-800`}>Current Status: {aqiStatus.status}</span>
            </div>
          </div>
          <div className="space-y-4">
            {healthRecommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-xl">
                <div className="text-lg">{rec.split(' ')[0]}</div>
                <div className="text-sm text-gray-700 flex-1">{rec.substring(rec.indexOf(' ') + 1)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Analysis */}
      {selectedStation && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Pollutant Breakdown */}
          <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Pollutant Analysis - {selectedStation.name}
            </h2>
            <div className="space-y-4">
              {pollutantData.map((pollutant: any) => (
                <div key={pollutant.pollutant} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-700">{pollutant.pollutant}</span>
                    <span className="text-sm text-gray-500">
                      {pollutant.value} {pollutant.unit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full bg-gradient-to-r ${
                        pollutant.value / pollutant.max > 0.8 ? 'from-red-500 to-red-600' :
                        pollutant.value / pollutant.max > 0.6 ? 'from-orange-500 to-red-500' :
                        pollutant.value / pollutant.max > 0.4 ? 'from-yellow-500 to-orange-500' :
                        'from-emerald-500 to-teal-500'
                      } transition-all duration-500`}
                      style={{ width: `${Math.min((pollutant.value / pollutant.max) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AQI Chart */}
          <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <TrendingUp className="mr-3 text-blue-600" />
              7-Day AQI Trend
            </h2>
            <AQIChart />
          </div>
        </div>
      )}
    </div>
  );
};

export default AirQuality;
