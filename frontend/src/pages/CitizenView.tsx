import React from 'react';
import { Wind, Trash2, AlertTriangle, Users } from 'lucide-react';

interface CitizenViewProps {
  sidebarCollapsed: boolean;
}

const alerts = [
  { id: 1, message: 'AQI is Moderate in Connaught Place.', severity: 'info' },
  { id: 2, message: 'Bin #23 (Karol Bagh) is almost full.', severity: 'warning' },
];

const severityColors = {
  info: 'bg-emerald-100 text-emerald-700',
  warning: 'bg-yellow-100 text-yellow-700',
};

const CitizenView: React.FC<CitizenViewProps> = ({ sidebarCollapsed }) => {
  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-emerald-700 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi Citizen View
      </h1>
      <p className="mb-8 text-slate-600 text-lg text-center max-w-2xl">Empowering citizens with real-time air quality and waste management insights.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center gap-4">
          <Wind className="w-12 h-12 text-emerald-500 mb-2" />
          <div className="text-2xl font-bold text-slate-900">AQI: 98</div>
          <div className="text-lg text-emerald-700 font-semibold">Moderate</div>
          <div className="text-sm text-slate-500">Nearest Station: Connaught Place</div>
        </div>
        <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center gap-4">
          <Trash2 className="w-12 h-12 text-indigo-500 mb-2" />
          <div className="text-2xl font-bold text-slate-900">Bin #23</div>
          <div className="text-lg text-yellow-700 font-semibold">95% Full</div>
          <div className="text-sm text-slate-500">Location: Karol Bagh</div>
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-indigo-900 mb-2">Community Alerts</h2>
        <div className="space-y-4">
          {alerts.map(alert => (
            <div key={alert.id} className={`flex items-center gap-4 p-4 rounded-xl shadow-sm ${severityColors[alert.severity]}`}>
              <AlertTriangle className="w-6 h-6" />
              <div className="flex-1 text-lg">{alert.message}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-8 text-center text-lg text-emerald-700 font-semibold">
        <Users className="inline-block w-8 h-8 mr-2 text-emerald-500" />
        Good news: Delhi’s waste collection and air quality are improving!
      </div>
    </div>
  );
};

export default CitizenView;
