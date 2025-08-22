import React from 'react';
import DelhiMap from '../components/DelhiMap.tsx';
import DelhiLeafletMap from '../components/DelhiLeafletMap.tsx';

interface MapProps {
  sidebarCollapsed: boolean;
}

const legendItems = [
  { label: 'Air Quality Station', color: 'bg-emerald-500' },
  { label: 'Waste Bin', color: 'bg-indigo-500' },
  { label: 'Collection Route', color: 'bg-yellow-400' },
];

const Map: React.FC<MapProps> = ({ sidebarCollapsed }) => {
  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-indigo-900 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi City Map
      </h1>
      <p className="mb-8 text-slate-600 text-center max-w-2xl">Visualize air quality stations, waste bins, and collection routes across Delhi.</p>
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <div className="flex items-center gap-8 mb-4">
          <div className="flex gap-4">
            {legendItems.map(item => (
              <span key={item.label} className="flex items-center gap-2 text-sm font-medium">
                <span className={`inline-block w-4 h-4 rounded-full ${item.color}`}></span>
                {item.label}
              </span>
            ))}
          </div>
        </div>
        <div className="rounded-xl overflow-hidden border border-gray-100 shadow-md">
          <DelhiLeafletMap />
        </div>
      </div>
      <div className="bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-emerald-700 mb-2">Map Extensions</h2>
        <DelhiMap />
      </div>
    </div>
  );
};

export default Map;
