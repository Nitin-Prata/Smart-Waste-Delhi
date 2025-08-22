
import React, { useEffect, useState } from 'react';

interface AlertsProps {
  sidebarCollapsed: boolean;
}

const severityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  warning: 'bg-yellow-100 text-yellow-700',
  success: 'bg-emerald-100 text-emerald-700',
};

interface AirQualityAlert {
  id: number;
  type: string;
  severity: string;
  message: string;
  triggered_at: string;
  acknowledged: boolean;
}

interface WasteCollectionAlert {
  bin_id: number;
  bin_name: string;
  location: string;
  fill_level: number;
  priority: string;
  last_updated: string;
}

const Alerts: React.FC<AlertsProps> = ({ sidebarCollapsed }) => {
  const [airQualityAlerts, setAirQualityAlerts] = useState<AirQualityAlert[]>([]);
  const [wasteAlerts, setWasteAlerts] = useState<WasteCollectionAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/dashboard/alerts-summary`);
        const data = await res.json();
        setAirQualityAlerts(data.alerts_summary.air_quality_alerts || []);
        setWasteAlerts(data.alerts_summary.waste_collection_alerts || []);
      } catch (err) {
        setAirQualityAlerts([]);
        setWasteAlerts([]);
      }
      setLoading(false);
    };
    fetchAlerts();
  }, []);

  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-emerald-700 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi Alerts
      </h1>
      <p className="mb-8 text-slate-600 text-center max-w-2xl">Stay updated with real-time alerts for air quality and waste management.</p>
      <div className="bg-white rounded-2xl shadow-lg p-6 w-full max-w-2xl">
        <div className="sticky top-0 bg-white z-10 pb-2 mb-4 border-b border-gray-100 flex items-center justify-between">
          <span className="text-lg font-semibold text-indigo-900">Recent Alerts</span>
          <button className="px-4 py-1 rounded-full bg-emerald-600 text-white text-sm font-medium shadow hover:brightness-110 transition">Sound On</button>
        </div>
        {loading ? (
          <div className="text-center text-slate-500 py-8">Loading alerts...</div>
        ) : (
          <div className="space-y-4">
            {airQualityAlerts.map(alert => (
              <div key={`aq-${alert.id}`} className="flex items-center gap-4 p-4 rounded-xl shadow-sm bg-gray-50 hover:bg-gray-100 transition">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${severityColors[alert.severity] || 'bg-gray-200 text-gray-700'}`}>{alert.severity?.toUpperCase() || 'ALERT'}</span>
                <div className="flex-1">
                  <div className="font-medium text-slate-900">{alert.message}</div>
                  <div className="text-xs text-slate-500">Air Quality • {new Date(alert.triggered_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
            {wasteAlerts.map(alert => (
              <div key={`waste-${alert.bin_id}`} className="flex items-center gap-4 p-4 rounded-xl shadow-sm bg-gray-50 hover:bg-gray-100 transition">
                <span className={`px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-700`}>WASTE</span>
                <div className="flex-1">
                  <div className="font-medium text-slate-900">{alert.bin_name} ({alert.location}) needs collection. Fill Level: <span className="font-bold">{Math.round(alert.fill_level * 100)}%</span></div>
                  <div className="text-xs text-slate-500">Priority: {alert.priority} • Last Updated: {new Date(alert.last_updated).toLocaleString()}</div>
                </div>
              </div>
            ))}
            {airQualityAlerts.length === 0 && wasteAlerts.length === 0 && (
              <div className="text-center text-slate-500 py-8">No active alerts at the moment.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
