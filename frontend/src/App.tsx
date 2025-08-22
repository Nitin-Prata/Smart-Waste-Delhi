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
import Navbar from './components/Navbar.tsx';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  return (
    <DataProvider>
      <Router>
        <div className="App bg-gradient-to-br from-slate-50 via-blue-50 to-emerald-50 min-h-screen">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                borderRadius: '12px',
                padding: '16px',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
              },
            }}
          />
          
          {/* Enhanced Navbar */}
          <Navbar 
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
          />
          
          <div className="flex">
            {/* Enhanced Sidebar */}
            <div className={`fixed inset-y-0 left-0 z-30 transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:block`}>
              <Sidebar 
                collapsed={sidebarCollapsed} 
                setCollapsed={setSidebarCollapsed}
                sidebarOpen={sidebarOpen}
                setSidebarOpen={setSidebarOpen}
              />
            </div>
            
            {/* Backdrop for mobile */}
            {sidebarOpen && (
              <div 
                className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
                onClick={() => setSidebarOpen(false)}
              />
            )}
            
            {/* Main Content */}
            <main className={`flex-1 transition-all duration-300 pt-20 ${sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-80'}`}>
              <div className="container mx-auto px-4 py-6 max-w-7xl">
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
              </div>
            </main>
          </div>
        </div>
      </Router>
    </DataProvider>
  );
}

export default App;
