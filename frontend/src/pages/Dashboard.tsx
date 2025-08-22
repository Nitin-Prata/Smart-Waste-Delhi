import React, { useEffect, useState } from 'react';
import { TrendingUp, Trash2, Wind, AlertTriangle, Users, Download, Zap, Eye, BarChart3 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area } from 'recharts';

interface DashboardProps {
  sidebarCollapsed: boolean;
}

const API_BASE = "http://localhost:8000";

function downloadCSV(metrics: any[]) {
  const rows = [
    ['Metric', 'Value', 'Description'],
    ...metrics.map(m => [m.label, m.value, m.desc]),
  ];
  const csvContent = rows.map(e => e.join(",")).join("\n");
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'smart_delhi_report.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  toast.success('📊 Dashboard Report Downloaded!');
}

const Dashboard: React.FC<DashboardProps> = ({ sidebarCollapsed }) => {
  const [metrics, setMetrics] = useState([
    { 
      icon: Wind, 
      label: 'Current AQI', 
      value: '...', 
      desc: 'Delhi average',
      trend: '+5%',
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'from-blue-50 to-cyan-50'
    },
    { 
      icon: Trash2, 
      label: 'Bins Need Collection', 
      value: '...', 
      desc: 'Out of 1200',
      trend: '-12%',
      color: 'from-emerald-500 to-teal-500',
      bgColor: 'from-emerald-50 to-teal-50'
    },
    { 
      icon: AlertTriangle, 
      label: 'Active Alerts', 
      value: '...', 
      desc: 'Critical',
      trend: '-8%',
      color: 'from-red-500 to-pink-500',
      bgColor: 'from-red-50 to-pink-50'
    },
    { 
      icon: Users, 
      label: 'Citizens Online', 
      value: '12.4k', 
      desc: 'Live users',
      trend: '+24%',
      color: 'from-purple-500 to-indigo-500',
      bgColor: 'from-purple-50 to-indigo-50'
    },
  ]);
  
  const [aqiData, setAqiData] = useState([]);
  const [wasteData, setWasteData] = useState([]);
  const [systemHealth, setSystemHealth] = useState(87);

  useEffect(() => {
    // Fetch dashboard overview metrics
    fetch(`${API_BASE}/api/dashboard/overview`)
      .then(res => res.json())
      .then(data => {
        if (data && data.overview) {
          setMetrics(prev => [
            { ...prev[0], value: data.overview.current_aqi || '168' },
            { ...prev[1], value: data.overview.bins_needing_collection || '47', desc: `Out of ${data.overview.total_waste_bins || 1200}` },
            { ...prev[2], value: data.overview.active_alerts || '3' },
            { ...prev[3], value: '12.4k' },
          ]);
        }
      })
      .catch(() => {
        // Use demo data
        setMetrics(prev => [
          { ...prev[0], value: '168' },
          { ...prev[1], value: '47' },
          { ...prev[2], value: '3' },
          { ...prev[3], value: '12.4k' },
        ]);
        toast.error('Using demo data - API not available');
      });

    // Fetch dashboard trends for charts
    fetch(`${API_BASE}/api/dashboard/trends`)
      .then(res => res.json())
      .then(data => {
        if (data && data.trends) {
          const aqi = (data.trends.air_quality || []).map((d: any) => ({
            timestamp: d.timestamp,
            AQI: d.aqi,
            Healthy: d.aqi < 100 ? d.aqi : 0,
            Moderate: d.aqi >= 100 && d.aqi < 200 ? d.aqi : 0,
            Unhealthy: d.aqi >= 200 ? d.aqi : 0,
          }));
          setAqiData(aqi);
          
          const waste = (data.trends.waste_collection || []).map((d: any) => ({
            date: d.date,
            Collected: d.waste_collected,
            Predicted: d.waste_collected * 1.1,
          }));
          setWasteData(waste);
        }
      })
      .catch(() => {
        // Use demo data
        const demoAQI = Array.from({ length: 7 }, (_, i) => ({
          timestamp: new Date(Date.now() - (6-i) * 24 * 60 * 60 * 1000).toISOString(),
          AQI: 120 + Math.random() * 80,
          Healthy: Math.random() * 50,
          Moderate: 50 + Math.random() * 100,
          Unhealthy: Math.random() * 50,
        }));
        
        const demoWaste = Array.from({ length: 7 }, (_, i) => ({
          date: new Date(Date.now() - (6-i) * 24 * 60 * 60 * 1000).toISOString(),
          Collected: 800 + Math.random() * 400,
          Predicted: 900 + Math.random() * 300,
        }));
        
        setAqiData(demoAQI);
        setWasteData(demoWaste);
      });
  }, []);

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="mb-6 lg:mb-0">
            <h1 className="text-4xl lg:text-5xl font-bold mb-2">
              Smart Delhi Dashboard
            </h1>
            <p className="text-xl opacity-90 mb-4">
              AI-Powered Waste & Air Quality Management System
            </p>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-emerald-300 rounded-full animate-pulse"></div>
                <span>Real-time Monitoring Active</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>System Health: {systemHealth}%</span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center lg:items-end space-y-4">
            <div className="text-right">
              <div className="text-3xl font-bold">Delhi NCR</div>
              <div className="text-lg opacity-90">28°C · Partly Cloudy</div>
            </div>
            <button
              onClick={() => downloadCSV(metrics)}
              className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl transition-all duration-200 backdrop-blur-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div
              key={index}
              className={`bg-gradient-to-br ${metric.bgColor} border border-white/50 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 group`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-r ${metric.color} shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  metric.trend.startsWith('+') ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                }`}>
                  {metric.trend}
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-gray-900 group-hover:scale-105 transition-transform">
                  {metric.value}
                </div>
                <div className="font-semibold text-gray-700">{metric.label}</div>
                <div className="text-sm text-gray-500">{metric.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AQI Trend Chart */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">Air Quality Index</h2>
              <p className="text-gray-600">7-day trend analysis</p>
            </div>
            <div className="flex items-center space-x-2 bg-blue-50 px-3 py-2 rounded-full">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span className="text-blue-700 font-semibold text-sm">Live Data</span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={aqiData}>
                <defs>
                  <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f9ff" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  stroke="#64748b"
                />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="AQI" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  fill="url(#aqiGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Waste Collection Chart */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">Waste Collection</h2>
              <p className="text-gray-600">Actual vs Predicted (tons)</p>
            </div>
            <div className="flex items-center space-x-2 bg-emerald-50 px-3 py-2 rounded-full">
              <Eye className="w-4 h-4 text-emerald-600" />
              <span className="text-emerald-700 font-semibold text-sm">AI Prediction</span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wasteData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  stroke="#64748b"
                />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  contentStyle={{
                    backgroundColor: '#065f46',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                />
                <Bar dataKey="Collected" fill="#10b981" radius={[8, 8, 0, 0]} name="Collected" />
                <Bar dataKey="Predicted" fill="#6ee7b7" radius={[8, 8, 0, 0]} name="AI Predicted" opacity={0.7} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">System Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="relative w-20 h-20 mx-auto mb-4">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle cx="40" cy="40" r="36" fill="none" stroke="#e5e7eb" strokeWidth="8"/>
                <circle 
                  cx="40" 
                  cy="40" 
                  r="36" 
                  fill="none" 
                  stroke="#10b981" 
                  strokeWidth="8"
                  strokeDasharray={`${systemHealth * 2.26} 226`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-900">{systemHealth}%</span>
              </div>
            </div>
            <p className="font-semibold text-gray-700">Overall Health</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">2.4s</div>
            <p className="font-semibold text-gray-700">Response Time</p>
            <p className="text-sm text-gray-500">Average API latency</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600 mb-2">99.8%</div>
            <p className="font-semibold text-gray-700">Uptime</p>
            <p className="text-sm text-gray-500">Last 30 days</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;