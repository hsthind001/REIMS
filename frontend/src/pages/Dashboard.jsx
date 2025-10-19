import React, { useState, useEffect } from 'react';
import useAnalytics from '../hooks/useAnalytics';
import KPICard, { KPICardGrid, KPICardSkeleton } from '../components/KPICard';

/**
 * REIMS Dashboard - Main Dashboard Page
 * 
 * Features:
 * - Real-time analytics KPI cards
 * - Auto-updating date/time
 * - System status indicator
 * - Auto-refresh every 5 minutes
 * - Responsive layout
 * - Error handling with retry
 * - Loading states
 * - Accessibility features
 */
export default function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showError, setShowError] = useState(false);

  // Fetch analytics data with auto-refresh
  const {
    analytics,
    isLoading,
    error,
    refetch,
    isFetching,
    usingMockData,
  } = useAnalytics({
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 3 * 60 * 1000, // 3 minutes
  });

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Show error toast
  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => setShowError(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Determine system status based on data
  const getSystemStatus = () => {
    if (error) return { color: 'red', label: 'Error', bgColor: 'bg-red-500' };
    if (usingMockData) return { color: 'yellow', label: 'Demo', bgColor: 'bg-yellow-500' };
    if (isFetching) return { color: 'yellow', label: 'Updating', bgColor: 'bg-yellow-500' };
    return { color: 'green', label: 'Online', bgColor: 'bg-green-500' };
  };

  const systemStatus = getSystemStatus();

  // Icons for KPI cards
  const DollarIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );

  const BuildingIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );

  const ChartIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );

  const TrendingIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Error Toast */}
      {showError && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
          <div className="bg-red-500 text-white px-6 py-4 rounded-lg shadow-2xl flex items-start gap-3 max-w-md">
            <svg className="w-6 h-6 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-semibold mb-1">Error Loading Data</h4>
              <p className="text-sm text-red-100">{error}</p>
            </div>
            <button
              onClick={() => setShowError(false)}
              className="ml-auto text-white hover:text-red-200"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <header className="mb-8" role="banner">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              {/* Title and Time */}
              <div className="flex-1">
                <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
                  REIMS Dashboard
                </h1>
                <div className="flex items-center gap-2 text-gray-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <time
                    dateTime={currentTime.toISOString()}
                    aria-live="polite"
                    aria-atomic="true"
                    className="font-medium"
                  >
                    {currentTime.toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                    {' • '}
                    {currentTime.toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </time>
                </div>
              </div>

              {/* System Status and Actions */}
              <div className="flex items-center gap-4">
                {/* System Status Indicator */}
                <div
                  className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg"
                  role="status"
                  aria-live="polite"
                >
                  <div className="relative">
                    <div className={`w-3 h-3 ${systemStatus.bgColor} rounded-full`}></div>
                    <div className={`absolute inset-0 ${systemStatus.bgColor} rounded-full animate-ping opacity-75`}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    System: <span className="font-semibold">{systemStatus.label}</span>
                  </span>
                </div>

                {/* Refresh Button */}
                <button
                  onClick={refetch}
                  disabled={isFetching}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
                  aria-label="Refresh dashboard data"
                >
                  <svg
                    className={`w-5 h-5 ${isFetching ? 'animate-spin' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span className="hidden sm:inline">
                    {isFetching ? 'Refreshing...' : 'Refresh'}
                  </span>
                </button>
              </div>
            </div>

            {/* Mock Data Warning */}
            {usingMockData && (
              <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-center gap-2 text-yellow-800">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm font-medium">
                    Using demo data - Backend API unavailable
                  </span>
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Main Content */}
        <main role="main">
          {/* Loading State */}
          {isLoading ? (
            <section aria-label="Loading dashboard data">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Key Performance Indicators</h2>
              <KPICardGrid columns={4}>
                <KPICardSkeleton color="blue" />
                <KPICardSkeleton color="green" />
                <KPICardSkeleton color="purple" />
                <KPICardSkeleton color="indigo" />
              </KPICardGrid>
            </section>
          ) : error && !analytics ? (
            /* Error State */
            <section
              className="bg-red-50 border border-red-200 rounded-xl p-8 text-center"
              role="alert"
              aria-live="assertive"
            >
              <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h2 className="text-2xl font-bold text-red-900 mb-2">
                Failed to Load Dashboard Data
              </h2>
              <p className="text-red-700 mb-6">{error}</p>
              <button
                onClick={refetch}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition-colors"
              >
                Try Again
              </button>
            </section>
          ) : (
            /* Success State */
            <div className="space-y-8">
              {/* KPI Cards Section */}
              <section aria-labelledby="kpi-heading">
                <h2 id="kpi-heading" className="text-2xl font-bold text-gray-800 mb-4">
                  Key Performance Indicators
                </h2>
                <KPICardGrid columns={4}>
                  <KPICard
                    title="Portfolio Value"
                    value={analytics.portfolio_value}
                    unit="$"
                    trend={analytics.yoy_growth}
                    trendUp={analytics.yoy_growth >= 0}
                    icon={DollarIcon}
                    color="blue"
                    subtitle={`${analytics.total_properties} properties`}
                    aria-label={`Portfolio Value: $${(analytics.portfolio_value / 1000000).toFixed(1)} million, trending ${analytics.yoy_growth >= 0 ? 'up' : 'down'} ${Math.abs(analytics.yoy_growth)}%`}
                  />

                  <KPICard
                    title="Total Properties"
                    value={analytics.total_properties}
                    trend={12.3}
                    trendUp={true}
                    icon={BuildingIcon}
                    color="green"
                    subtitle="Active portfolio"
                    aria-label={`Total Properties: ${analytics.total_properties}, trending up 12.3%`}
                  />

                  <KPICard
                    title="Monthly Income"
                    value={analytics.monthly_income}
                    unit="$"
                    trend={8.4}
                    trendUp={true}
                    icon={DollarIcon}
                    color="purple"
                    subtitle="Net operating income"
                    aria-label={`Monthly Income: $${(analytics.monthly_income / 1000000).toFixed(1)} million, trending up 8.4%`}
                  />

                  <KPICard
                    title="Occupancy Rate"
                    value={analytics.occupancy_rate * 100}
                    unit="%"
                    trend={2.4}
                    trendUp={true}
                    icon={ChartIcon}
                    color="indigo"
                    subtitle={`${analytics.total_units} total units`}
                    aria-label={`Occupancy Rate: ${(analytics.occupancy_rate * 100).toFixed(1)}%, trending up 2.4%`}
                  />
                </KPICardGrid>
              </section>

              {/* Quick Stats Section */}
              <section aria-labelledby="quick-stats-heading">
                <h2 id="quick-stats-heading" className="text-2xl font-bold text-gray-800 mb-4">
                  Quick Stats
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* YoY Growth */}
                  <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-600">YoY Growth</h3>
                      <TrendingIcon className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-bold text-green-600">
                        +{analytics.yoy_growth.toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-500">vs last year</span>
                    </div>
                    <div className="mt-2 flex items-center gap-1 text-sm text-green-700">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                      <span>Strong performance</span>
                    </div>
                  </div>

                  {/* Available Properties */}
                  <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-600">Available Properties</h3>
                      <BuildingIcon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-bold text-blue-600">23</span>
                      <span className="text-sm text-gray-500">ready to lease</span>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      {((23 / analytics.total_properties) * 100).toFixed(1)}% of portfolio
                    </div>
                  </div>

                  {/* Risk Score */}
                  <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-600">Risk Score</h3>
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-bold text-green-600">
                        {analytics.risk_score.toFixed(1)}
                      </span>
                      <span className="text-sm text-gray-500">/ 10</span>
                    </div>
                    <div className="mt-2 flex items-center gap-1 text-sm text-green-700">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Low risk portfolio</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* Recent Activity Section */}
              <section aria-labelledby="recent-activity-heading">
                <h2 id="recent-activity-heading" className="text-2xl font-bold text-gray-800 mb-4">
                  Recent Activity
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Latest Documents */}
                  <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Latest Documents</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="space-y-3">
                      <ActivityItem
                        title="Property_Agreement_184.pdf"
                        subtitle="Uploaded 2 hours ago"
                        icon="document"
                      />
                      <ActivityItem
                        title="Financial_Report_Q3.xlsx"
                        subtitle="Uploaded 5 hours ago"
                        icon="document"
                      />
                      <ActivityItem
                        title="Lease_Contract_Update.pdf"
                        subtitle="Uploaded yesterday"
                        icon="document"
                      />
                    </div>
                    <button className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View all documents →
                    </button>
                  </div>

                  {/* Latest Alerts */}
                  <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Latest Alerts</h3>
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                    </div>
                    <div className="space-y-3">
                      <ActivityItem
                        title="Lease expiring in 30 days"
                        subtitle="Property #127 - Action required"
                        icon="alert"
                        iconColor="text-yellow-600"
                      />
                      <ActivityItem
                        title="Maintenance completed"
                        subtitle="Property #89 - 1 hour ago"
                        icon="check"
                        iconColor="text-green-600"
                      />
                      <ActivityItem
                        title="New tenant inquiry"
                        subtitle="Property #45 - 3 hours ago"
                        icon="user"
                        iconColor="text-blue-600"
                      />
                    </div>
                    <button className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View all alerts →
                    </button>
                  </div>
                </div>
              </section>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-500" role="contentinfo">
          <p>
            Auto-refreshes every 5 minutes • Last updated: {new Date(analytics?.last_updated || new Date()).toLocaleString()}
          </p>
        </footer>
      </div>
    </div>
  );
}

/**
 * Activity Item Component
 */
function ActivityItem({ title, subtitle, icon, iconColor = 'text-gray-400' }) {
  const getIcon = () => {
    switch (icon) {
      case 'document':
        return (
          <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'alert':
        return (
          <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case 'check':
        return (
          <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'user':
        return (
          <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div className="flex-shrink-0 mt-0.5">
        {getIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{title}</p>
        <p className="text-xs text-gray-500">{subtitle}</p>
      </div>
    </div>
  );
}

