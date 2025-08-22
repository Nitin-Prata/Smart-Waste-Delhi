import React, { useEffect, useState } from 'react';
import { Bot, Brain, Lightbulb, TrendingUp, AlertCircle, Cpu, Zap, Target, BarChart3, MessageSquare } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, AreaChart, Area } from 'recharts';

interface AIInsightsProps {
  sidebarCollapsed: boolean;
}

const AIInsights: React.FC<AIInsightsProps> = ({ sidebarCollapsed }) => {
  const [loading, setLoading] = useState(true);
  const [predictions, setPredictions] = useState({
    aqi_forecast: [],
    waste_forecast: [],
    recommendations: [],
    alerts: []
  });
  const [modelPerformance, setModelPerformance] = useState([
    { model: 'AQI LSTM', accuracy: 94.2, latency: 45, status: 'active' },
    { model: 'Waste RF', accuracy: 91.7, latency: 23, status: 'active' },
    { model: 'Route Optimizer', accuracy: 96.1, latency: 78, status: 'active' },
    { model: 'Anomaly Detection', accuracy: 88.9, latency: 12, status: 'training' }
  ]);
  const [aiChat, setAiChat] = useState([
    { type: 'ai', message: 'Hello! I\'m your AI assistant for Smart Delhi. How can I help you analyze the city\'s data today?' },
    { type: 'user', message: 'What are the key insights for today?' },
    { type: 'ai', message: '🔍 Today\'s key insights:\n• AQI is expected to improve by 15% this afternoon\n• 47 waste bins need urgent collection\n• Route optimization saved 23% travel time\n• Air quality is unhealthy - recommend indoor activities' }
  ]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    fetchAIInsights();
  }, []);

  const fetchAIInsights = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/ai-insights/predictions`);
      const data = await res.json();
      setPredictions(data);
    } catch (err) {
      // Demo data
      setPredictions({
        aqi_forecast: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          predicted_aqi: 150 + Math.sin(i * 0.3) * 30 + Math.random() * 20,
          confidence: 0.85 + Math.random() * 0.1
        })),
        waste_forecast: Array.from({ length: 7 }, (_, i) => ({
          day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
          predicted_waste: 800 + Math.random() * 400,
          actual_waste: i < 5 ? 750 + Math.random() * 350 : null
        })),
        recommendations: [
          { 
            type: 'urgent', 
            title: 'Air Quality Alert', 
            message: 'AQI expected to reach 200+ in next 2 hours. Deploy emergency measures.',
            confidence: 0.92,
            action: 'Activate air purifiers in public areas'
          },
          { 
            type: 'optimization', 
            title: 'Route Optimization', 
            message: 'Rerouting trucks can save 2.3 hours and reduce emissions by 18%.',
            confidence: 0.87,
            action: 'Update collection routes'
          },
          { 
            type: 'maintenance', 
            title: 'Bin Maintenance', 
            message: '12 smart bins showing sensor anomalies - schedule maintenance.',
            confidence: 0.94,
            action: 'Schedule technical inspection'
          }
        ],
        alerts: [
          { severity: 'high', message: 'AQI spike detected in Connaught Place area', timestamp: new Date() },
          { severity: 'medium', message: 'Waste collection efficiency down 8% this week', timestamp: new Date(Date.now() - 3600000) },
          { severity: 'low', message: 'New AI model training completed successfully', timestamp: new Date(Date.now() - 7200000) }
        ]
      });
      toast.error('Using demo data - AI API not available');
    }
    setLoading(false);
  };

  const sendMessage = () => {
    if (!newMessage.trim()) return;
    
    setAiChat(prev => [...prev, { type: 'user', message: newMessage }]);
    setNewMessage('');
    
    // Simulate AI response
    setTimeout(() => {
      const responses = [
        '🤖 Based on current data patterns, I recommend focusing on the Karol Bagh area where AQI is highest and waste collection is most needed.',
        '📊 The predictive models show a 23% improvement opportunity in route optimization. Would you like me to generate specific recommendations?',
        '🔄 System efficiency is at 87%. The main bottlenecks are in sensor maintenance and route planning algorithms.',
        '⚠️ I\'ve detected unusual patterns in the data that might indicate equipment malfunctions. Shall I run a diagnostic check?'
      ];
      setAiChat(prev => [...prev, { 
        type: 'ai', 
        message: responses[Math.floor(Math.random() * responses.length)]
      }]);
    }, 1500);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <Bot className="absolute inset-0 m-auto w-8 h-8 text-purple-600" />
          </div>
          <p className="text-gray-600 font-medium">AI models are analyzing data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="mb-6 lg:mb-0">
            <h1 className="text-4xl lg:text-5xl font-bold mb-2 flex items-center">
              <Brain className="mr-4" />
              AI Insights Hub
            </h1>
            <p className="text-xl opacity-90 mb-4">
              Advanced Machine Learning Analytics & Predictions
            </p>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4" />
                <span>4 Active Models</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>Real-time Processing</span>
              </div>
            </div>
          </div>
          <div className="text-center lg:text-right">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-3xl font-bold">94.2%</div>
                <div className="text-sm opacity-90">Avg Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold">2.3s</div>
                <div className="text-sm opacity-90">Inference Time</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {predictions.recommendations.map((rec: any, index: number) => (
          <div
            key={index}
            className={`bg-gradient-to-br ${
              rec.type === 'urgent' ? 'from-red-50 to-pink-50 border-red-200' :
              rec.type === 'optimization' ? 'from-blue-50 to-indigo-50 border-blue-200' :
              'from-emerald-50 to-teal-50 border-emerald-200'
            } border-2 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`p-3 rounded-xl ${
                rec.type === 'urgent' ? 'bg-red-500' :
                rec.type === 'optimization' ? 'bg-blue-500' :
                'bg-emerald-500'
              } shadow-lg`}>
                {rec.type === 'urgent' ? <AlertCircle className="w-6 h-6 text-white" /> :
                 rec.type === 'optimization' ? <Target className="w-6 h-6 text-white" /> :
                 <Lightbulb className="w-6 h-6 text-white" />}
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                rec.type === 'urgent' ? 'bg-red-100 text-red-700' :
                rec.type === 'optimization' ? 'bg-blue-100 text-blue-700' :
                'bg-emerald-100 text-emerald-700'
              }`}>
                {Math.round(rec.confidence * 100)}% confident
              </div>
            </div>
            <h3 className="font-bold text-gray-900 mb-2">{rec.title}</h3>
            <p className="text-gray-700 mb-4 text-sm">{rec.message}</p>
            <div className="bg-white/50 p-3 rounded-xl">
              <p className="text-xs font-semibold text-gray-600">RECOMMENDED ACTION:</p>
              <p className="text-sm text-gray-800 font-medium">{rec.action}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Predictions Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AQI Forecast */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="mr-3 text-purple-600" />
            24h AQI Prediction
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={predictions.aqi_forecast}>
                <defs>
                  <linearGradient id="aqiPredictionGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f9ff" />
                <XAxis dataKey="hour" tickFormatter={(hour) => `${hour}:00`} stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  labelFormatter={(hour) => `${hour}:00`}
                  formatter={(value: any, name: any) => [Math.round(value), name === 'predicted_aqi' ? 'Predicted AQI' : name]}
                  contentStyle={{
                    backgroundColor: '#1e1b4b',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="predicted_aqi" 
                  stroke="#8b5cf6" 
                  strokeWidth={3}
                  fill="url(#aqiPredictionGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Waste Prediction */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="mr-3 text-emerald-600" />
            Weekly Waste Forecast
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={predictions.waste_forecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
                <XAxis dataKey="day" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  formatter={(value: any, name: any) => [
                    `${Math.round(value)} tons`, 
                    name === 'predicted_waste' ? 'Predicted' : 'Actual'
                  ]}
                  contentStyle={{
                    backgroundColor: '#064e3b',
                    border: 'none',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted_waste" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  dot={{ r: 6, fill: '#10b981' }}
                  name="Predicted"
                />
                <Line 
                  type="monotone" 
                  dataKey="actual_waste" 
                  stroke="#6b7280" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 4, fill: '#6b7280' }}
                  name="Actual"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Chat Interface & Model Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Chat */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <MessageSquare className="mr-3 text-blue-600" />
            AI Assistant
          </h2>
          <div className="h-64 overflow-y-auto bg-gray-50 rounded-2xl p-4 mb-4 space-y-3">
            {aiChat.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-4 py-3 rounded-2xl ${
                  message.type === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}>
                  <p className="text-sm whitespace-pre-line">{message.message}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask AI about city data..."
              className="flex-1 px-4 py-3 bg-gray-100 rounded-xl border-none focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <button
              onClick={sendMessage}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-200"
            >
              Send
            </button>
          </div>
        </div>

        {/* Model Performance */}
        <div className="bg-white rounded-3xl p-8 shadow-xl border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Cpu className="mr-3 text-purple-600" />
            Model Performance
          </h2>
          <div className="space-y-4">
            {modelPerformance.map((model, index) => (
              <div key={index} className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-gray-900">{model.model}</h3>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                    model.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {model.status}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Accuracy</div>
                    <div className="text-xl font-bold text-gray-900">{model.accuracy}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Latency</div>
                    <div className="text-xl font-bold text-gray-900">{model.latency}ms</div>
                  </div>
                </div>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${model.accuracy}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
