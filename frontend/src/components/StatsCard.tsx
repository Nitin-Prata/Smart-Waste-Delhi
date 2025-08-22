import React from 'react';

interface StatsCardProps {
  title: string;
  value: number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color,
  change,
  changeType = 'neutral'
}) => {
  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive':
        return '↗';
      case 'negative':
        return '↘';
      default:
        return '→';
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="stats-card card-hover">
      <div className="stats-card-header">
        <div className="flex items-center">
          <div 
            className="p-2 rounded-lg mr-3"
            style={{ backgroundColor: `${color}20` }}
          >
            <div style={{ color }}>
              {icon}
            </div>
          </div>
          <div>
            <h3 className="stats-card-title">{title}</h3>
            <p className="text-sm text-gray-600">{subtitle}</p>
          </div>
        </div>
      </div>
      
      <div className="flex items-end justify-between">
        <div className="stats-card-value">{value.toLocaleString()}</div>
        {change && (
          <div className={`stats-card-change ${getChangeColor()}`}>
            <span className="mr-1">{getChangeIcon()}</span>
            {change}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsCard; 