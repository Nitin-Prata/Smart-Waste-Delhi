
import React, { useEffect, useState } from 'react';
import AQIChart from '../components/AQIChart.tsx';

interface AirQualityProps {
  sidebarCollapsed: boolean;
}

const statusColors: Record<string, string> = {
  Good: 'bg-emerald-100 text-emerald-700',
  Moderate: 'bg-yellow-100 text-yellow-700',
  Unhealthy: 'bg-red-100 text-red-700',
  Poor: 'bg-red-100 text-red-700',
  'Very Poor': 'bg-red-200 text-red-800',
  Hazardous: 'bg-red-300 text-red-900',
};

interface Station {
  id: number;
  name: string;
  aqi: number;
  aqi_category: string;
  latitude: number;
  longitude: number;
  timestamp: string;
}

const AirQuality: React.FC<AirQualityProps> = ({ sidebarCollapsed }) => {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [healthRecommendations, setHealthRecommendations] = useState<string[]>([]);

  useEffect(() => {
    const fetchStations = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/real-time-map`);
        const data = await res.json();
        setStations(data.map_data.air_quality_stations || []);
      } catch (err) {
        setStations([]);
      }
      setLoading(false);
    };
    fetchStations();
  }, []);

  useEffect(() => {
    const fetchHealthTips = async () => {
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/citizen-view`);
        const data = await res.json();
        setHealthRecommendations(data.citizen_dashboard.health_tips || []);
      } catch (err) {
        setHealthRecommendations([]);
      }
    };
    fetchHealthTips();
  }, []);

  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-emerald-700 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi Air Quality
      </h1>
      <p className="mb-8 text-slate-600 text-center max-w-2xl">Live AQI data, trends, and health insights for Delhi citizens and officials.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 w-full max-w-5xl">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-indigo-900 mb-2">AQI Trend</h2>
          <AQIChart />
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-emerald-700 mb-2">Monitoring Stations</h2>
          {loading ? (
            <div className="text-center text-slate-500 py-8">Loading stations...</div>
          ) : (
            <div className="space-y-4">
              {stations.map(station => (
                <div key={station.id} className="flex items-center gap-4 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[station.aqi_category] || 'bg-gray-200 text-gray-700'}`}>{station.aqi_category}</span>
                  <div className="flex-1">
                    <div className="font-medium text-slate-900">{station.name}</div>
                    <div className="text-xs text-slate-500">AQI: {station.aqi}</div>
                  </div>
                  <div className="text-xs text-slate-400">{new Date(station.timestamp).toLocaleString()}</div>
                </div>
              ))}
              {stations.length === 0 && (
                <div className="text-center text-slate-500 py-8">No active stations found.</div>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-md p-6 mt-8 w-full max-w-3xl">
        <h2 className="text-lg font-semibold text-indigo-700 mb-2">Health Recommendations</h2>
        <ul className="list-disc pl-6 text-slate-700 space-y-2">
          {healthRecommendations.map((tip, idx) => (
            <li key={idx}>{tip}</li>
          ))}
          {healthRecommendations.length === 0 && (
            <li>No health tips available.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default AirQuality;
