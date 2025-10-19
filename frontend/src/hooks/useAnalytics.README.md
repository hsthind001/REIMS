# useAnalytics Hook - Documentation

**Custom React hook for fetching and managing analytics/KPI data with caching, auto-refresh, and error handling.**

---

## 🎯 Features

✅ **Auto-Fetch** - Fetches from `GET /api/analytics`  
✅ **Loading States** - Track loading and fetching states  
✅ **Error Handling** - User-friendly error messages  
✅ **Auto-Refetch** - Every 5 minutes (configurable)  
✅ **Caching** - 3-minute cache (configurable)  
✅ **Mock Data Fallback** - Demo mode when API unavailable  
✅ **Error Boundary** - Safe error handling wrapper  
✅ **Manual Refetch** - Refresh on demand  
✅ **Type Safety** - Normalized data structure  

---

## 🚀 Quick Start

### Basic Usage

```jsx
import useAnalytics from '@/hooks/useAnalytics';
import KPICard, { KPICardGrid } from '@/components/KPICard';

function Dashboard() {
  const { analytics, isLoading, error, refetch } = useAnalytics();

  if (isLoading) {
    return <div>Loading...</div>;
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
    <KPICardGrid columns={4}>
      <KPICard
        title="Total Properties"
        value={analytics.total_properties}
        color="blue"
      />
      
      <KPICard
        title="Portfolio Value"
        value={analytics.portfolio_value}
        unit="$"
        color="green"
      />
      
      <KPICard
        title="Occupancy Rate"
        value={analytics.occupancy_rate * 100}
        unit="%"
        color="purple"
      />
      
      <KPICard
        title="Risk Score"
        value={analytics.risk_score}
        color="orange"
      />
    </KPICardGrid>
  );
}
```

---

## 📖 API Reference

### useAnalytics(options)

Main hook for fetching analytics data.

#### Parameters

```typescript
options: {
  useMockData?: boolean,          // Force mock data (default: false)
  enableAutoRefetch?: boolean,    // Enable auto-refetch (default: true)
  refetchInterval?: number,       // Refetch interval in ms (default: 300000 = 5 min)
  staleTime?: number,            // Cache duration in ms (default: 180000 = 3 min)
}
```

#### Return Object

```typescript
{
  analytics: {
    total_properties: number,
    portfolio_value: number,
    monthly_income: number,
    occupancy_rate: number,      // 0-1 (e.g., 0.946 = 94.6%)
    yoy_growth: number,
    risk_score: number,
    total_units: number,
    average_cap_rate: number,
    maintenance_ratio: number,
    debt_to_equity: number,
    lease_expiry_90_days: number,
    market_trend: string,
    last_updated: string,        // ISO date
  },
  isLoading: boolean,            // Initial load state
  error: string | null,          // User-friendly error message
  refetch: () => Promise,        // Manual refetch function
  isFetching: boolean,           // Background fetch state
  isError: boolean,              // Error flag
  isSuccess: boolean,            // Success flag
  usingMockData: boolean,        // Whether mock data is active
}
```

---

## 📊 Analytics Data Structure

### Core Metrics

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `total_properties` | `number` | Total number of properties | `184` |
| `portfolio_value` | `number` | Total portfolio value in dollars | `47800000` |
| `monthly_income` | `number` | Monthly income in dollars | `3750000` |
| `occupancy_rate` | `number` | Occupancy rate (0-1) | `0.946` |
| `yoy_growth` | `number` | Year-over-year growth percentage | `8.2` |
| `risk_score` | `number` | Portfolio risk score | `23.5` |

### Additional Metrics

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `total_units` | `number` | Total rental units | `1247` |
| `average_cap_rate` | `number` | Average capitalization rate | `7.2` |
| `maintenance_ratio` | `number` | Maintenance cost ratio | `0.12` |
| `debt_to_equity` | `number` | Debt-to-equity ratio | `0.65` |
| `lease_expiry_90_days` | `number` | Leases expiring in 90 days | `42` |
| `market_trend` | `string` | Market trend indicator | `"bullish"` |
| `last_updated` | `string` | Last update timestamp (ISO) | `"2025-10-12T..."` |

---

## 🎨 Usage Examples

### 1. Basic Dashboard

```jsx
function Dashboard() {
  const { analytics, isLoading } = useAnalytics();

  return (
    <div>
      <h1>Portfolio Analytics</h1>
      <p>Properties: {analytics.total_properties}</p>
      <p>Value: ${(analytics.portfolio_value / 1000000).toFixed(1)}M</p>
      <p>Occupancy: {(analytics.occupancy_rate * 100).toFixed(1)}%</p>
    </div>
  );
}
```

### 2. With KPI Cards

```jsx
function KPIDashboard() {
  const { analytics, isLoading } = useAnalytics();

  return (
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
  );
}
```

### 3. Demo Mode (Mock Data)

```jsx
function DemoDashboard() {
  const { analytics, usingMockData } = useAnalytics({
    useMockData: true,
  });

  return (
    <div>
      {usingMockData && (
        <div className="bg-yellow-100 p-3 rounded">
          ⚠️ Using mock data for demonstration
        </div>
      )}
      
      <KPICardGrid columns={4}>
        <KPICard title="Properties" value={analytics.total_properties} />
        <KPICard title="Value" value={analytics.portfolio_value} unit="$" />
        <KPICard title="Income" value={analytics.monthly_income} unit="$" />
        <KPICard title="Occupancy" value={analytics.occupancy_rate * 100} unit="%" />
      </KPICardGrid>
    </div>
  );
}
```

### 4. With Error Handling

```jsx
function SafeDashboard() {
  const { analytics, isLoading, error, refetch } = useAnalytics();

  if (isLoading) {
    return <div>Loading analytics...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 p-4 rounded">
        <p className="text-red-700">{error}</p>
        <button
          onClick={refetch}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Display analytics */}
    </div>
  );
}
```

### 5. With Manual Refetch

```jsx
function InteractiveDashboard() {
  const { analytics, isFetching, refetch } = useAnalytics();
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const handleRefresh = async () => {
    await refetch();
    setLastRefresh(new Date());
  };

  return (
    <div>
      <div className="flex justify-between items-center">
        <h1>Analytics Dashboard</h1>
        <div>
          <p className="text-sm text-gray-600">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            {isFetching ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>
      
      {/* Display analytics */}
    </div>
  );
}
```

### 6. Custom Refresh Interval

```jsx
function FastRefreshDashboard() {
  // Refresh every 1 minute, cache for 30 seconds
  const { analytics, isFetching } = useAnalytics({
    refetchInterval: 60000,    // 1 minute
    staleTime: 30000,          // 30 seconds
  });

  return (
    <div>
      {isFetching && <span>Updating...</span>}
      {/* Display analytics */}
    </div>
  );
}
```

### 7. Disable Auto-Refetch

```jsx
function ManualOnlyDashboard() {
  const { analytics, refetch } = useAnalytics({
    enableAutoRefetch: false,
  });

  return (
    <div>
      <button onClick={refetch}>Refresh Data</button>
      {/* Display analytics */}
    </div>
  );
}
```

---

## 🛡️ Error Boundary Hook

### useAnalyticsWithErrorBoundary()

Wrapped version with error boundary protection.

```jsx
import { useAnalyticsWithErrorBoundary } from '@/hooks/useAnalytics';

function SafeDashboard() {
  const { analytics, error, usingMockData } = useAnalyticsWithErrorBoundary();

  return (
    <div>
      {error && <div className="alert">{error}</div>}
      {usingMockData && <div className="info">Using cached data</div>}
      
      <KPICard title="Properties" value={analytics.total_properties} />
    </div>
  );
}
```

**Benefits:**
- Never crashes the app
- Always returns valid data
- Catches unexpected errors
- Provides user-friendly fallback

---

## ⚡ Real-Time Hook

### useRealTimeAnalytics()

Higher frequency updates for real-time dashboards.

```jsx
import { useRealTimeAnalytics } from '@/hooks/useAnalytics';

function RealTimeDashboard() {
  const { analytics, isFetching } = useRealTimeAnalytics();

  return (
    <div>
      <div className="flex items-center gap-2">
        <h1>Real-Time Analytics</h1>
        {isFetching && <span className="animate-pulse">●</span>}
      </div>
      
      <p className="text-sm">Updates every 30 seconds</p>
      
      <KPICard title="Properties" value={analytics.total_properties} />
    </div>
  );
}
```

**Configuration:**
- Refetch interval: 30 seconds
- Cache time: 15 seconds
- Same API as `useAnalytics`

---

## 📊 Category-Specific Hook

### useKPIs(category)

Fetch KPIs for specific categories.

```jsx
import { useKPIs } from '@/hooks/useAnalytics';

function FinancialKPIs() {
  const { kpis, isLoading } = useKPIs('financial');

  return (
    <KPICardGrid columns={3}>
      <KPICard
        title="Portfolio Value"
        value={kpis.total_portfolio_value?.value || 0}
        unit="$"
        trend={kpis.total_portfolio_value?.trend}
        color="blue"
      />
      
      <KPICard
        title="Monthly NOI"
        value={kpis.monthly_noi?.value || 0}
        unit="$"
        trend={kpis.monthly_noi?.trend}
        color="green"
      />
      
      <KPICard
        title="Cap Rate"
        value={kpis.average_cap_rate?.value || 0}
        unit="%"
        trend={kpis.average_cap_rate?.trend}
        color="purple"
      />
    </KPICardGrid>
  );
}
```

**Available Categories:**
- `financial` - Financial metrics
- `operational` - Operational metrics
- `portfolio` - Portfolio distribution

---

## 🔧 Configuration Options

### Default Configuration

```javascript
{
  useMockData: false,           // Use real API
  enableAutoRefetch: true,      // Auto-refresh enabled
  refetchInterval: 300000,      // 5 minutes
  staleTime: 180000,           // 3 minutes cache
}
```

### Custom Configuration

```jsx
const { analytics } = useAnalytics({
  useMockData: false,
  enableAutoRefetch: true,
  refetchInterval: 120000,      // 2 minutes
  staleTime: 60000,            // 1 minute cache
});
```

---

## 🎯 Best Practices

### 1. Handle Loading States

```jsx
✅ Good:
if (isLoading) return <LoadingSkeleton />;

❌ Bad:
// No loading state, shows empty/broken UI
```

### 2. Display Error Messages

```jsx
✅ Good:
if (error) {
  return (
    <div>
      <p>{error}</p>
      <button onClick={refetch}>Retry</button>
    </div>
  );
}

❌ Bad:
// Silent failure, user doesn't know what happened
```

### 3. Use Mock Data for Development

```jsx
✅ Good:
const isDev = import.meta.env.DEV;
const { analytics } = useAnalytics({
  useMockData: isDev && !backendAvailable,
});
```

### 4. Show Refetch Indicator

```jsx
✅ Good:
{isFetching && <span>Updating...</span>}

❌ Bad:
// User doesn't know data is being refreshed
```

### 5. Normalize Data Before Display

```jsx
✅ Good:
value={analytics.occupancy_rate * 100}  // Convert 0.946 → 94.6

❌ Bad:
value={analytics.occupancy_rate}        // Shows 0.946 instead of 94.6
```

---

## 🔄 Caching Behavior

### How Caching Works

1. **First Request:**
   - Hook fetches from API
   - Data stored in localStorage
   - `isLoading = true`

2. **Subsequent Requests (within staleTime):**
   - Returns cached data immediately
   - `isLoading = false`
   - No API call

3. **Stale Data (after staleTime):**
   - Returns cached data immediately
   - Fetches fresh data in background
   - `isFetching = true`
   - Updates when fresh data arrives

4. **Auto-Refetch:**
   - Every `refetchInterval` (default: 5 min)
   - Fetches in background
   - Updates data seamlessly

### Cache Keys

- Main analytics: `'analytics-kpi'`
- Financial KPIs: `'kpis-financial'`
- Operational KPIs: `'kpis-operational'`
- Portfolio KPIs: `'kpis-portfolio'`

---

## 🐛 Troubleshooting

### Data Not Updating

**Issue:** Analytics data doesn't refresh

**Solutions:**
1. Check `enableAutoRefetch` is true
2. Verify `refetchInterval` is set
3. Call `refetch()` manually
4. Check browser cache/localStorage

### API Errors

**Issue:** Getting errors from API

**Solutions:**
1. Check backend is running on correct port
2. Verify CORS is configured
3. Check API endpoint exists
4. Enable `useMockData` for development

### Mock Data Always Shows

**Issue:** Always seeing mock data

**Solutions:**
1. Set `useMockData: false`
2. Check API is reachable
3. Check network tab for failed requests
4. Verify API response format

### Numbers Look Wrong

**Issue:** Numbers display incorrectly

**Solutions:**
1. Convert `occupancy_rate`: multiply by 100
2. Check unit prop on KPICard
3. Verify API returns numbers, not strings
4. Check number formatting in KPICard

---

## 📚 Integration with Other Hooks

### With useMutation

```jsx
import useAnalytics from '@/hooks/useAnalytics';
import { useMutation } from '@/hooks/useMutation';

function PropertyManager() {
  const { analytics, refetch } = useAnalytics();
  
  const { mutate: addProperty } = useMutation(
    async (data) => api.post('/api/properties', data),
    {
      onSuccess: () => {
        refetch(); // Refresh analytics after adding property
      },
    }
  );

  return (
    <div>
      <KPICard title="Properties" value={analytics.total_properties} />
      <button onClick={() => addProperty(newPropertyData)}>
        Add Property
      </button>
    </div>
  );
}
```

### With useQuery

```jsx
import useAnalytics from '@/hooks/useAnalytics';
import { useQuery } from '@/hooks/useQuery';

function Dashboard() {
  const { analytics } = useAnalytics();
  
  const { data: properties } = useQuery(
    'properties',
    () => api.get('/api/properties')
  );

  return (
    <div>
      <KPICard title="Total" value={analytics.total_properties} />
      <PropertyList properties={properties} />
    </div>
  );
}
```

---

## 🎉 Summary

The `useAnalytics` hook provides a complete solution for fetching and managing analytics data:

✅ **Easy to Use** - Simple API, works out of the box  
✅ **Robust** - Error handling, fallbacks, caching  
✅ **Flexible** - Configurable refresh intervals  
✅ **Reliable** - Auto-refetch, mock data fallback  
✅ **Performant** - Smart caching, background updates  

**Perfect for dashboards and analytics views!** 🚀

