import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './App.css';
import Sidebar from './components/Sidebar.tsx';
import Dashboard from './pages/Dashboard.tsx';
import AirQuality from './pages/AirQuality.tsx';
import WasteManagement from './pages/WasteManagement.tsx';
import AIInsights from './pages/AIInsights.tsx';
import Map from './pages/Map.tsx';
import CitizenView from './pages/CitizenView.tsx';
import Alerts from './pages/Alerts.tsx';
import { DataProvider } from './context/DataContext.tsx';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // for mobile
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false); // for desktop collapse
  return (
    <DataProvider>
      <Router>
        <div className="App bg-gray-50 min-h-screen">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
          {/* Header */}
          <header className="flex items-center justify-between px-8 py-4 bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
            <div className="flex items-center">
              <button
                className="mr-4 p-2 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-700 focus:outline-none md:hidden"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Open sidebar"
              >
                <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
              </button>
              <span className="text-2xl font-bold text-blue-700 tracking-wide">Smart Waste Delhi</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-green-600 font-medium flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>System Online</span>
              <span className="bg-gray-100 px-3 py-1 rounded-full text-gray-700 font-semibold">Admin</span>
            </div>
          </header>
          <div className="flex">
            {/* Sidebar: hidden on mobile, toggled by button */}
            <div className={`fixed inset-y-0 left-0 z-20 transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:static md:block`}>
              <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
            </div>
            <main
              className={`flex-1 p-6 transition-all duration-300 ${sidebarCollapsed ? 'md:ml-16' : 'md:ml-64'}`}
            >
              <Routes>
                <Route path="/" element={<Dashboard sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/dashboard" element={<Dashboard sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/air-quality" element={<AirQuality sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/waste-management" element={<WasteManagement sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/ai-insights" element={<AIInsights sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/map" element={<Map sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/alerts" element={<Alerts sidebarCollapsed={sidebarCollapsed} />} />
                <Route path="/citizen" element={<CitizenView sidebarCollapsed={sidebarCollapsed} />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </DataProvider>
  );
}
export default App;
