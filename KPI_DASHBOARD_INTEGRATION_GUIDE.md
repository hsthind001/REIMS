# 🎯 KPI Dashboard - Integration Guide

**Complete guide for integrating KPICard component with useAnalytics hook**

---

## 📦 What You Have

### Components
✅ **KPICard** - Beautiful, animated KPI display component  
✅ **KPICardGrid** - Responsive grid layout  
✅ **KPICardSkeleton** - Loading state skeleton  

### Hooks
✅ **useAnalytics** - Fetch analytics/KPI data with caching  
✅ **useKPIs** - Category-specific KPI data  
✅ **useRealTimeAnalytics** - Real-time updates (30s)  
✅ **useAnalyticsWithErrorBoundary** - Safe error handling  

---

## 🚀 Complete Integration Example

### Basic Dashboard

```jsx
import React from 'react';
import useAnalytics from '@/hooks/useAnalytics';
import KPICard, { KPICardGrid, KPICardSkeleton } from '@/components/KPICard';

function PortfolioDashboard() {
  const { analytics, isLoading, error, refetch, isFetching, usingMockData } = useAnalytics();

  // Loading state
  if (isLoading) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Portfolio Analytics</h1>
        <KPICardGrid columns={4}>
          <KPICardSkeleton color="blue" />
          <KPICardSkeleton color="green" />
          <KPICardSkeleton color="purple" />
          <KPICardSkeleton color="orange" />
        </KPICardGrid>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-red-800 mb-2">Error Loading Analytics</h3>
          <p className="text-red-700">{error}</p>
          <button
            onClick={refetch}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Success state
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Portfolio Analytics
            </h1>
            <p className="text-gray-600">
              Real-time overview of your property portfolio performance
            </p>
          </div>

          <button
            onClick={refetch}
            disabled={isFetching}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
          >
            {isFetching ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                Refreshing...
              </>
            ) : (
              'Refresh Data'
            )}
          </button>
        </div>

        {/* Mock Data Warning */}
        {usingMockData && (
          <div className="bg-yellow-100 border border-yellow-400 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-yellow-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="font-semibold text-yellow-800">Using Demo Data</h4>
                <p className="text-yellow-700 text-sm">
                  Backend API unavailable. Displaying mock data for demonstration.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Primary KPIs */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Primary Metrics
          </h2>
          <KPICardGrid columns={4}>
            <KPICard
              title="Total Properties"
              value={analytics.total_properties}
              trend={analytics.yoy_growth}
              color="blue"
              subtitle={`${analytics.yoy_growth}% YoY growth`}
            />

            <KPICard
              title="Portfolio Value"
              value={analytics.portfolio_value}
              unit="$"
              trend={analytics.yoy_growth}
              color="green"
              subtitle="Total asset value"
            />

            <KPICard
              title="Monthly Income"
              value={analytics.monthly_income}
              unit="$"
              trend={5.7}
              color="purple"
              subtitle="Net operating income"
            />

            <KPICard
              title="Occupancy Rate"
              value={analytics.occupancy_rate * 100}
              unit="%"
              trend={2.4}
              color="indigo"
              subtitle={`${analytics.total_units} total units`}
            />
          </KPICardGrid>
        </section>

        {/* Secondary KPIs */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Performance Indicators
          </h2>
          <KPICardGrid columns={4}>
            <KPICard
              title="Risk Score"
              value={analytics.risk_score}
              trend={-5.3}
              trendUp={true} // Lower is better
              color="green"
              subtitle="Risk assessment"
            />

            <KPICard
              title="Average Cap Rate"
              value={analytics.average_cap_rate}
              unit="%"
              trend={0.3}
              color="blue"
              subtitle="Portfolio average"
            />

            <KPICard
              title="Debt-to-Equity"
              value={(analytics.debt_to_equity * 100).toFixed(1)}
              unit="%"
              trend={-5.2}
              trendUp={true} // Lower is better
              color="purple"
              subtitle="Financial leverage"
            />

            <KPICard
              title="Lease Expiry (90d)"
              value={analytics.lease_expiry_90_days}
              trend={-12}
              trendUp={true}
              color="orange"
              subtitle="Expiring soon"
            />
          </KPICardGrid>
        </section>

        {/* Market Trend */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Market Overview
          </h2>
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-1">
                  Market Trend
                </h3>
                <p className="text-gray-600">
                  Last updated: {new Date(analytics.last_updated).toLocaleString()}
                </p>
              </div>
              <div className={`
                px-6 py-3 rounded-lg font-bold text-xl
                ${analytics.market_trend === 'bullish' ? 'bg-green-100 text-green-700' : ''}
                ${analytics.market_trend === 'bearish' ? 'bg-red-100 text-red-700' : ''}
                ${analytics.market_trend === 'neutral' ? 'bg-gray-100 text-gray-700' : ''}
              `}>
                {analytics.market_trend.toUpperCase()}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default PortfolioDashboard;
```

---

## 🎨 Advanced Examples

### 1. Real-Time Dashboard

```jsx
import { useRealTimeAnalytics } from '@/hooks/useAnalytics';

function RealTimeDashboard() {
  const { analytics, isFetching } = useRealTimeAnalytics();

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-3xl font-bold">Real-Time Analytics</h1>
        {isFetching && (
          <div className="flex items-center gap-2 text-sm text-blue-600">
            <div className="animate-pulse w-2 h-2 bg-blue-600 rounded-full"></div>
            Live
          </div>
        )}
      </div>

      <p className="text-sm text-gray-600 mb-6">
        Updates automatically every 30 seconds
      </p>

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Properties"
          value={analytics.total_properties}
          color="blue"
        />
        {/* More cards... */}
      </KPICardGrid>
    </div>
  );
}
```

### 2. Category-Specific Dashboards

```jsx
import { useKPIs } from '@/hooks/useAnalytics';

function FinancialDashboard() {
  const { kpis, isLoading } = useKPIs('financial');

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Financial Performance</h1>

      <KPICardGrid columns={3}>
        <KPICard
          title="Portfolio Value"
          value={kpis.total_portfolio_value?.value || 0}
          unit="$"
          trend={kpis.total_portfolio_value?.trend}
          color="blue"
          loading={isLoading}
          subtitle={kpis.total_portfolio_value?.formatted}
        />

        <KPICard
          title="Monthly NOI"
          value={kpis.monthly_noi?.value || 0}
          unit="$"
          trend={kpis.monthly_noi?.trend}
          color="green"
          loading={isLoading}
        />

        <KPICard
          title="Annual Revenue"
          value={kpis.annual_revenue?.value || 0}
          unit="$"
          trend={kpis.annual_revenue?.trend}
          color="purple"
          loading={isLoading}
        />
      </KPICardGrid>
    </div>
  );
}
```

### 3. Multi-Category Dashboard

```jsx
import useAnalytics, { useKPIs } from '@/hooks/useAnalytics';

function ComprehensiveDashboard() {
  const { analytics } = useAnalytics();
  const { kpis: financial } = useKPIs('financial');
  const { kpis: operational } = useKPIs('operational');

  return (
    <div className="p-6 space-y-8">
      {/* Overview */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Portfolio Overview</h2>
        <KPICardGrid columns={4}>
          <KPICard
            title="Total Properties"
            value={analytics.total_properties}
            trend={analytics.yoy_growth}
            color="blue"
          />
          <KPICard
            title="Portfolio Value"
            value={analytics.portfolio_value}
            unit="$"
            trend={analytics.yoy_growth}
            color="green"
          />
          {/* ... */}
        </KPICardGrid>
      </section>

      {/* Financial */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Financial Metrics</h2>
        <KPICardGrid columns={3}>
          <KPICard
            title="Monthly NOI"
            value={financial.monthly_noi?.value}
            unit="$"
            trend={financial.monthly_noi?.trend}
            color="green"
          />
          {/* ... */}
        </KPICardGrid>
      </section>

      {/* Operational */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Operational Metrics</h2>
        <KPICardGrid columns={3}>
          <KPICard
            title="Occupancy Rate"
            value={operational.average_occupancy?.value}
            unit="%"
            trend={operational.average_occupancy?.trend}
            color="purple"
          />
          {/* ... */}
        </KPICardGrid>
      </section>
    </div>
  );
}
```

---

## 🔧 Configuration Tips

### 1. Adjust Refresh Interval

```jsx
// Fast refresh (1 minute)
const { analytics } = useAnalytics({
  refetchInterval: 60000,
  staleTime: 30000,
});

// Slow refresh (10 minutes)
const { analytics } = useAnalytics({
  refetchInterval: 600000,
  staleTime: 300000,
});

// No auto-refresh
const { analytics } = useAnalytics({
  enableAutoRefetch: false,
});
```

### 2. Use Mock Data for Development

```jsx
const isDev = import.meta.env.DEV;
const backendAvailable = false; // Set based on health check

const { analytics } = useAnalytics({
  useMockData: isDev && !backendAvailable,
});
```

### 3. Error Boundary Protection

```jsx
import { useAnalyticsWithErrorBoundary } from '@/hooks/useAnalytics';

function CriticalDashboard() {
  // Will never crash, always returns valid data
  const { analytics, error } = useAnalyticsWithErrorBoundary();

  return (
    <div>
      {error && <ErrorBanner message={error} />}
      <KPICard title="Properties" value={analytics.total_properties} />
    </div>
  );
}
```

---

## 🎯 Best Practices

### 1. Always Show Loading State

```jsx
✅ Good:
if (isLoading) {
  return (
    <KPICardGrid columns={4}>
      <KPICardSkeleton />
      <KPICardSkeleton />
      <KPICardSkeleton />
      <KPICardSkeleton />
    </KPICardGrid>
  );
}

❌ Bad:
// No loading state, blank screen
```

### 2. Handle Errors Gracefully

```jsx
✅ Good:
if (error) {
  return (
    <div className="error-container">
      <p>{error}</p>
      <button onClick={refetch}>Retry</button>
    </div>
  );
}

❌ Bad:
// Silent failure
```

### 3. Show Refresh Indicator

```jsx
✅ Good:
<div className="flex items-center gap-2">
  <h1>Dashboard</h1>
  {isFetching && <span className="text-blue-600">Updating...</span>}
</div>

❌ Bad:
// User doesn't know data is being updated
```

### 4. Normalize Occupancy Rate

```jsx
✅ Good:
<KPICard
  title="Occupancy"
  value={analytics.occupancy_rate * 100}  // 0.946 → 94.6
  unit="%"
/>

❌ Bad:
<KPICard
  title="Occupancy"
  value={analytics.occupancy_rate}  // Shows 0.946
  unit="%"
/>
```

### 5. Use Appropriate Colors

```jsx
✅ Good:
<KPICard title="Revenue" color="green" />     // Positive metric
<KPICard title="Risk Score" color="orange" />  // Warning metric
<KPICard title="Expenses" color="red" />       // Cost metric

❌ Bad:
<KPICard title="Revenue" color="red" />        // Confusing
```

---

## 🧪 Testing Guide

### 1. Test with Mock Data

```jsx
// Enable mock data for testing
const { analytics } = useAnalytics({ useMockData: true });
```

### 2. Test Loading States

```jsx
// Check loading skeleton display
if (isLoading) {
  return <KPICardSkeleton />;
}
```

### 3. Test Error Handling

```jsx
// Simulate error by disconnecting backend
// Verify error message displays
// Verify retry button works
```

### 4. Test Auto-Refresh

```jsx
// Set fast refresh interval
const { analytics, isFetching } = useAnalytics({
  refetchInterval: 5000, // 5 seconds for testing
});

// Watch for isFetching indicator
console.log('Fetching:', isFetching);
```

---

## 📊 Data Normalization

### Convert Values for Display

```jsx
// Occupancy rate (0-1 → percentage)
value={analytics.occupancy_rate * 100}

// Debt-to-equity (decimal → percentage)
value={(analytics.debt_to_equity * 100).toFixed(1)}

// Currency (auto-formatted by KPICard)
value={analytics.portfolio_value}
unit="$"

// Percentage (auto-formatted by KPICard)
value={analytics.average_cap_rate}
unit="%"
```

---

## 🚀 Deployment Checklist

- [ ] Backend API endpoint `/api/analytics` implemented
- [ ] CORS configured for frontend origin
- [ ] API returns correct data structure
- [ ] Frontend can reach backend (check port/URL)
- [ ] Loading states tested
- [ ] Error handling tested
- [ ] Mock data fallback works
- [ ] Auto-refresh interval appropriate for production
- [ ] Cache time appropriate for data freshness
- [ ] All KPI cards display correctly
- [ ] Number formatting correct
- [ ] Trend indicators work
- [ ] Color themes appropriate
- [ ] Responsive on mobile/tablet/desktop

---

## 🎉 Summary

You now have a complete, production-ready KPI dashboard solution:

✅ **KPICard Component** - Beautiful animated cards  
✅ **useAnalytics Hook** - Smart data fetching  
✅ **Auto-Refresh** - Background updates  
✅ **Error Handling** - Graceful failures  
✅ **Mock Data** - Works without backend  
✅ **Loading States** - Smooth UX  
✅ **Real-Time Mode** - For live dashboards  
✅ **Category KPIs** - Flexible organization  

**Start building your dashboard today!** 🚀

---

## 📚 Quick Links

- **KPICard Documentation:** `frontend/src/components/KPICard.README.md`
- **useAnalytics Documentation:** `frontend/src/hooks/useAnalytics.README.md`
- **KPICard Examples:** `frontend/src/components/KPICard.examples.jsx`
- **useAnalytics Examples:** `frontend/src/hooks/useAnalytics.examples.jsx`
- **Demo Components:**
  - `frontend/src/components/KPICardDemo.jsx`
  - See examples files for hook demos

