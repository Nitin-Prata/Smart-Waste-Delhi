import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Wind, Trash2, Bot, Map, Users, AlertTriangle, ChevronLeft, ChevronRight, Home } from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: React.Dispatch<React.SetStateAction<boolean>>;
  sidebarOpen: boolean;
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed, sidebarOpen, setSidebarOpen }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home, description: 'Overview & Analytics' },
    { name: 'Air Quality', href: '/air-quality', icon: Wind, description: 'AQI Monitoring' },
    { name: 'Waste Management', href: '/waste-management', icon: Trash2, description: 'Smart Bins' },
    { name: 'AI Insights', href: '/ai-insights', icon: Bot, description: 'ML Predictions' },
    { name: 'Live Map', href: '/map', icon: Map, description: 'Real-time Data' },
    { name: 'Citizen Portal', href: '/citizen', icon: Users, description: 'Public Interface' },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle, description: 'System Alerts' },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLinkClick = () => {
    // Close sidebar on mobile after clicking a link
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  return (
    <aside
      className={`${collapsed ? 'w-20' : 'w-80'} transition-all duration-300 bg-white/90 backdrop-blur-xl border-r border-gray-200/50 shadow-2xl h-screen flex flex-col`}
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200/50">
        <div className="flex items-center justify-between">
          <div className={`flex items-center space-x-3 ${collapsed ? 'justify-center' : ''}`}>
            <div className="w-10 h-10 bg-gradient-to-r from-emerald-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">🌱</span>
            </div>
            {!collapsed && (
              <div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                  Smart Delhi
                </h2>
                <p className="text-xs text-gray-500 font-medium">
                  Waste & Air Quality
                </p>
              </div>
            )}
          </div>
          <button
            className="hidden lg:flex p-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 transition-all duration-200"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={handleLinkClick}
              className={`group flex items-center px-3 py-4 rounded-xl transition-all duration-200 ${
                active
                  ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-lg transform scale-[1.02]'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className={`w-5 h-5 ${collapsed ? 'mx-auto' : 'mr-3'} ${active ? 'text-white' : ''}`} />
              {!collapsed && (
                <div className="flex-1">
                  <div className="font-semibold">{item.name}</div>
                  <div className={`text-xs ${active ? 'text-white/80' : 'text-gray-400'}`}>
                    {item.description}
                  </div>
                </div>
              )}
              {!collapsed && active && (
                <div className="w-2 h-2 bg-white rounded-full opacity-80"></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-6 border-t border-gray-200/50">
          <div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-4 rounded-xl border border-emerald-200/50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-400 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🏆</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-800">Hackathon Edition</p>
                <p className="text-xs text-gray-600">v2.0.0 - Gen AI</p>
              </div>
            </div>
            <div className="mt-3 flex items-center space-x-2">
              <div className="flex-1 bg-emerald-200 rounded-full h-2">
                <div className="bg-gradient-to-r from-emerald-400 to-blue-500 h-2 rounded-full w-3/4"></div>
              </div>
              <span className="text-xs text-gray-600 font-medium">75%</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">System Optimization</p>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;