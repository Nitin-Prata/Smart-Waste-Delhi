
import React, { useEffect, useState } from 'react';
import WasteChart from '../components/WasteChart.tsx';

interface WasteManagementProps {
  sidebarCollapsed: boolean;
}

const statusColors: Record<string, string> = {
  Full: 'bg-red-100 text-red-700',
  Partial: 'bg-yellow-100 text-yellow-700',
  Empty: 'bg-emerald-100 text-emerald-700',
  Poor: 'bg-red-100 text-red-700',
};

interface Bin {
  id: number;
  name: string;
  location: string;
  fill_level: number;
  needs_collection: boolean;
  priority: string;
  last_updated: string;
}

const WasteManagement: React.FC<WasteManagementProps> = ({ sidebarCollapsed }) => {
  const [bins, setBins] = useState<Bin[]>([]);
  const [loading, setLoading] = useState(true);
  const [routeSummary, setRouteSummary] = useState<string[]>([]);

  useEffect(() => {
    const fetchBins = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/real-time-map`);
        const data = await res.json();
        setBins(data.map_data.waste_bins || []);
      } catch (err) {
        setBins([]);
      }
      setLoading(false);
    };
    fetchBins();
  }, []);

  useEffect(() => {
    const fetchRouteSummary = async () => {
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/citizen-view`);
        const data = await res.json();
        setRouteSummary(data.citizen_dashboard.health_tips || []);
      } catch (err) {
        setRouteSummary([]);
      }
    };
    fetchRouteSummary();
  }, []);

  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-indigo-900 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi Waste Management
      </h1>
      <p className="mb-8 text-slate-600 text-center max-w-2xl">Monitor bin status, collection routes, and optimize waste management operations.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 w-full max-w-5xl">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-emerald-700 mb-2">Waste Collection Trend</h2>
          <WasteChart />
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-indigo-900 mb-2">Bin Status</h2>
          {loading ? (
            <div className="text-center text-slate-500 py-8">Loading bins...</div>
          ) : (
            <div className="space-y-4">
              {bins.map(bin => (
                <div key={bin.id} className="flex items-center gap-4 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[bin.priority] || 'bg-gray-200 text-gray-700'}`}>{bin.priority || (bin.needs_collection ? 'Full' : 'Empty')}</span>
                  <div className="flex-1">
                    <div className="font-medium text-slate-900">{bin.name} <span className="text-xs text-slate-500">({bin.location})</span></div>
                    <div className="text-xs text-slate-500">Fill Level: <span className="font-bold">{Math.round(bin.fill_level * 100)}%</span></div>
                  </div>
                  <div className="w-16 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div className={`h-3 rounded-full transition-all duration-700`} style={{ width: `${Math.round(bin.fill_level * 100)}%`, backgroundColor: bin.needs_collection ? '#ef4444' : '#10b981' }}></div>
                  </div>
                  <div className="text-xs text-slate-400">{new Date(bin.last_updated).toLocaleString()}</div>
                </div>
              ))}
              {bins.length === 0 && (
                <div className="text-center text-slate-500 py-8">No bins found.</div>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-md p-6 mt-8 w-full max-w-3xl">
        <h2 className="text-lg font-semibold text-emerald-700 mb-2">Collection Route Summary</h2>
        <ul className="list-disc pl-6 text-slate-700 space-y-2">
          {routeSummary.map((tip, idx) => (
            <li key={idx}>{tip}</li>
          ))}
          {routeSummary.length === 0 && (
            <li>No route summary available.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default WasteManagement;
