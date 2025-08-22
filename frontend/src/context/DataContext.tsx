import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface DataContextType {
  // Air Quality Data
  airQualityData: any;
  loadingAirQuality: boolean;
  errorAirQuality: string | null;
  fetchAirQualityData: () => Promise<void>;
  
  // Waste Management Data
  wasteData: any;
  loadingWaste: boolean;
  errorWaste: string | null;
  fetchWasteData: () => Promise<void>;
  
  // Dashboard Data
  dashboardData: any;
  loadingDashboard: boolean;
  errorDashboard: string | null;
  fetchDashboardData: () => Promise<void>;
  
  // General loading state
  isLoading: boolean;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

interface DataProviderProps {
  children: ReactNode;
}

export const DataProvider: React.FC<DataProviderProps> = ({ children }) => {
  // Air Quality State
  const [airQualityData, setAirQualityData] = useState<any>(null);
  const [loadingAirQuality, setLoadingAirQuality] = useState(false);
  const [errorAirQuality, setErrorAirQuality] = useState<string | null>(null);

  // Waste Management State
  const [wasteData, setWasteData] = useState<any>(null);
  const [loadingWaste, setLoadingWaste] = useState(false);
  const [errorWaste, setErrorWaste] = useState<string | null>(null);

  // Dashboard State
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [errorDashboard, setErrorDashboard] = useState<string | null>(null);

  // Fetch Air Quality Data
  const fetchAirQualityData = async () => {
    try {
      setLoadingAirQuality(true);
      setErrorAirQuality(null);
      
      const response = await fetch('/api/air-quality/current');
      if (!response.ok) {
        throw new Error('Failed to fetch air quality data');
      }
      
      const data = await response.json();
      setAirQualityData(data);
    } catch (error) {
      console.error('Error fetching air quality data:', error);
      setErrorAirQuality(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoadingAirQuality(false);
    }
  };

  // Fetch Waste Management Data
  const fetchWasteData = async () => {
    try {
      setLoadingWaste(true);
      setErrorWaste(null);
      
      const response = await fetch('/api/waste/summary');
      if (!response.ok) {
        throw new Error('Failed to fetch waste data');
      }
      
      const data = await response.json();
      setWasteData(data);
    } catch (error) {
      console.error('Error fetching waste data:', error);
      setErrorWaste(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoadingWaste(false);
    }
  };

  // Fetch Dashboard Data
  const fetchDashboardData = async () => {
    try {
      setLoadingDashboard(true);
      setErrorDashboard(null);
      
      const [overviewResponse, healthResponse, trendsResponse, alertsResponse] = await Promise.all([
        fetch('/api/dashboard/overview'),
        fetch('/api/dashboard/city-health'),
        fetch('/api/dashboard/trends?days=7'),
        fetch('/api/dashboard/alerts-summary')
      ]);

      if (!overviewResponse.ok || !healthResponse.ok || !trendsResponse.ok || !alertsResponse.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const [overviewData, healthData, trendsData, alertsData] = await Promise.all([
        overviewResponse.json(),
        healthResponse.json(),
        trendsResponse.json(),
        alertsResponse.json()
      ]);

      setDashboardData({
        overview: overviewData.overview,
        city_health: healthData.city_health,
        trends: trendsData.trends,
        alerts_summary: alertsData.alerts_summary
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setErrorDashboard(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoadingDashboard(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
    
    // Set up periodic refresh
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const isLoading = loadingAirQuality || loadingWaste || loadingDashboard;

  const value: DataContextType = {
    airQualityData,
    loadingAirQuality,
    errorAirQuality,
    fetchAirQualityData,
    wasteData,
    loadingWaste,
    errorWaste,
    fetchWasteData,
    dashboardData,
    loadingDashboard,
    errorDashboard,
    fetchDashboardData,
    isLoading
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}; 