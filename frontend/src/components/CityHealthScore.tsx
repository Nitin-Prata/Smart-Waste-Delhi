import React from 'react';

interface CityHealthScoreProps {
  overallScore: number;
  airQualityScore: number;
  wasteManagementScore: number;
  status: string;
  statusColor: string;
}

const CityHealthScore: React.FC<CityHealthScoreProps> = ({
  overallScore,
  airQualityScore,
  wasteManagementScore,
  status,
  statusColor
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Moderate';
    return 'Poor';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">City Health Score</h2>
          <p className="text-gray-600">Overall environmental health of Delhi</p>
        </div>
        <div className="text-right">
          <div 
            className="text-4xl font-bold"
            style={{ color: statusColor }}
          >
            {overallScore}
          </div>
          <div 
            className="text-lg font-medium"
            style={{ color: statusColor }}
          >
            {status}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Air Quality Score */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-lg font-medium text-gray-900">Air Quality</span>
            <span 
              className="text-2xl font-bold"
              style={{ color: getScoreColor(airQualityScore) }}
            >
              {airQualityScore}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="h-3 rounded-full transition-all duration-500"
              style={{ 
                width: `${airQualityScore}%`,
                backgroundColor: getScoreColor(airQualityScore)
              }}
            ></div>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Score</span>
            <span 
              className="font-medium"
              style={{ color: getScoreColor(airQualityScore) }}
            >
              {getScoreLabel(airQualityScore)}
            </span>
          </div>
        </div>

        {/* Waste Management Score */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-lg font-medium text-gray-900">Waste Management</span>
            <span 
              className="text-2xl font-bold"
              style={{ color: getScoreColor(wasteManagementScore) }}
            >
              {wasteManagementScore}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="h-3 rounded-full transition-all duration-500"
              style={{ 
                width: `${wasteManagementScore}%`,
                backgroundColor: getScoreColor(wasteManagementScore)
              }}
            ></div>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Score</span>
            <span 
              className="font-medium"
              style={{ color: getScoreColor(wasteManagementScore) }}
            >
              {getScoreLabel(wasteManagementScore)}
            </span>
          </div>
        </div>
      </div>

      {/* Health Indicators */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Health Indicators</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mx-auto mb-2"></div>
            <span className="text-sm text-gray-600">Excellent</span>
          </div>
          <div className="text-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mx-auto mb-2"></div>
            <span className="text-sm text-gray-600">Good</span>
          </div>
          <div className="text-center">
            <div className="w-3 h-3 rounded-full bg-yellow-500 mx-auto mb-2"></div>
            <span className="text-sm text-gray-600">Moderate</span>
          </div>
          <div className="text-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mx-auto mb-2"></div>
            <span className="text-sm text-gray-600">Poor</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CityHealthScore; 