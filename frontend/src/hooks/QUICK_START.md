# useQuery Hook - Quick Start Guide

Get started with the custom `useQuery` hook in under 5 minutes!

---

## 🚀 Installation

The hook is already included in your project. No installation needed!

```javascript
import { useQuery } from '@/hooks/useQuery';
// or
import { useQuery } from '../hooks';
```

---

## 📝 Basic Example

```javascript
import React from 'react';
import { useQuery } from '@/hooks/useQuery';
import api from '@/api';

function MyComponent() {
  const { data, isLoading, error } = useQuery(
    'my-unique-key',           // Query key (unique identifier)
    async () => {              // Query function (returns Promise)
      const response = await api.get('/api/endpoint');
      return response.data;
    }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>My Data</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
```

---

## 🎯 Common Patterns

### 1. With Manual Refetch

```javascript
function Properties() {
  const { data, isLoading, refetch } = useQuery(
    'properties',
    () => api.get('/api/properties')
  );

  return (
    <div>
      <button onClick={refetch}>Refresh</button>
      {data?.properties?.map(p => <div key={p.id}>{p.name}</div>)}
    </div>
  );
}
```

### 2. With Auto-Refetch (Every 30 seconds)

```javascript
function LiveKPIs() {
  const { data, isFetching } = useQuery(
    'kpis',
    () => api.get('/api/kpis'),
    {
      refetchInterval: 30000, // 30 seconds
    }
  );

  return (
    <div>
      <h2>KPIs {isFetching && '🔄'}</h2>
      <p>Value: ${data?.total_value}</p>
    </div>
  );
}
```

### 3. Conditional Query (Only Fetch When Ready)

```javascript
function Details({ id }) {
  const { data, isLoading } = useQuery(
    `details-${id}`,
    () => api.get(`/api/items/${id}`),
    {
      enabled: !!id, // Only fetch if ID exists
    }
  );

  if (!id) return <div>Select an item</div>;
  if (isLoading) return <div>Loading...</div>;

  return <div>{data?.name}</div>;
}
```

---

## 🔄 Mutations (POST/PUT/DELETE)

```javascript
import { useMutation } from '@/hooks/useQuery';

function CreateForm() {
  const { mutate, isLoading, isSuccess } = useMutation(
    async (formData) => {
      return await api.post('/api/items', formData);
    },
    {
      onSuccess: () => alert('Created!'),
      onError: (err) => alert('Failed: ' + err.message),
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = { name: 'Test' };
    mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create'}
      </button>
      {isSuccess && <p>Success!</p>}
    </form>
  );
}
```

---

## ⚙️ Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `refetchInterval` | `null` | Auto-refetch interval (ms) |
| `staleTime` | `300000` (5 min) | Cache duration |
| `enabled` | `true` | Enable/disable query |
| `refetchOnWindowFocus` | `true` | Refetch on focus |
| `retry` | `1` | Retries on failure |
| `cacheEnabled` | `true` | Enable caching |

---

## 🎨 Return Values

```javascript
const {
  data,          // Query result
  isLoading,     // Initial loading
  isFetching,    // Any fetching (including background)
  error,         // Error object
  isError,       // True if error
  isSuccess,     // True if success
  refetch,       // Manual refetch function
} = useQuery(...);
```

---

## 💡 Tips

1. **Use unique query keys:**
   ```javascript
   ✅ 'properties-list'
   ✅ `property-${id}-details`
   ❌ 'data'
   ```

2. **Handle errors gracefully:**
   ```javascript
   if (error) {
     return <ErrorMessage error={error} onRetry={refetch} />;
   }
   ```

3. **Show loading indicators:**
   ```javascript
   {isFetching && <span className="spinner">🔄</span>}
   ```

4. **Clear cache when needed:**
   ```javascript
   import { clearQueryCache } from '@/hooks/useQuery';
   clearQueryCache('my-key');
   ```

---

## 📚 Next Steps

- [Full Documentation](./README.md)
- [Complete Examples](./useQuery.examples.js)
- [Demo Component](../components/QueryDemo.jsx)

---

**Ready to use! Happy coding! 🚀**

