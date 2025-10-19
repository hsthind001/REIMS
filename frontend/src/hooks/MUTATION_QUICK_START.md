# useMutation - Quick Start

Get started with mutations in under 5 minutes!

---

## 🚀 Basic Usage

```javascript
import { useMutation } from '@/hooks/useMutation';
import api from '@/api';

function CreateItem() {
  const { mutate, isLoading, isSuccess } = useMutation(
    async (data) => {
      const response = await api.post('/api/items', data);
      return response.data;
    }
  );

  const handleCreate = () => {
    mutate({ name: 'New Item', value: 123 });
  };

  return (
    <button onClick={handleCreate} disabled={isLoading}>
      {isLoading ? 'Creating...' : 'Create Item'}
    </button>
  );
}
```

---

## 💾 With Auto Cache Invalidation

```javascript
const { mutate } = useMutation(
  async (data) => api.post('/api/items', data),
  {
    invalidateQueries: ['items'], // Auto-refresh items list
    onSuccess: () => alert('Created!'),
  }
);
```

---

## ⚡ Optimistic Updates

```javascript
import { useOptimisticMutation } from '@/hooks/useMutation';

const { mutate } = useOptimisticMutation(
  async (item) => api.post('/api/items', item),
  'items',                              // Query key to update
  (oldData, newItem) => {              // How to update
    return {
      ...oldData,
      items: [...oldData.items, newItem],
    };
  }
);
```

---

## 🔄 With Retry

```javascript
const { mutate } = useMutation(
  async (data) => api.post('/api/critical', data),
  {
    retry: 3,           // Retry 3 times
    retryDelay: 1000,   // Start with 1s delay
  }
);
```

---

## 📋 Return Values

```javascript
const {
  mutate,      // Function to trigger mutation
  isLoading,   // Is mutation in progress?
  isSuccess,   // Did mutation succeed?
  isError,     // Did mutation fail?
  error,       // Error object
  data,        // Response data
  reset,       // Reset state
} = useMutation(mutationFn);
```

---

## 🎯 Common Patterns

### File Upload

```javascript
const { mutate: uploadFile, isLoading } = useMutation(
  async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return await api.post('/api/upload', formData);
  },
  {
    onSuccess: () => alert('Uploaded!'),
  }
);

// Use it
<input type="file" onChange={(e) => uploadFile(e.target.files[0])} />
```

### Form Submit

```javascript
const { mutate: submit, isLoading } = useMutation(
  async (formData) => api.post('/api/submit', formData),
  {
    invalidateQueries: ['data'],
    onSuccess: () => alert('Submitted!'),
  }
);

const handleSubmit = (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  submit(Object.fromEntries(data));
};
```

### Delete with Confirmation

```javascript
const { mutate: deleteItem } = useMutation(
  async (id) => api.delete(`/api/items/${id}`),
  {
    invalidateQueries: ['items'],
    onSuccess: () => alert('Deleted!'),
  }
);

const handleDelete = (id) => {
  if (confirm('Delete this item?')) {
    deleteItem(id);
  }
};
```

---

## 📖 Next Steps

- [Full Guide](./MUTATION_GUIDE.md) - Complete documentation
- [Examples](./useMutation.examples.js) - 12 real-world examples
- [useQuery Hook](./README.md) - Data fetching

---

**Ready to use! 🎉**

