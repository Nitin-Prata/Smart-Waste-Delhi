
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AQITrend {
  timestamp: string;
  aqi: number;
  pm25: number;
  pm10: number;
}

const AQIChart: React.FC = () => {
  const [data, setData] = useState<AQITrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/trends?days=7`);
        const json = await res.json();
        setData(json.trends.air_quality || []);
      } catch (err) {
        setError('Failed to load AQI data');
      }
      setLoading(false);
    };
    fetchTrends();
  }, []);

  if (loading) return <div>Loading AQI chart...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Delhi AQI Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
          <YAxis />
          <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
          <Line type="monotone" dataKey="aqi" stroke="#3b82f6" name="AQI" dot={false} />
          <Line type="monotone" dataKey="pm25" stroke="#ef4444" name="PM2.5" dot={false} />
          <Line type="monotone" dataKey="pm10" stroke="#f59e0b" name="PM10" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AQIChart;
