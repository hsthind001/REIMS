# Custom React Hooks

This directory contains custom React hooks for the REIMS frontend application.

---

## 📚 Available Hooks

### 1. `useQuery` - Data Fetching Hook

A powerful custom hook for fetching and managing server state with caching, automatic refetching, and retry logic.

#### Features

✅ **Loading/Error/Success States** - Comprehensive state management  
✅ **Automatic Refetching** - Configurable intervals  
✅ **Manual Refetch** - Trigger refetch on demand  
✅ **Caching** - localStorage-based caching (5 minute default)  
✅ **Retry Logic** - Automatic retry on failure (1 retry default)  
✅ **Window Focus Refetch** - Refetch when tab gains focus  
✅ **Conditional Queries** - Enable/disable queries dynamically  
✅ **Background Refetch** - Update data without loading state  
✅ **Cache Management** - Clear cache manually or automatically  

---

## 🚀 Quick Start

### Basic Usage

```javascript
import { useQuery } from '@/hooks/useQuery';
import api from '@/api';

function PropertyList() {
  const { data, isLoading, error, refetch } = useQuery(
    'properties',
    async () => {
      const response = await api.get('/api/properties');
      return response.data;
    }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <button onClick={refetch}>Refresh</button>
      <ul>
        {data?.properties?.map(property => (
          <li key={property.id}>{property.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 📖 API Reference

### `useQuery(queryKey, queryFn, options)`

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `queryKey` | `string` | ✅ Yes | Unique identifier for the query |
| `queryFn` | `async function` | ✅ Yes | Function that returns a Promise with data |
| `options` | `object` | ❌ No | Configuration options |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `refetchInterval` | `number \| null` | `null` | Auto-refetch interval in milliseconds |
| `staleTime` | `number` | `300000` | Cache duration (5 minutes) |
| `enabled` | `boolean` | `true` | Enable/disable the query |
| `refetchOnWindowFocus` | `boolean` | `true` | Refetch when window gains focus |
| `retry` | `number` | `1` | Number of retries on failure |
| `cacheEnabled` | `boolean` | `true` | Enable/disable caching |

#### Return Value

```typescript
{
  data: T | null,              // Query data
  isLoading: boolean,          // Initial loading state
  isFetching: boolean,         // Fetching state (including background)
  error: Error | null,         // Error object if query failed
  isError: boolean,            // True if query failed
  isSuccess: boolean,          // True if query succeeded
  refetch: () => Promise<T>    // Manual refetch function
}
```

---

## 🎯 Common Use Cases

### 1. Auto-Refetch at Intervals

```javascript
const { data, isFetching } = useQuery(
  'kpis',
  async () => api.get('/api/kpis/financial'),
  {
    refetchInterval: 30000, // Refetch every 30 seconds
  }
);
```

### 2. Conditional Query

```javascript
function PropertyDetails({ propertyId }) {
  const { data, isLoading } = useQuery(
    `property-${propertyId}`,
    async () => api.get(`/api/properties/${propertyId}`),
    {
      enabled: !!propertyId, // Only fetch if propertyId exists
    }
  );
}
```

### 3. Disable Window Focus Refetch

```javascript
const { data } = useQuery(
  'static-data',
  async () => api.get('/api/static-data'),
  {
    refetchOnWindowFocus: false,
  }
);
```

### 4. Custom Cache Duration

```javascript
const { data } = useQuery(
  'long-lived-data',
  async () => api.get('/api/config'),
  {
    staleTime: 60 * 60 * 1000, // Cache for 1 hour
  }
);
```

### 5. No Caching (Always Fresh)

```javascript
const { data } = useQuery(
  'real-time-status',
  async () => api.get('/ai/process/status'),
  {
    cacheEnabled: false,
    staleTime: 0,
  }
);
```

### 6. Custom Retry Logic

```javascript
const { data, isError } = useQuery(
  'critical-data',
  async () => api.get('/api/critical'),
  {
    retry: 3, // Retry 3 times on failure
  }
);
```

### 7. Multiple Queries

```javascript
function Dashboard() {
  const properties = useQuery('properties', () => api.get('/api/properties'));
  const kpis = useQuery('kpis', () => api.get('/api/kpis'));
  const alerts = useQuery('alerts', () => api.get('/api/alerts'));

  const isLoading = properties.isLoading || kpis.isLoading || alerts.isLoading;

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {/* Render dashboard */}
    </div>
  );
}
```

### 8. Dependent Queries

```javascript
function PropertyFinancials({ propertyId }) {
  // First query
  const property = useQuery(
    `property-${propertyId}`,
    () => api.get(`/api/properties/${propertyId}`),
    { enabled: !!propertyId }
  );

  // Second query (depends on first)
  const financials = useQuery(
    `financials-${propertyId}`,
    () => api.get(`/api/properties/${propertyId}/financials`),
    { enabled: property.isSuccess } // Only run if first query succeeded
  );

  return <div>{/* Render */}</div>;
}
```

---

## 🔄 useMutation Hook

For POST, PUT, DELETE operations.

### Usage

```javascript
import { useMutation } from '@/hooks/useQuery';

function CreateProperty() {
  const { mutate, isLoading, isSuccess, error } = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        console.log('Property created:', data);
      },
      onError: (error) => {
        console.error('Failed:', error);
      },
    }
  );

  const handleSubmit = (data) => {
    mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create'}
      </button>
      {isSuccess && <p>Created successfully!</p>}
      {error && <p>Error: {error.message}</p>}
    </form>
  );
}
```

### Mutation with Query Invalidation

```javascript
function DocumentUpload() {
  const documentsQuery = useQuery('documents', () => api.get('/api/documents'));

  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return await api.post('/api/documents/upload', formData);
    },
    {
      onSuccess: () => {
        documentsQuery.refetch(); // Refresh documents list
      },
    }
  );

  return (
    <div>
      <input
        type="file"
        onChange={(e) => uploadMutation.mutate(e.target.files[0])}
      />
    </div>
  );
}
```

---

## 💾 Cache Management

### Clear Specific Query Cache

```javascript
import { clearQueryCache } from '@/hooks/useQuery';

// Clear cache for a specific query
clearQueryCache('properties');
```

### Clear All Query Cache

```javascript
import { clearAllQueryCache } from '@/hooks/useQuery';

// Clear all cached queries
clearAllQueryCache();
```

### Manual Cache Control

```javascript
function DataManager() {
  const { data, refetch } = useQuery('data', fetchData);

  const handleClearAndRefresh = () => {
    clearQueryCache('data');
    refetch();
  };

  return <button onClick={handleClearAndRefresh}>Clear & Refresh</button>;
}
```

---

## ⚡ Performance Tips

### 1. Use Appropriate Cache Times

```javascript
// Short-lived data (real-time)
{ staleTime: 5000 } // 5 seconds

// Medium-lived data (dashboards)
{ staleTime: 5 * 60 * 1000 } // 5 minutes (default)

// Long-lived data (config, static)
{ staleTime: 60 * 60 * 1000 } // 1 hour
```

### 2. Disable Unnecessary Refetches

```javascript
// For static/rarely changing data
{
  refetchOnWindowFocus: false,
  refetchInterval: null,
  staleTime: 60 * 60 * 1000, // 1 hour
}
```

### 3. Conditional Queries

```javascript
// Only fetch when needed
{
  enabled: isModalOpen && hasPermission,
}
```

### 4. Background Refetch

The hook automatically uses background refetch for:
- Window focus refetch
- Interval refetch
- When cache is valid but stale

This keeps the UI responsive while updating data.

---

## 🐛 Debugging

### Enable Logging

```javascript
// Add this to your query for debugging
const { data, isLoading, error } = useQuery(
  'debug-query',
  async () => {
    console.log('Fetching data...');
    const result = await api.get('/api/data');
    console.log('Data received:', result);
    return result;
  }
);

// Check cache in browser console
console.log(localStorage.getItem('query_cache_debug-query'));
```

### Common Issues

**Query not fetching:**
- Check if `enabled: false` is set
- Verify `queryFn` is async and returns data
- Check network tab for errors

**Cache not working:**
- Check if `cacheEnabled: false` is set
- Verify localStorage is available
- Check if cache time expired

**Too many refetches:**
- Increase `staleTime`
- Disable `refetchOnWindowFocus`
- Remove or increase `refetchInterval`

---

## 🔗 Integration with API Client

This hook works seamlessly with the custom API client:

```javascript
import api from '@/api';
import { useQuery } from '@/hooks/useQuery';

function MyComponent() {
  const { data, isLoading, error } = useQuery(
    'my-data',
    async () => {
      // API client automatically handles:
      // - JWT tokens
      // - Error handling
      // - Timeout
      // - Request/response interceptors
      const response = await api.get('/api/endpoint');
      return response.data; // or just response if using default client
    }
  );
}
```

---

## 📝 Best Practices

1. **Use descriptive query keys:**
   ```javascript
   ✅ useQuery('properties-list', ...)
   ✅ useQuery(`property-${id}-details`, ...)
   ❌ useQuery('data', ...)
   ```

2. **Handle loading and error states:**
   ```javascript
   if (isLoading) return <LoadingSpinner />;
   if (error) return <ErrorMessage error={error} />;
   ```

3. **Use appropriate cache times:**
   - Real-time data: 5-30 seconds
   - Dashboard data: 1-5 minutes
   - Static data: 30-60 minutes

4. **Disable queries when not needed:**
   ```javascript
   { enabled: isModalOpen }
   ```

5. **Clear cache when data changes:**
   ```javascript
   onSuccess: () => {
     clearQueryCache('related-data');
   }
   ```

---

## 🆚 Comparison with TanStack Query (React Query)

| Feature | useQuery (Custom) | TanStack Query |
|---------|------------------|----------------|
| Caching | ✅ localStorage | ✅ Memory |
| Auto-refetch | ✅ Yes | ✅ Yes |
| Window focus refetch | ✅ Yes | ✅ Yes |
| Retry logic | ✅ Yes | ✅ Yes |
| Query invalidation | ⚠️ Manual | ✅ Automatic |
| Devtools | ❌ No | ✅ Yes |
| SSR Support | ❌ No | ✅ Yes |
| Bundle size | ✅ ~3KB | ⚠️ ~40KB |
| Dependencies | ✅ None | ⚠️ External |

**When to use custom hook:**
- Small to medium projects
- No external dependencies
- Simple caching needs
- localStorage persistence preferred

**When to use TanStack Query:**
- Large/complex applications
- Need advanced features (infinite queries, SSR, etc.)
- Need official devtools
- Need ecosystem plugins

---

## 📚 Additional Resources

- [useQuery Examples](./useQuery.examples.js) - Comprehensive examples
- [API Client Documentation](../api/README.md) - API client integration
- [Component Examples](../components/) - Real-world usage

---

## 🤝 Contributing

When adding new hooks:
1. Follow the same pattern as `useQuery`
2. Add comprehensive JSDoc comments
3. Create example file (`.examples.js`)
4. Update this README
5. Add TypeScript types if using TS

---

**Last Updated:** 2025-10-12  
**Version:** 1.0.0

