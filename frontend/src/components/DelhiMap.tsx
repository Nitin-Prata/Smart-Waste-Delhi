import React from 'react';

const DelhiMap: React.FC = () => {
  // TODO: Integrate real map API (e.g., Leaflet, Google Maps) and show stations/bins
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Delhi Smart City Map</h3>
      <div className="h-96 flex items-center justify-center text-gray-500">
        [Interactive map will appear here]
      </div>
      <p className="mt-4 text-gray-600">Visualize air quality stations, waste bins, and collection routes across Delhi.</p>
    </div>
  );
};

export default DelhiMap;
