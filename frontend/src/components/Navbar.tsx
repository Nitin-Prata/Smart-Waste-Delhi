import React, { useState, useEffect } from 'react';
import { Menu, X, Bell, Settings, User, ChevronDown } from 'lucide-react';

interface NavbarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ sidebarOpen, setSidebarOpen }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notifications, setNotifications] = useState(3);
  
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-200/50 shadow-lg">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          <button
            className="lg:hidden p-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-emerald-400 to-blue-500 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">🌱</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                Smart Delhi
              </h1>
              <p className="text-xs text-gray-500 font-medium">
                AI-Powered City Management
              </p>
            </div>
          </div>
        </div>

        {/* Center Section - Time & Status */}
        <div className="hidden md:flex items-center space-x-6">
          <div className="flex items-center space-x-2 bg-emerald-100 px-3 py-2 rounded-full">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-emerald-700 font-semibold text-sm">System Online</span>
          </div>
          
          <div className="text-gray-600 font-medium">
            {currentTime.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              timeZone: 'Asia/Kolkata'
            })} IST
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-all duration-200">
            <Bell className="w-5 h-5 text-gray-700" />
            {notifications > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                {notifications}
              </span>
            )}
          </button>

          {/* Settings */}
          <button className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-all duration-200">
            <Settings className="w-5 h-5 text-gray-700" />
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full shadow-lg">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold">Admin</p>
              <p className="text-xs opacity-90">Delhi Municipal</p>
            </div>
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar; 