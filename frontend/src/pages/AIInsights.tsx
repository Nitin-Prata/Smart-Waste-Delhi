import React from 'react';

interface AIInsightsProps {
  sidebarCollapsed: boolean;
}

const recommendations = [
  {
    id: 1,
    title: 'Optimize Waste Collection Route',
    description: 'AI suggests a new route for North Delhi to reduce travel time by 22%.',
    action: 'Optimize Route',
    color: 'bg-indigo-100 text-indigo-700',
  },
  {
    id: 2,
    title: 'Send Air Quality Alert',
    description: 'AQI predicted to exceed safe levels in Karol Bagh tomorrow.',
    action: 'Send Alert',
    color: 'bg-red-100 text-red-700',
  },
  {
    id: 3,
    title: 'Increase Bin Pickup Frequency',
    description: 'Bin #23 (Karol Bagh) predicted to be full by 8 AM daily.',
    action: 'Update Schedule',
    color: 'bg-emerald-100 text-emerald-700',
  },
];

const AIInsights: React.FC<AIInsightsProps> = ({ sidebarCollapsed }) => {
  return (
    <div className={`pt-4 min-h-screen bg-gray-50 flex flex-col items-center justify-start transition-all duration-300 px-8 ${sidebarCollapsed ? 'md:max-w-6xl' : 'md:max-w-full'}`}> 
      <h1 className="text-4xl font-extrabold tracking-tight mb-8 text-indigo-900 text-center w-full bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-indigo-600">
        Smart Waste Delhi AI Insights
      </h1>
      <p className="mb-8 text-slate-600 text-center max-w-2xl">Discover actionable insights powered by AI for air quality and waste management.</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
        {recommendations.map(rec => (
          <div key={rec.id} className={`rounded-2xl shadow-lg p-6 flex flex-col gap-3 ${rec.color} hover:shadow-xl transition`}>
            <div className="font-semibold text-lg">{rec.title}</div>
            <div className="text-slate-700">{rec.description}</div>
            <button className="mt-2 px-4 py-2 rounded-full bg-indigo-600 text-white text-sm font-medium shadow hover:brightness-110 transition">{rec.action}</button>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-lg font-semibold text-emerald-700 mb-2">Impact Analysis</h2>
        <ul className="list-disc pl-6 text-slate-700 space-y-2">
          <li>AI-driven route optimization saved 18% fuel last month.</li>
          <li>Predictive alerts reduced bin overflow incidents by 35%.</li>
          <li>Air quality warnings reached 12,000 citizens in real time.</li>
        </ul>
      </div>
    </div>
  );
};

export default AIInsights;
