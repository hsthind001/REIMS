/**
 * useAnalytics Hook - Usage Examples
 * 
 * Demonstrates various use cases for the analytics data fetching hook
 */

import React from 'react';
import useAnalytics, {
  useKPIs,
  useAnalyticsWithErrorBoundary,
  useRealTimeAnalytics,
  MOCK_ANALYTICS_DATA,
} from './useAnalytics';
import KPICard, { KPICardGrid } from '../components/KPICard';

// ============================================================================
// Example 1: Basic Usage
// ============================================================================

export function BasicAnalyticsDashboard() {
  const { analytics, isLoading, error, refetch } = useAnalytics();

  if (isLoading) {
    return <div>Loading analytics...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    );
  }

  return (
    <div>
      <h1>Analytics Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <h3>Total Properties</h3>
          <p className="text-2xl font-bold">{analytics.total_properties}</p>
        </div>
        <div>
          <h3>Portfolio Value</h3>
          <p className="text-2xl font-bold">
            ${(analytics.portfolio_value / 1000000).toFixed(1)}M
          </p>
        </div>
        <div>
          <h3>Occupancy Rate</h3>
          <p className="text-2xl font-bold">
            {(analytics.occupancy_rate * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Example 2: With KPI Cards
// ============================================================================

export function KPIDashboard() {
  const { analytics, isLoading, isFetching, refetch } = useAnalytics();

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Portfolio Analytics</h1>
        <button
          onClick={refetch}
          disabled={isFetching}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {isFetching ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          trend={analytics.yoy_growth}
          color="blue"
          loading={isLoading}
        />

        <KPICard
          title="Portfolio Value"
          value={analytics.portfolio_value}
          unit="$"
          trend={analytics.yoy_growth}
          color="green"
          loading={isLoading}
        />

        <KPICard
          title="Monthly Income"
          value={analytics.monthly_income}
          unit="$"
          trend={5.7}
          color="purple"
          loading={isLoading}
        />

        <KPICard
          title="Occupancy Rate"
          value={analytics.occupancy_rate * 100}
          unit="%"
          trend={2.4}
          color="indigo"
          loading={isLoading}
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 3: With Mock Data (Demo Mode)
// ============================================================================

export function DemoAnalyticsDashboard() {
  const { analytics, usingMockData } = useAnalytics({
    useMockData: true, // Force mock data for demo
  });

  return (
    <div className="p-6">
      {usingMockData && (
        <div className="bg-yellow-100 border border-yellow-400 rounded p-3 mb-4">
          ⚠️ Using mock data for demonstration
        </div>
      )}

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          trend={12}
          color="blue"
        />

        <KPICard
          title="Portfolio Value"
          value={analytics.portfolio_value}
          unit="$"
          trend={8.2}
          color="green"
        />

        <KPICard
          title="Occupancy Rate"
          value={analytics.occupancy_rate * 100}
          unit="%"
          trend={2.4}
          color="purple"
        />

        <KPICard
          title="Risk Score"
          value={analytics.risk_score}
          trend={-5.3}
          trendUp={true} // Lower risk is better
          color="green"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 4: With Error Boundary
// ============================================================================

export function SafeAnalyticsDashboard() {
  const { analytics, isLoading, error, usingMockData } = useAnalyticsWithErrorBoundary();

  return (
    <div className="p-6">
      {error && (
        <div className="bg-red-100 border border-red-400 rounded p-3 mb-4">
          {error}
        </div>
      )}

      {usingMockData && !error && (
        <div className="bg-blue-100 border border-blue-400 rounded p-3 mb-4">
          📊 Displaying cached data
        </div>
      )}

      <KPICardGrid columns={3}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          color="blue"
          loading={isLoading}
        />

        <KPICard
          title="Portfolio Value"
          value={analytics.portfolio_value}
          unit="$"
          color="green"
          loading={isLoading}
        />

        <KPICard
          title="Monthly Income"
          value={analytics.monthly_income}
          unit="$"
          color="purple"
          loading={isLoading}
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 5: Real-Time Analytics
// ============================================================================

export function RealTimeDashboard() {
  const { analytics, isFetching, isLoading } = useRealTimeAnalytics();

  return (
    <div className="p-6">
      <div className="flex items-center gap-2 mb-6">
        <h1 className="text-3xl font-bold">Real-Time Analytics</h1>
        {isFetching && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
            Updating...
          </div>
        )}
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Updates every 30 seconds
      </p>

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          trend={analytics.yoy_growth}
          color="blue"
          loading={isLoading}
        />

        <KPICard
          title="Portfolio Value"
          value={analytics.portfolio_value}
          unit="$"
          trend={analytics.yoy_growth}
          color="green"
          loading={isLoading}
        />

        <KPICard
          title="Occupancy Rate"
          value={analytics.occupancy_rate * 100}
          unit="%"
          trend={2.4}
          color="purple"
          loading={isLoading}
        />

        <KPICard
          title="Risk Score"
          value={analytics.risk_score}
          trend={-5.3}
          trendUp={true}
          color="orange"
          loading={isLoading}
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 6: Using KPIs Hook (Category-Specific)
// ============================================================================

export function FinancialKPIsDashboard() {
  const { kpis, isLoading, refetch } = useKPIs('financial');

  if (isLoading) {
    return <div>Loading financial KPIs...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Financial KPIs</h1>
        <button onClick={refetch} className="px-4 py-2 bg-blue-500 text-white rounded">
          Refresh
        </button>
      </div>

      <KPICardGrid columns={3}>
        <KPICard
          title="Total Portfolio Value"
          value={kpis.total_portfolio_value?.value || 0}
          unit="$"
          trend={kpis.total_portfolio_value?.trend}
          color="blue"
          subtitle={kpis.total_portfolio_value?.formatted}
        />

        <KPICard
          title="Monthly NOI"
          value={kpis.monthly_noi?.value || 0}
          unit="$"
          trend={kpis.monthly_noi?.trend}
          color="green"
          subtitle={kpis.monthly_noi?.formatted}
        />

        <KPICard
          title="Average Cap Rate"
          value={kpis.average_cap_rate?.value || 0}
          unit="%"
          trend={kpis.average_cap_rate?.trend}
          color="purple"
        />

        <KPICard
          title="Annual Revenue"
          value={kpis.annual_revenue?.value || 0}
          unit="$"
          trend={kpis.annual_revenue?.trend}
          color="indigo"
        />

        <KPICard
          title="Debt-to-Equity"
          value={kpis.debt_to_equity?.value || 0}
          trend={kpis.debt_to_equity?.trend}
          trendUp={kpis.debt_to_equity?.trend < 0} // Lower is better
          color="orange"
        />

        <KPICard
          title="Total Properties"
          value={kpis.total_properties || 0}
          color="blue"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 7: Multiple Categories
// ============================================================================

export function ComprehensiveDashboard() {
  const { kpis: financial, isLoading: loadingFinancial } = useKPIs('financial');
  const { kpis: operational, isLoading: loadingOperational } = useKPIs('operational');
  const { kpis: portfolio, isLoading: loadingPortfolio } = useKPIs('portfolio');

  const isLoading = loadingFinancial || loadingOperational || loadingPortfolio;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-3xl font-bold">Comprehensive Analytics</h1>

      {/* Financial KPIs */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Financial Metrics</h2>
        <KPICardGrid columns={4}>
          <KPICard
            title="Portfolio Value"
            value={financial.total_portfolio_value?.value || 0}
            unit="$"
            trend={financial.total_portfolio_value?.trend}
            color="blue"
            loading={isLoading}
          />

          <KPICard
            title="Monthly NOI"
            value={financial.monthly_noi?.value || 0}
            unit="$"
            trend={financial.monthly_noi?.trend}
            color="green"
            loading={isLoading}
          />

          <KPICard
            title="Cap Rate"
            value={financial.average_cap_rate?.value || 0}
            unit="%"
            trend={financial.average_cap_rate?.trend}
            color="purple"
            loading={isLoading}
          />

          <KPICard
            title="Annual Revenue"
            value={financial.annual_revenue?.value || 0}
            unit="$"
            trend={financial.annual_revenue?.trend}
            color="indigo"
            loading={isLoading}
          />
        </KPICardGrid>
      </section>

      {/* Operational KPIs */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Operational Metrics</h2>
        <KPICardGrid columns={4}>
          <KPICard
            title="Occupancy Rate"
            value={operational.average_occupancy?.value || 0}
            unit="%"
            trend={operational.average_occupancy?.trend}
            color="green"
            loading={isLoading}
          />

          <KPICard
            title="Active Tenants"
            value={operational.active_tenants || 0}
            color="blue"
            loading={isLoading}
          />

          <KPICard
            title="Maintenance Requests"
            value={operational.maintenance_requests?.value || 0}
            trend={operational.maintenance_requests?.trend}
            trendUp={operational.maintenance_requests?.trend < 0}
            color="orange"
            loading={isLoading}
          />

          <KPICard
            title="Lease Renewals"
            value={operational.lease_renewals?.value || 0}
            unit="%"
            trend={operational.lease_renewals?.trend}
            color="purple"
            loading={isLoading}
          />
        </KPICardGrid>
      </section>

      {/* Portfolio Distribution */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Portfolio Distribution</h2>
        <KPICardGrid columns={4}>
          <KPICard
            title="Residential"
            value={portfolio.properties_by_type?.residential || 0}
            color="blue"
            loading={isLoading}
            subtitle="properties"
          />

          <KPICard
            title="Commercial"
            value={portfolio.properties_by_type?.commercial || 0}
            color="green"
            loading={isLoading}
            subtitle="properties"
          />

          <KPICard
            title="Mixed Use"
            value={portfolio.properties_by_type?.mixed_use || 0}
            color="purple"
            loading={isLoading}
            subtitle="properties"
          />

          <KPICard
            title="Industrial"
            value={portfolio.properties_by_type?.industrial || 0}
            color="orange"
            loading={isLoading}
            subtitle="properties"
          />
        </KPICardGrid>
      </section>
    </div>
  );
}

// ============================================================================
// Example 8: With Manual Refetch and Status Indicator
// ============================================================================

export function InteractiveDashboard() {
  const { analytics, isLoading, isFetching, error, refetch, usingMockData } = useAnalytics();
  const [lastRefresh, setLastRefresh] = React.useState(new Date());

  const handleRefresh = async () => {
    await refetch();
    setLastRefresh(new Date());
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Portfolio Dashboard</h1>
          <p className="text-sm text-gray-600">
            Last updated: {lastRefresh.toLocaleTimeString()}
            {usingMockData && ' (Mock Data)'}
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
        >
          {isFetching ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              Refreshing...
            </>
          ) : (
            'Refresh Now'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-yellow-100 border border-yellow-400 rounded p-4 mb-4">
          ⚠️ {error}
        </div>
      )}

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          trend={analytics.yoy_growth}
          color="blue"
          loading={isLoading}
        />

        <KPICard
          title="Portfolio Value"
          value={analytics.portfolio_value}
          unit="$"
          trend={analytics.yoy_growth}
          color="green"
          loading={isLoading}
        />

        <KPICard
          title="Monthly Income"
          value={analytics.monthly_income}
          unit="$"
          trend={5.7}
          color="purple"
          loading={isLoading}
        />

        <KPICard
          title="Occupancy Rate"
          value={analytics.occupancy_rate * 100}
          unit="%"
          trend={2.4}
          color="indigo"
          loading={isLoading}
        />
      </KPICardGrid>
    </div>
  );
}

