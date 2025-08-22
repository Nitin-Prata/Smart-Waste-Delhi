import React, { useEffect, useState } from 'react';
import { TrendingUp, Trash2, Wind, AlertTriangle, Users } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface DashboardProps {
  sidebarCollapsed: boolean;
}

const METRIC_ICONS = [
  <Wind className="h-8 w-8 text-emerald-500" />,
  <Trash2 className="h-8 w-8 text-indigo-500" />,
  <AlertTriangle className="h-8 w-8 text-red-500" />,
  <Users className="h-8 w-8 text-yellow-500" />,
];

const API_BASE = "http://localhost:8000";

function downloadCSV(metrics) {
  const rows = [
    ['Metric', 'Value', 'Description'],
    ...metrics.map(m => [m.label, m.value, m.desc]),
  ];
  const csvContent = rows.map(e => e.join(",")).join("\n");
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'dashboard_report.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  toast.success('Report downloaded!');
}

const Dashboard: React.FC<DashboardProps> = ({ sidebarCollapsed }) => {
  const [metrics, setMetrics] = useState([
    { icon: METRIC_ICONS[0], label: 'Current AQI', value: '...', desc: 'Delhi average' },
    { icon: METRIC_ICONS[1], label: 'Bins Needing Collection', value: '...', desc: 'Out of 1200' },
    { icon: METRIC_ICONS[2], label: 'Active Alerts', value: '...', desc: 'Critical' },
    { icon: METRIC_ICONS[3], label: 'Citizens Online', value: '...', desc: 'Live' },
  ]);
  const [aqiData, setAqiData] = useState([]);
  const [wasteData, setWasteData] = useState([]);

  useEffect(() => {
    // Fetch dashboard overview metrics
  fetch(`${API_BASE}/api/dashboard/overview`)
      .then(res => res.json())
      .then(data => {
        if (data && data.overview) {
          setMetrics([
            { icon: METRIC_ICONS[0], label: 'Current AQI', value: data.overview.current_aqi, desc: 'Delhi average' },
            { icon: METRIC_ICONS[1], label: 'Bins Needing Collection', value: data.overview.bins_needing_collection, desc: `Out of ${data.overview.total_waste_bins}` },
            { icon: METRIC_ICONS[2], label: 'Active Alerts', value: data.overview.active_alerts, desc: 'Critical' },
            { icon: METRIC_ICONS[3], label: 'Citizens Online', value: '...', desc: 'Live' }, // Citizen count not in overview
          ]);
        }
      })
      .catch(() => toast.error('Failed to fetch dashboard metrics'));

    // Fetch dashboard trends for charts
  fetch(`${API_BASE}/api/dashboard/trends`)
      .then(res => res.json())
      .then(data => {
        if (data && data.trends) {
          // AQI chart
          const aqi = (data.trends.air_quality || []).map((d) => ({
            timestamp: d.timestamp,
            AQI: d.aqi
          }));
          setAqiData(aqi);
          // Waste chart
          const waste = (data.trends.waste_collection || []).map((d) => ({
            date: d.date,
            Collected: d.waste_collected
          }));
          setWasteData(waste);
        }
      })
      .catch(() => toast.error('Failed to fetch dashboard trends'));
  }, []);

  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-transparent bg-clip-text bg-gradient-to-r from-emerald-700 to-indigo-600 text-center w-full">
        Smart Waste Delhi Dashboard
      </h1>
      <div className="flex flex-wrap items-center justify-between mb-8 w-full max-w-6xl gap-4">
        <div className="flex gap-4">
          <span className="rounded-full px-4 py-1 bg-emerald-100 text-emerald-600 text-sm flex items-center">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse mr-2"></span>
            System Online
          </span>
        </div>
        <button
          className="px-4 py-1 rounded-full bg-emerald-600 text-white text-sm font-medium shadow hover:brightness-110 transition"
          onClick={() => downloadCSV(metrics)}
        >
          Download Report
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
        {metrics.map((m, i) => (
          <div key={i} className="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-start gap-2 hover:scale-[1.03] transition-transform">
            {m.icon}
            <div className="text-lg font-bold text-slate-900">{m.value}</div>
            <div className="text-sm text-slate-600">{m.label}</div>
            <div className="text-xs text-slate-400">{m.desc}</div>
          </div>
        ))}
      </div>
      <div className="flex flex-col md:flex-row gap-8 mt-2 w-full justify-center items-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-start min-h-[350px] w-full md:w-[600px] xl:w-[700px]">
          <h2 className="text-2xl font-bold text-emerald-700 mb-4">AQI Trend</h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={aqiData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                <YAxis />
                <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
                <Line type="monotone" dataKey="AQI" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-start min-h-[350px] w-full md:w-[600px] xl:w-[700px]">
          <h2 className="text-2xl font-bold text-indigo-700 mb-4">Waste Collection</h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wasteData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                <YAxis />
                <Tooltip labelFormatter={(value) => new Date(value).toLocaleString()} />
                <Bar dataKey="Collected" fill="#6366f1" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;