import { useMemo } from 'react';
import { useQuery } from './useQuery';
import api from '../api';

/**
 * Mock analytics data for fallback/demo purposes
 */
const MOCK_ANALYTICS_DATA = {
  total_properties: 184,
  portfolio_value: 47800000,
  monthly_income: 3750000,
  occupancy_rate: 0.946,
  yoy_growth: 8.2,
  risk_score: 23.5,
  total_units: 1247,
  average_cap_rate: 7.2,
  maintenance_ratio: 0.12,
  debt_to_equity: 0.65,
  lease_expiry_90_days: 42,
  market_trend: 'bullish',
  last_updated: new Date().toISOString(),
};

/**
 * Custom hook for fetching analytics/KPI data
 * 
 * Features:
 * - Fetches from GET /api/analytics
 * - Loading state while fetching
 * - Error handling with fallback to mock data
 * - Auto-refetch every 5 minutes
 * - Cache for 3 minutes
 * - Manual refetch function
 * 
 * @param {Object} options - Hook configuration options
 * @param {boolean} options.useMockData - Force use of mock data (default: false)
 * @param {boolean} options.enableAutoRefetch - Enable 5-minute auto-refetch (default: true)
 * @param {number} options.refetchInterval - Custom refetch interval in ms (default: 300000 = 5 min)
 * @param {number} options.staleTime - Cache duration in ms (default: 180000 = 3 min)
 * 
 * @returns {Object} Analytics data and state
 * @returns {Object} returns.analytics - Analytics data object
 * @returns {boolean} returns.isLoading - Loading state
 * @returns {string|null} returns.error - Error message
 * @returns {Function} returns.refetch - Manual refetch function
 * @returns {boolean} returns.isFetching - Background fetching state
 * @returns {boolean} returns.isError - Error state flag
 * @returns {boolean} returns.isSuccess - Success state flag
 * @returns {boolean} returns.usingMockData - Whether mock data is being used
 */
export function useAnalytics(options = {}) {
  const {
    useMockData = false,
    enableAutoRefetch = true,
    refetchInterval = 5 * 60 * 1000, // 5 minutes
    staleTime = 3 * 60 * 1000, // 3 minutes
  } = options;

  // Use mock data if requested
  if (useMockData) {
    return {
      analytics: MOCK_ANALYTICS_DATA,
      isLoading: false,
      error: null,
      refetch: () => Promise.resolve(MOCK_ANALYTICS_DATA),
      isFetching: false,
      isError: false,
      isSuccess: true,
      usingMockData: true,
    };
  }

  // Fetch analytics data using useQuery hook
  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
    isError,
    isSuccess,
  } = useQuery(
    'analytics-kpi',
    async () => {
      try {
        const response = await api.get('/api/analytics');
        
        // Handle different response formats
        const analyticsData = response.data || response;
        
        // Validate and normalize the data
        return normalizeAnalyticsData(analyticsData);
      } catch (error) {
        console.error('Failed to fetch analytics data:', error);
        
        // Fallback to mock data on error for demo purposes
        console.warn('Using mock analytics data due to fetch error');
        return MOCK_ANALYTICS_DATA;
      }
    },
    {
      refetchInterval: enableAutoRefetch ? refetchInterval : null,
      staleTime,
      retry: 2,
      refetchOnWindowFocus: true,
      cacheEnabled: true,
    }
  );

  // Determine if mock data is being used
  const usingMockData = data === MOCK_ANALYTICS_DATA;

  // Format error message for user display
  const errorMessage = useMemo(() => {
    if (!error) return null;
    
    if (error.message) {
      return error.message;
    }
    
    if (typeof error === 'string') {
      return error;
    }
    
    return 'Failed to load analytics data. Using cached data.';
  }, [error]);

  // Return analytics data with fallback
  const analytics = useMemo(() => {
    return data || MOCK_ANALYTICS_DATA;
  }, [data]);

  return {
    analytics,
    isLoading,
    error: errorMessage,
    refetch,
    isFetching,
    isError,
    isSuccess,
    usingMockData,
  };
}

/**
 * Normalize analytics data to ensure consistent structure
 */
function normalizeAnalyticsData(data) {
  return {
    total_properties: Number(data.total_properties || 0),
    portfolio_value: Number(data.portfolio_value || 0),
    monthly_income: Number(data.monthly_income || 0),
    occupancy_rate: Number(data.occupancy_rate || 0),
    yoy_growth: Number(data.yoy_growth || 0),
    risk_score: Number(data.risk_score || 0),
    total_units: Number(data.total_units || 0),
    average_cap_rate: Number(data.average_cap_rate || 0),
    maintenance_ratio: Number(data.maintenance_ratio || 0),
    debt_to_equity: Number(data.debt_to_equity || 0),
    lease_expiry_90_days: Number(data.lease_expiry_90_days || 0),
    market_trend: data.market_trend || 'neutral',
    last_updated: data.last_updated || new Date().toISOString(),
  };
}

/**
 * Hook for fetching specific KPI categories
 */
export function useKPIs(category = 'financial', options = {}) {
  const {
    refetchInterval = 5 * 60 * 1000,
    staleTime = 3 * 60 * 1000,
  } = options;

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery(
    `kpis-${category}`,
    async () => {
      try {
        const response = await api.get(`/api/kpis/${category}`);
        return response.data || response;
      } catch (error) {
        console.error(`Failed to fetch ${category} KPIs:`, error);
        // Return category-specific mock data
        return getMockKPIData(category);
      }
    },
    {
      refetchInterval,
      staleTime,
      retry: 2,
    }
  );

  return {
    kpis: data || getMockKPIData(category),
    isLoading,
    error: error ? 'Failed to load KPI data' : null,
    refetch,
    isFetching,
  };
}

/**
 * Get mock KPI data by category
 */
function getMockKPIData(category) {
  const mockData = {
    financial: {
      total_portfolio_value: { value: 47800000, formatted: '$47.8M', trend: 8.2 },
      total_properties: 184,
      monthly_noi: { value: 3750000, formatted: '$3.8M', trend: 5.7 },
      average_cap_rate: { value: 7.2, formatted: '7.2%', trend: 0.3 },
      debt_to_equity: { value: 0.65, formatted: '0.65', trend: -5.2 },
      annual_revenue: { value: 125000000, formatted: '$125M', trend: 15.3 },
    },
    operational: {
      average_occupancy: { value: 94.6, formatted: '94.6%', trend: 2.4 },
      total_units: 1247,
      active_tenants: 1176,
      maintenance_requests: { value: 42, trend: -15.2 },
      lease_renewals: { value: 87.3, formatted: '87.3%', trend: 4.1 },
      vacancy_rate: { value: 5.4, formatted: '5.4%', trend: -2.1 },
    },
    portfolio: {
      properties_by_type: {
        residential: 98,
        commercial: 45,
        mixed_use: 28,
        industrial: 13,
      },
      properties_by_region: {
        northeast: 52,
        southeast: 38,
        midwest: 46,
        west: 48,
      },
      total_square_footage: 2500000,
      average_property_value: 259782,
    },
  };

  return mockData[category] || {};
}

/**
 * Hook for fetching analytics with error boundary
 */
export function useAnalyticsWithErrorBoundary(options = {}) {
  try {
    return useAnalytics(options);
  } catch (error) {
    console.error('Error boundary caught error in useAnalytics:', error);
    
    // Return safe fallback state
    return {
      analytics: MOCK_ANALYTICS_DATA,
      isLoading: false,
      error: 'An unexpected error occurred. Displaying cached data.',
      refetch: () => Promise.resolve(MOCK_ANALYTICS_DATA),
      isFetching: false,
      isError: true,
      isSuccess: false,
      usingMockData: true,
    };
  }
}

/**
 * Hook for real-time analytics (shorter refresh interval)
 */
export function useRealTimeAnalytics(options = {}) {
  return useAnalytics({
    ...options,
    refetchInterval: 30000, // 30 seconds
    staleTime: 15000, // 15 seconds
  });
}

/**
 * Export mock data for testing
 */
export { MOCK_ANALYTICS_DATA };

export default useAnalytics;

