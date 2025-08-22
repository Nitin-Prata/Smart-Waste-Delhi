
import React, { useEffect, useState } from 'react';
import { Trash2, MapPin, Route, Clock, TrendingUp, Zap, Truck, AlertTriangle, CheckCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import WasteChart from '../components/WasteChart.tsx';

interface WasteManagementProps {
  sidebarCollapsed: boolean;
}

const getFillStatus = (fillLevel: number) => {
  if (fillLevel <= 20) return { status: 'Empty', color: 'emerald', priority: 'low' };
  if (fillLevel <= 40) return { status: 'Low', color: 'yellow', priority: 'low' };
  if (fillLevel <= 70) return { status: 'Medium', color: 'orange', priority: 'medium' };
  if (fillLevel <= 90) return { status: 'High', color: 'red', priority: 'high' };
  return { status: 'Critical', color: 'red', priority: 'urgent' };
};

interface Bin {
  id: number;
  name: string;
  location: string;
  fill_level: number;
  needs_collection: boolean;
  priority: string;
  last_updated: string;
  latitude?: number;
  longitude?: number;
  bin_type?: string;
  capacity?: number;
}

const WasteManagement: React.FC<WasteManagementProps> = ({ sidebarCollapsed }) => {
  const [bins, setBins] = useState<Bin[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBin, setSelectedBin] = useState<Bin | null>(null);
  const [routeSummary, setRouteSummary] = useState<string[]>([]);
  const [statistics, setStatistics] = useState({
    totalBins: 1200,
    needingCollection: 47,
    routeOptimized: 12,
    efficiencyGain: 23
  });

  useEffect(() => {
    const fetchBins = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/real-time-map`);
        const data = await res.json();
        const binsData = data.map_data?.waste_bins || [];
        setBins(binsData);
        if (binsData.length > 0) {
          setSelectedBin(binsData[0]);
        }
      } catch (err) {
        // Demo data
        const demoBins = [
          { id: 1, name: 'CP-001', location: 'Connaught Place Metro', fill_level: 87, needs_collection: true, priority: 'high', last_updated: new Date().toISOString(), latitude: 28.6315, longitude: 77.2167, bin_type: 'Smart', capacity: 240 },
          { id: 2, name: 'IG-002', location: 'India Gate Parking', fill_level: 34, needs_collection: false, priority: 'low', last_updated: new Date().toISOString(), latitude: 28.6129, longitude: 77.2295, bin_type: 'Smart', capacity: 240 },
          { id: 3, name: 'KB-003', location: 'Karol Bagh Market', fill_level: 92, needs_collection: true, priority: 'urgent', last_updated: new Date().toISOString(), latitude: 28.6519, longitude: 77.1909, bin_type: 'Smart', capacity: 360 },
          { id: 4, name: 'LN-004', location: 'Lajpat Nagar Central', fill_level: 15, needs_collection: false, priority: 'low', last_updated: new Date().toISOString(), latitude: 28.5678, longitude: 77.2434, bin_type: 'Standard', capacity: 180 },
          { id: 5, name: 'CP-005', location: 'Central Park', fill_level: 76, needs_collection: true, priority: 'medium', last_updated: new Date().toISOString(), latitude: 28.6328, longitude: 77.2197, bin_type: 'Smart', capacity: 240 },
          { id: 6, name: 'DU-006', location: 'Delhi University', fill_level: 45, needs_collection: false, priority: 'low', last_updated: new Date().toISOString(), latitude: 28.6958, longitude: 77.2167, bin_type: 'Smart', capacity: 300 },
        ];
        setBins(demoBins);
        setSelectedBin(demoBins[0]);
        setStatistics({
          totalBins: 1200,
          needingCollection: demoBins.filter(b => b.needs_collection).length,
          routeOptimized: 12,
          efficiencyGain: 23
        });
        toast.error('Using demo data - API not available');
      }
      setLoading(false);
    };

    fetchBins();
    fetchRouteSummary();
  }, []);

  const fetchRouteSummary = async () => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/citizen-view`);
      const data = await res.json();
      setRouteSummary(data.route_summary || [
        '🚛 Optimized route reduces travel time by 23%',
        '⚡ AI algorithm processes 1200+ bins in real-time',
        '🌱 Reduced carbon emissions by 15% this month',
        '📊 99.2% collection efficiency achieved'
      ]);
    } catch (err) {
      setRouteSummary([
        '🚛 Optimized route reduces travel time by 23%',
        '⚡ AI algorithm processes 1200+ bins in real-time',
        '🌱 Reduced carbon emissions by 15% this month',
        '📊 99.2% collection efficiency achieved'
      ]);
    }
  };

  const fillLevelDistribution = [
    { name: '0-25%', value: bins.filter(b => b.fill_level <= 25).length, color: '#10b981' },
    { name: '26-50%', value: bins.filter(b => b.fill_level > 25 && b.fill_level <= 50).length, color: '#f59e0b' },
    { name: '51-75%', value: bins.filter(b => b.fill_level > 50 && b.fill_level <= 75).length, color: '#f97316' },
    { name: '76-100%', value: bins.filter(b => b.fill_level > 75).length, color: '#ef4444' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading waste management data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-blue-600 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="mb-6 lg:mb-0">
            <h1 className="text-4xl lg:text-5xl font-bold mb-2 flex items-center">
              <Trash2 className="mr-4" />
              Smart Waste Management
            </h1>
            <p className="text-xl opacity-90 mb-4">
              AI-Powered Waste Collection & Route Optimization
            </p>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Truck className="w-4 h-4" />
                <span>12 Active Routes</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Last Update: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold">{statistics.totalBins}</div>
              <div className="text-sm opacity-90">Total Bins</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-red-300">{statistics.needingCollection}</div>
              <div className="text-sm opacity-90">Need Collection</div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            icon: Trash2,
            label: 'Smart Bins Active',
            value: statistics.totalBins,
            trend: '+12',
            color: 'from-emerald-500 to-teal-500',
            bgColor: 'from-emerald-50 to-teal-50'
          },
          {
            icon: AlertTriangle,
            label: 'Urgent Collections',
            value: statistics.needingCollection,
            trend: '-8',
            color: 'from-red-500 to-pink-500',
            bgColor: 'from-red-50 to-pink-50'
          },
          {
            icon: Route,
            label: 'Optimized Routes',
            value: statistics.routeOptimized,
            trend: '+3',
            color: 'from-blue-500 to-indigo-500',
            bgColor: 'from-blue-50 to-indigo-50'
          },
          {
            icon: TrendingUp,
            label: 'Efficiency Gain',
            value: `${statistics.efficiencyGain}%`,
            trend: '+5%',
            color: 'from-purple-500 to-pink-500',
            bgColor: 'from-purple-50 to-pink-50'
          },
        ].map((metric, index) => {
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
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Bin Status List */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <MapPin className="mr-3 text-emerald-600" />
            Live Bin Status
          </h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {bins.map((bin) => {
              const status = getFillStatus(bin.fill_level);
              return (
                <div
                  key={bin.id}
                  onClick={() => setSelectedBin(bin)}
                  className={`p-6 rounded-2xl cursor-pointer transition-all duration-300 border-2 ${
                    selectedBin?.id === bin.id 
                      ? `border-${status.color}-500 shadow-lg transform scale-[1.02]` 
                      : 'border-gray-200 hover:border-emerald-300'
                  } bg-gradient-to-br from-white to-gray-50`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-bold text-gray-900 flex items-center">
                        {bin.name}
                        {bin.bin_type === 'Smart' && <Zap className="w-4 h-4 ml-2 text-blue-500" />}
                      </h3>
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{bin.location}</span>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Capacity: {bin.capacity || 240}L · Last: {new Date(bin.last_updated).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-gray-900">{bin.fill_level}%</div>
                      <div className={`text-xs font-semibold px-3 py-1 rounded-full bg-${status.color}-100 text-${status.color}-700 flex items-center`}>
                        {bin.needs_collection ? (
                          <AlertTriangle className="w-3 h-3 mr-1" />
                        ) : (
                          <CheckCircle className="w-3 h-3 mr-1" />
                        )}
                        {status.status}
                      </div>
                    </div>
                  </div>
                  
                  {/* Fill Level Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full bg-gradient-to-r ${
                        bin.fill_level > 80 ? 'from-red-500 to-red-600' :
                        bin.fill_level > 60 ? 'from-orange-500 to-red-500' :
                        bin.fill_level > 30 ? 'from-yellow-500 to-orange-500' :
                        'from-emerald-500 to-teal-500'
                      } transition-all duration-500`}
                      style={{ width: `${bin.fill_level}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Route Optimization */}
        <div className="space-y-6">
          {/* Fill Distribution */}
          <div className="bg-white rounded-3xl p-6 shadow-xl border border-gray-100">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Fill Distribution</h3>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={fillLevelDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={60}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {fillLevelDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2">
              {fillLevelDistribution.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2`} style={{backgroundColor: item.color}}></div>
                    <span>{item.name}</span>
                  </div>
                  <span className="font-semibold">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-white rounded-3xl p-6 shadow-xl border border-gray-100">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Zap className="mr-2 text-blue-600" />
              AI Insights
            </h3>
            <div className="space-y-3">
              {routeSummary.map((insight, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gradient-to-r from-blue-50 to-emerald-50 rounded-xl">
                  <div className="text-lg">{insight.split(' ')[0]}</div>
                  <div className="text-sm text-gray-700 flex-1">{insight.substring(insight.indexOf(' ') + 1)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Waste Collection Chart */}
      <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <TrendingUp className="mr-3 text-emerald-600" />
          Collection Analytics
        </h2>
        <WasteChart />
      </div>
    </div>
  );
};

export default WasteManagement;
