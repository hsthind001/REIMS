# useMutation Hook - Complete Guide

**Advanced mutation hook for POST, PUT, DELETE operations with optimistic updates, automatic cache invalidation, and error recovery.**

---

## 🎯 Overview

The `useMutation` hook provides a powerful and flexible way to handle API mutations with:

✅ **Loading/Error/Success States** - Complete state management  
✅ **Optimistic Updates** - Update UI before server response  
✅ **Automatic Cache Invalidation** - Keep queries in sync  
✅ **Error Recovery** - Rollback and retry logic  
✅ **Retry with Exponential Backoff** - Configurable retry strategy  
✅ **Query Client Integration** - Manage cache easily  

---

## 🚀 Quick Start

### Basic Usage

```javascript
import { useMutation } from '@/hooks/useMutation';
import api from '@/api';

function CreateProperty() {
  const { mutate, isLoading, isSuccess, error } = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        alert(`Property "${data.name}" created!`);
      },
      onError: (error) => {
        alert('Error: ' + error.message);
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({ name: 'New Property', address: '123 Main St' });
  };

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create'}
      </button>
      {isSuccess && <p>✓ Created!</p>}
      {error && <p>✗ {error.message}</p>}
    </form>
  );
}
```

---

## 📖 API Reference

### useMutation(mutationFn, options)

#### Parameters

**mutationFn: `(variables) => Promise`**  
The function that performs the mutation.

**options: `Object`** (optional)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `onSuccess` | `(data, variables) => void` | - | Called on successful mutation |
| `onError` | `(error, variables, rollback) => void` | - | Called on failed mutation |
| `onSettled` | `(data, error, variables) => void` | - | Called when mutation completes |
| `onMutate` | `(variables) => rollback` | - | Called before mutation (optimistic updates) |
| `invalidateQueries` | `string[]` | `[]` | Query keys to invalidate on success |
| `retry` | `number` | `2` | Number of retries on failure |
| `retryDelay` | `number` | `1000` | Initial retry delay in ms |
| `throwOnError` | `boolean` | `false` | Whether to throw errors |

#### Return Value

```typescript
{
  mutate: (variables) => void,        // Execute mutation
  mutateAsync: (variables) => Promise, // Execute and return promise
  data: T | null,                      // Mutation result
  error: Error | null,                 // Error object
  isLoading: boolean,                  // Loading state
  isError: boolean,                    // Error state
  isSuccess: boolean,                  // Success state
  status: string,                      // 'idle' | 'loading' | 'error' | 'success'
  reset: () => void,                   // Reset state
}
```

---

## 🎨 Core Features

### 1. Automatic Cache Invalidation

Automatically clear and refetch related queries after successful mutation.

```javascript
const { mutate } = useMutation(
  async (data) => api.post('/api/properties', data),
  {
    invalidateQueries: ['properties', 'properties-list', 'dashboard'],
    onSuccess: () => {
      console.log('Cache invalidated automatically');
    },
  }
);
```

**How it works:**
- On success, clears cache for specified query keys
- Queries will refetch next time they're accessed
- Keeps UI in sync with server state

### 2. Optimistic Updates

Update UI immediately before server responds, then rollback on error.

```javascript
const queryClient = useQueryClient();

const { mutate } = useMutation(
  async (newItem) => api.post('/api/items', newItem),
  {
    onMutate: async (newItem) => {
      // Get current data
      const previousItems = queryClient.getQueryData('items');

      // Update cache optimistically
      queryClient.setQueryData('items', (old) => ({
        ...old,
        items: [...old.items, { ...newItem, id: 'temp-' + Date.now() }],
      }));

      // Return rollback function
      return () => {
        queryClient.setQueryData('items', previousItems);
      };
    },
    onError: (error, variables, rollback) => {
      // Rollback on error
      if (rollback) rollback();
    },
    onSuccess: () => {
      // Refetch to get server data
      queryClient.invalidateQueries('items');
    },
  }
);
```

### 3. Retry with Exponential Backoff

Automatically retry failed mutations with increasing delays.

```javascript
const { mutate } = useMutation(
  async (data) => api.post('/api/critical', data),
  {
    retry: 3,           // Retry 3 times
    retryDelay: 1000,   // 1s, then 2s, then 4s
    onError: (error) => {
      console.error('All retries failed:', error);
    },
  }
);

// Delays: 1000ms → 2000ms → 4000ms (exponential backoff)
```

### 4. Error Recovery

Handle errors gracefully with rollback and reset capabilities.

```javascript
const { mutate, isError, error, reset } = useMutation(
  async (data) => api.post('/api/risky', data)
);

// On error, user can:
// 1. Try again: mutate(data)
// 2. Clear error: reset()
```

---

## 🔧 Query Client

Manage query cache directly with the query client.

### useQueryClient Hook

```javascript
import { useQueryClient } from '@/hooks/useMutation';

function MyComponent() {
  const queryClient = useQueryClient();

  // Invalidate queries
  queryClient.invalidateQueries('items');
  queryClient.invalidateQueries(['items', 'dashboard']);

  // Get cached data
  const items = queryClient.getQueryData('items');

  // Set cached data
  queryClient.setQueryData('items', newData);
  queryClient.setQueryData('items', (old) => ({ ...old, updated: true }));

  // Clear all cache
  queryClient.clear();
}
```

---

## 🎯 Advanced Patterns

### 1. Optimistic Mutation Helper

Simplify optimistic updates with helper hook.

```javascript
import { useOptimisticMutation } from '@/hooks/useMutation';

const { mutate } = useOptimisticMutation(
  async (comment) => api.post('/api/comments', comment),
  'comments',                                    // Query key
  (oldData, newComment) => {                    // Optimistic updater
    return {
      ...oldData,
      comments: [...oldData.comments, { ...newComment, id: 'temp' }],
    };
  },
  {
    onError: (error) => alert('Failed: ' + error.message),
  }
);
```

### 2. Multiple Mutations

Manage multiple related mutations.

```javascript
function ItemManager() {
  const createMutation = useMutation(
    (data) => api.post('/api/items', data),
    { invalidateQueries: ['items'] }
  );

  const updateMutation = useMutation(
    ({ id, data }) => api.put(`/api/items/${id}`, data),
    { invalidateQueries: ['items'] }
  );

  const deleteMutation = useMutation(
    (id) => api.delete(`/api/items/${id}`),
    { invalidateQueries: ['items'] }
  );

  return {
    create: createMutation.mutate,
    update: updateMutation.mutate,
    delete: deleteMutation.mutate,
    isLoading: 
      createMutation.isLoading || 
      updateMutation.isLoading || 
      deleteMutation.isLoading,
  };
}
```

### 3. Async Mutation (Sequential Operations)

Use `mutateAsync` for sequential operations.

```javascript
const { mutateAsync } = useMutation(
  async (data) => api.post('/api/process', data)
);

const handleProcess = async () => {
  try {
    // Step 1
    const result1 = await mutateAsync({ step: 1 });
    console.log('Step 1 complete:', result1);

    // Step 2 (depends on step 1)
    const result2 = await mutateAsync({ step: 2, prev: result1.id });
    console.log('Step 2 complete:', result2);

    alert('All steps completed!');
  } catch (error) {
    alert('Process failed: ' + error.message);
  }
};
```

### 4. Batch Operations

Upload multiple files or perform batch operations.

```javascript
const { mutate: uploadFile } = useMutation(
  async ({ file, fileId }) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload', formData);
  }
);

const handleBatchUpload = (files) => {
  files.forEach((file, index) => {
    uploadFile({ file, fileId: `file-${index}` });
  });
};
```

### 5. Undo Functionality

Implement undo with optimistic delete.

```javascript
const [deletedItem, setDeletedItem] = useState(null);

const { mutate: deleteItem } = useMutation(
  async (id) => api.delete(`/api/items/${id}`),
  {
    onMutate: async (id) => {
      const previous = queryClient.getQueryData('items');
      const item = previous.items.find(i => i.id === id);
      
      // Optimistically remove
      queryClient.setQueryData('items', (old) => ({
        ...old,
        items: old.items.filter(i => i.id !== id),
      }));

      setDeletedItem(item);

      return () => queryClient.setQueryData('items', previous);
    },
  }
);

const handleUndo = () => {
  if (deletedItem) {
    queryClient.setQueryData('items', (old) => ({
      ...old,
      items: [...old.items, deletedItem],
    }));
    setDeletedItem(null);
  }
};
```

---

## 💡 Best Practices

### 1. Use Callbacks Wisely

```javascript
✅ Good: Use for side effects
{
  onSuccess: (data) => {
    showNotification('Success!');
    navigate(`/items/${data.id}`);
  }
}

❌ Bad: Complex logic in callbacks
{
  onSuccess: (data) => {
    // Too much logic here...
    // Should be in component or separate function
  }
}
```

### 2. Invalidate Related Queries

```javascript
✅ Good: Invalidate all related queries
{
  invalidateQueries: ['items', 'items-list', 'dashboard', 'stats']
}

⚠️ Careful: Don't invalidate unrelated queries
{
  invalidateQueries: ['everything'] // Too broad
}
```

### 3. Handle Errors Gracefully

```javascript
✅ Good: Provide user feedback and recovery
{
  onError: (error) => {
    showNotification('Failed to save. Please try again.');
    logError(error);
  },
  retry: 2,
}

❌ Bad: Silent failures
{
  onError: (error) => {
    // Nothing...
  }
}
```

### 4. Use Optimistic Updates Wisely

```javascript
✅ Good: Use for fast operations (like, upvote)
const { mutate: likePost } = useOptimisticMutation(...)

✅ Good: Use for create/delete
const { mutate: addComment } = useOptimisticMutation(...)

⚠️ Careful: Complex updates
// May need manual rollback logic

❌ Bad: File uploads (can fail)
// Don't show success until server confirms
```

---

## 🧪 Testing

### Manual Testing

```javascript
// Test success path
mutate({ name: 'Test' });
// Expected: Loading → Success

// Test error path  
mutate({ invalid: 'data' });
// Expected: Loading → Error → Rollback

// Test retry
mutate({ data: 'test' });
// Expected: Retry on failure (check console)
```

### Check Cache

```javascript
// In browser console
const queryClient = window.queryClient; // If exposed
console.log(queryClient.getQueryData('items'));

// Or check localStorage
console.log(localStorage.getItem('query_cache_items'));
```

---

## 📊 Comparison

### useMutation vs useQuery

| Aspect | useMutation | useQuery |
|--------|-------------|----------|
| **Purpose** | POST/PUT/DELETE | GET (fetch data) |
| **Trigger** | Manual (mutate) | Automatic |
| **Caching** | No | Yes |
| **Refetch** | No | Yes (auto/manual) |
| **Optimistic** | Yes | No |

### When to Use

**useMutation:**
- Creating items
- Updating items
- Deleting items
- Form submissions
- File uploads

**useQuery:**
- Fetching lists
- Fetching details
- Dashboard data
- Real-time data (with refetch)

---

## 🐛 Troubleshooting

### Mutation Not Working

**Check:**
- ✅ Is `mutationFn` async?
- ✅ Does it return data?
- ✅ Are network requests succeeding?

### Cache Not Invalidating

**Check:**
- ✅ Is query key correct?
- ✅ Is `invalidateQueries` array correct?
- ✅ Are queries using same keys?

### Optimistic Updates Not Rolling Back

**Check:**
- ✅ Is `onMutate` returning rollback function?
- ✅ Is rollback being called in `onError`?
- ✅ Is previous data captured correctly?

---

## 📚 Examples

See [useMutation.examples.js](./useMutation.examples.js) for 12 complete examples:

1. Basic mutation (file upload)
2. With automatic cache invalidation
3. Optimistic updates
4. Using useOptimisticMutation helper
5. Retry with exponential backoff
6. Multiple mutations with refresh
7. Error recovery
8. Async mutation (sequential)
9. Batch upload with progress
10. Complex form with multiple mutations
11. Optimistic delete with undo
12. Status-based UI updates

---

## 🔗 Related

- [useQuery Hook](./README.md) - Data fetching
- [API Client](../api/README.md) - HTTP requests
- [Examples](./useMutation.examples.js) - Real-world usage

---

**Status:** ✅ Production Ready  
**Last Updated:** 2025-10-12

