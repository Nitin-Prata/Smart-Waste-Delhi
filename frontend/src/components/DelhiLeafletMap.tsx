import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { parseWasteBinsCSV, BinLocation } from '../utils/parseWasteBinsCSV.ts';
import 'leaflet/dist/leaflet.css';

const stations = [
  { name: 'Station 1', position: [28.7041, 77.1025] },
  { name: 'Station 2', position: [28.5355, 77.3910] },
];

const DelhiLeafletMap: React.FC = () => {
  const [binsState, setBins] = useState<BinLocation[]>([]);
  useEffect(() => {
    fetch('/data/waste_bins_clean.csv')
      .then((res) => res.text())
      .then((csv) => {
        setBins(parseWasteBinsCSV(csv));
      });
  }, []);
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Delhi Smart City Map (Interactive)</h3>
      <MapContainer center={[28.6139, 77.2090]} zoom={11} style={{ height: '400px', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          options={{ attribution: '&copy; OpenStreetMap contributors' }}
        />
        {/* Example stations, can be loaded from backend if needed */}
        <Marker position={[28.7041, 77.1025]}>
          <Popup>Station 1 (Air Quality Station)</Popup>
        </Marker>
        <Marker position={[28.5355, 77.3910]}>
          <Popup>Station 2 (Air Quality Station)</Popup>
        </Marker>
    {/* Real bins from CSV */}
    {binsState.map((bin: BinLocation, idx: number) => (
      typeof bin.lat === 'number' && typeof bin.lng === 'number' && typeof bin.name === 'string' ? (
        <Marker key={idx} position={[bin.lat, bin.lng]}>
          <Popup>{bin.name} (Waste Bin)</Popup>
        </Marker>
      ) : null
    ))}
      </MapContainer>
      <p className="mt-4 text-gray-600">Visualize air quality stations and waste bins across Delhi.</p>
    </div>
  );
};

export default DelhiLeafletMap;
