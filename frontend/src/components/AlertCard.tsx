import React from 'react';

interface AlertCardProps {
  type: string;
  severity: string;
  message: string;
  timestamp: string;
}

const AlertCard: React.FC<AlertCardProps> = ({
  type,
  severity,
  message,
  timestamp
}) => {
  const getSeverityColor = () => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  const getTypeIcon = () => {
    switch (type) {
      case 'air_quality':
        return '🌬️';
      case 'waste_collection':
        return '🗑️';
      default:
        return '⚠️';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={`p-3 border-l-4 rounded-r-lg ${getSeverityColor()}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <span className="text-lg">{getTypeIcon()}</span>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-sm font-medium text-gray-900 capitalize">
                {type.replace('_', ' ')}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${
                severity.toLowerCase() === 'high' || severity.toLowerCase() === 'critical'
                  ? 'bg-red-100 text-red-800'
                  : severity.toLowerCase() === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {severity}
              </span>
            </div>
            <p className="text-sm text-gray-700">{message}</p>
          </div>
        </div>
        <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
          {formatTimestamp(timestamp)}
        </span>
      </div>
    </div>
  );
};

export default AlertCard; 