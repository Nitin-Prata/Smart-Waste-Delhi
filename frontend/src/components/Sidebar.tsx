import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart2, Wind, Trash2, Bot, Map, Users, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: React.Dispatch<React.SetStateAction<boolean>>;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: <BarChart2 className="w-6 h-6" /> },
    { name: 'Air Quality', href: '/air-quality', icon: <Wind className="w-6 h-6" /> },
    { name: 'Waste Management', href: '/waste-management', icon: <Trash2 className="w-6 h-6" /> },
    { name: 'AI Insights', href: '/ai-insights', icon: <Bot className="w-6 h-6" /> },
    { name: 'Map', href: '/map', icon: <Map className="w-6 h-6" /> },
    { name: 'Citizen View', href: '/citizen', icon: <Users className="w-6 h-6" /> },
    { name: 'Alerts', href: '/alerts', icon: <AlertTriangle className="w-6 h-6" /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside
      className={`hidden md:flex flex-col fixed inset-y-0 z-30 transition-all duration-300 bg-gradient-to-b from-indigo-900 to-indigo-700 shadow-xl ${
        collapsed ? 'w-16' : 'w-64'
      } rounded-r-3xl`}
      aria-label="Sidebar navigation"
    >
      <div className="flex flex-col min-h-0 px-2 py-6 h-full">
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">🌱</span>
            </div>
            {!collapsed && (
              <div>
                <h2 className="text-xl font-bold text-white tracking-wide">Smart Delhi</h2>
                <p className="text-xs text-indigo-100">Waste & Air Quality</p>
              </div>
            )}
          </div>
          <button
            className="p-2 rounded-full hover:bg-indigo-800 text-indigo-100 focus:outline-none"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>
        <nav className="flex-1 space-y-2" role="navigation">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`group flex items-center px-3 py-3 text-base font-semibold rounded-xl transition-all duration-200 shadow-sm ${
                isActive(item.href)
                  ? 'bg-white text-indigo-900 shadow-lg border-l-4 border-emerald-400 scale-105'
                  : 'text-indigo-100 hover:bg-indigo-800 hover:text-white'
              }`}
              aria-selected={isActive(item.href)}
              tabIndex={0}
            >
              <span className="mr-3">{item.icon}</span>
              {!collapsed && item.name}
            </Link>
          ))}
        </nav>
        <div className={`mt-10 flex flex-col items-center ${collapsed ? 'hidden' : ''}`}>
          <span className="text-xs text-indigo-200">Hackathon Edition</span>
          <span className="text-xs text-indigo-200">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;