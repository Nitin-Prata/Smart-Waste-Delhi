
import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface WasteTrend {
  date: string;
  waste_collected: number;
  collection_duration: number;
}

const WasteChart: React.FC = () => {
  const [data, setData] = useState<WasteTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/trends?days=7`);
        const json = await res.json();
        setData(json.trends.waste_collection || []);
      } catch (err) {
        setError('Failed to load waste data');
      }
      setLoading(false);
    };
    fetchTrends();
  }, []);

  if (loading) return <div>Loading waste chart...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Waste Collection Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
          <YAxis />
          <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
          <Legend />
          <Bar dataKey="waste_collected" fill="#3b82f6" name="Waste Collected (kg)" />
          <Bar dataKey="collection_duration" fill="#10b981" name="Collection Duration (min)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WasteChart;
