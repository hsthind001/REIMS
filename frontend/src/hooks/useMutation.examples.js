/**
 * useMutation Hook - Usage Examples
 * 
 * Demonstrates various use cases for the enhanced mutation hook
 */

import { useMutation, useOptimisticMutation, useQueryClient } from './useMutation';
import { useQuery } from './useQuery';
import api from '../api';

// ============================================================================
// Example 1: Basic Mutation (File Upload)
// ============================================================================

export function DocumentUploadBasic() {
  const { mutate: uploadFile, isLoading, isSuccess, error } = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/documents/upload', formData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        console.log('File uploaded:', data);
        alert('File uploaded successfully!');
      },
      onError: (error) => {
        console.error('Upload failed:', error);
        alert('Upload failed: ' + error.message);
      },
    }
  );

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadFile(file);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleFileChange}
        disabled={isLoading}
      />
      {isLoading && <p>Uploading...</p>}
      {isSuccess && <p className="success">✓ Upload complete!</p>}
      {error && <p className="error">✗ {error.message}</p>}
    </div>
  );
}

// ============================================================================
// Example 2: With Automatic Cache Invalidation
// ============================================================================

export function PropertyCreate() {
  const { mutate: createProperty, isLoading } = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      invalidateQueries: ['properties', 'properties-list'], // Auto-invalidate
      onSuccess: (data) => {
        alert(`Property "${data.name}" created successfully!`);
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    createProperty(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Property Name" required />
      <input name="address" placeholder="Address" required />
      <input name="type" placeholder="Type" required />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Property'}
      </button>
    </form>
  );
}

// ============================================================================
// Example 3: Optimistic Updates
// ============================================================================

export function TodoListOptimistic() {
  const queryClient = useQueryClient();

  // Fetch todos
  const { data: todos } = useQuery('todos', () => api.get('/api/todos'));

  // Create todo with optimistic update
  const { mutate: createTodo } = useMutation(
    async (newTodo) => {
      const response = await api.post('/api/todos', newTodo);
      return response.data;
    },
    {
      onMutate: async (newTodo) => {
        // Get current todos
        const previousTodos = queryClient.getQueryData('todos');

        // Optimistically update cache
        queryClient.setQueryData('todos', (old) => {
          return {
            ...old,
            todos: [
              ...old.todos,
              { ...newTodo, id: 'temp-' + Date.now(), status: 'pending' },
            ],
          };
        });

        // Return rollback function
        return () => {
          queryClient.setQueryData('todos', previousTodos);
        };
      },
      onError: (error, variables, rollback) => {
        // Rollback on error
        if (rollback) rollback();
        alert('Failed to create todo: ' + error.message);
      },
      onSuccess: () => {
        // Refetch to get server data
        queryClient.invalidateQueries('todos');
      },
    }
  );

  const handleAddTodo = () => {
    createTodo({
      title: 'New Todo',
      completed: false,
    });
  };

  return (
    <div>
      <button onClick={handleAddTodo}>Add Todo</button>
      <ul>
        {todos?.todos?.map((todo) => (
          <li key={todo.id}>
            {todo.title} {todo.status === 'pending' && '⏳'}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 4: Using useOptimisticMutation Helper
// ============================================================================

export function CommentSection({ postId }) {
  const { data: comments } = useQuery(`comments-${postId}`, () =>
    api.get(`/api/posts/${postId}/comments`)
  );

  const { mutate: addComment, isLoading } = useOptimisticMutation(
    async (comment) => {
      const response = await api.post(`/api/posts/${postId}/comments`, comment);
      return response.data;
    },
    `comments-${postId}`,
    (oldData, newComment) => {
      // Optimistic updater
      return {
        ...oldData,
        comments: [
          ...oldData.comments,
          {
            ...newComment,
            id: 'temp-' + Date.now(),
            createdAt: new Date().toISOString(),
          },
        ],
      };
    },
    {
      onError: (error) => {
        alert('Failed to add comment: ' + error.message);
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = e.target.comment.value;
    addComment({ text });
    e.target.reset();
  };

  return (
    <div>
      <h3>Comments</h3>
      <form onSubmit={handleSubmit}>
        <textarea name="comment" placeholder="Add a comment..." required />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Posting...' : 'Post Comment'}
        </button>
      </form>
      <ul>
        {comments?.comments?.map((comment) => (
          <li key={comment.id}>{comment.text}</li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 5: Retry with Exponential Backoff
// ============================================================================

export function CriticalDataUpdate() {
  const { mutate: updateData, isLoading, error } = useMutation(
    async (data) => {
      const response = await api.put('/api/critical-data', data);
      return response.data;
    },
    {
      retry: 3, // Retry 3 times
      retryDelay: 1000, // Start with 1s, then 2s, then 4s (exponential)
      onError: (error) => {
        console.error('All retries failed:', error);
        alert('Update failed after 3 attempts');
      },
    }
  );

  return (
    <div>
      <button onClick={() => updateData({ value: 123 })} disabled={isLoading}>
        {isLoading ? 'Updating (with retry)...' : 'Update Data'}
      </button>
      {error && <p className="error">Failed: {error.message}</p>}
    </div>
  );
}

// ============================================================================
// Example 6: Multiple Mutations with Refresh
// ============================================================================

export function PropertyManagement() {
  const queryClient = useQueryClient();

  // List properties
  const { data: properties, refetch } = useQuery('properties', () =>
    api.get('/api/properties')
  );

  // Create mutation
  const createMutation = useMutation(
    async (data) => api.post('/api/properties', data),
    {
      invalidateQueries: ['properties'],
      onSuccess: () => alert('Property created!'),
    }
  );

  // Update mutation
  const updateMutation = useMutation(
    async ({ id, data }) => api.put(`/api/properties/${id}`, data),
    {
      invalidateQueries: ['properties'],
      onSuccess: () => alert('Property updated!'),
    }
  );

  // Delete mutation
  const deleteMutation = useMutation(
    async (id) => api.delete(`/api/properties/${id}`),
    {
      invalidateQueries: ['properties'],
      onSuccess: () => alert('Property deleted!'),
    }
  );

  const handleCreate = () => {
    createMutation.mutate({
      name: 'New Property',
      address: '123 Main St',
    });
  };

  const handleUpdate = (id) => {
    updateMutation.mutate({
      id,
      data: { name: 'Updated Property' },
    });
  };

  const handleDelete = (id) => {
    if (confirm('Delete this property?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div>
      <button onClick={handleCreate}>Create Property</button>
      <button onClick={refetch}>Refresh List</button>

      <ul>
        {properties?.properties?.map((property) => (
          <li key={property.id}>
            {property.name}
            <button onClick={() => handleUpdate(property.id)}>Update</button>
            <button onClick={() => handleDelete(property.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 7: Error Recovery
// ============================================================================

export function ErrorRecoveryExample() {
  const { mutate, isLoading, isError, error, reset } = useMutation(
    async (data) => {
      const response = await api.post('/api/risky-operation', data);
      return response.data;
    },
    {
      retry: 2,
      onError: (error) => {
        console.error('Operation failed:', error);
      },
    }
  );

  const handleRetry = () => {
    reset(); // Clear error state
    mutate({ data: 'retry' });
  };

  return (
    <div>
      <button onClick={() => mutate({ data: 'test' })} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Start Operation'}
      </button>

      {isError && (
        <div className="error-recovery">
          <p className="error">Error: {error.message}</p>
          <button onClick={handleRetry}>Try Again</button>
          <button onClick={reset}>Dismiss</button>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 8: Async Mutation (with Promise)
// ============================================================================

export function AsyncMutationExample() {
  const { mutateAsync, isLoading } = useMutation(async (data) => {
    const response = await api.post('/api/process', data);
    return response.data;
  });

  const handleProcess = async () => {
    try {
      const result = await mutateAsync({ value: 123 });
      console.log('Result:', result);

      // Continue with next operation
      const nextResult = await mutateAsync({ value: 456 });
      console.log('Next result:', nextResult);

      alert('All operations completed!');
    } catch (error) {
      console.error('Operation failed:', error);
      alert('Operation failed: ' + error.message);
    }
  };

  return (
    <button onClick={handleProcess} disabled={isLoading}>
      {isLoading ? 'Processing...' : 'Start Async Operations'}
    </button>
  );
}

// ============================================================================
// Example 9: Batch Upload with Progress
// ============================================================================

export function BatchFileUpload() {
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = React.useState({});

  const { mutate: uploadFile } = useMutation(
    async ({ file, fileId }) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/documents/upload', formData);
      return { fileId, data: response.data };
    },
    {
      onSuccess: ({ fileId }) => {
        setUploadProgress((prev) => ({
          ...prev,
          [fileId]: 'success',
        }));
      },
      onError: (error, { fileId }) => {
        setUploadProgress((prev) => ({
          ...prev,
          [fileId]: 'error',
        }));
      },
      invalidateQueries: ['documents'],
    }
  );

  const handleMultipleFiles = (e) => {
    const files = Array.from(e.target.files);
    files.forEach((file, index) => {
      const fileId = `file-${index}`;
      setUploadProgress((prev) => ({ ...prev, [fileId]: 'uploading' }));
      uploadFile({ file, fileId });
    });
  };

  return (
    <div>
      <input type="file" multiple onChange={handleMultipleFiles} />
      <div>
        {Object.entries(uploadProgress).map(([fileId, status]) => (
          <div key={fileId}>
            {fileId}: {status}
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 10: Complex Form with Multiple Mutations
// ============================================================================

export function PropertyCreateForm() {
  const queryClient = useQueryClient();

  const { mutate: createProperty, isLoading } = useMutation(
    async (propertyData) => {
      // Step 1: Create property
      const propertyResponse = await api.post('/api/properties', propertyData);
      const propertyId = propertyResponse.data.id;

      // Step 2: Upload documents
      if (propertyData.documents?.length > 0) {
        await Promise.all(
          propertyData.documents.map((file) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('property_id', propertyId);
            return api.post('/api/documents/upload', formData);
          })
        );
      }

      return propertyResponse.data;
    },
    {
      invalidateQueries: ['properties', 'documents'],
      onSuccess: (data) => {
        alert(`Property "${data.name}" created with documents!`);
      },
      onError: (error) => {
        alert('Failed to create property: ' + error.message);
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const documents = Array.from(formData.getAll('documents'));

    createProperty({
      name: formData.get('name'),
      address: formData.get('address'),
      type: formData.get('type'),
      documents,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Property Name" required />
      <input name="address" placeholder="Address" required />
      <select name="type" required>
        <option value="residential">Residential</option>
        <option value="commercial">Commercial</option>
        <option value="industrial">Industrial</option>
      </select>
      <input type="file" name="documents" multiple />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Property'}
      </button>
    </form>
  );
}

// ============================================================================
// Example 11: Optimistic Delete with Undo
// ============================================================================

export function OptimisticDeleteExample() {
  const queryClient = useQueryClient();
  const [deletedItem, setDeletedItem] = React.useState(null);

  const { mutate: deleteItem } = useMutation(
    async (id) => {
      await api.delete(`/api/items/${id}`);
      return id;
    },
    {
      onMutate: async (id) => {
        const previousItems = queryClient.getQueryData('items');

        // Optimistically remove item
        queryClient.setQueryData('items', (old) => ({
          ...old,
          items: old.items.filter((item) => item.id !== id),
        }));

        // Store deleted item for undo
        const item = previousItems.items.find((item) => item.id === id);
        setDeletedItem(item);

        // Return rollback
        return () => {
          queryClient.setQueryData('items', previousItems);
          setDeletedItem(null);
        };
      },
      onError: (error, variables, rollback) => {
        if (rollback) rollback();
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

  return (
    <div>
      {deletedItem && (
        <div className="undo-banner">
          <p>Item deleted</p>
          <button onClick={handleUndo}>Undo</button>
        </div>
      )}
      {/* List items */}
    </div>
  );
}

// ============================================================================
// Example 12: Status-based UI Updates
// ============================================================================

export function StatusBasedMutation() {
  const { mutate, status, data, error } = useMutation(
    async (data) => {
      const response = await api.post('/api/process', data);
      return response.data;
    }
  );

  return (
    <div>
      <button onClick={() => mutate({ value: 123 })} disabled={status === 'loading'}>
        Submit
      </button>

      {status === 'idle' && <p>Ready to submit</p>}
      {status === 'loading' && <p>Processing...</p>}
      {status === 'error' && <p className="error">Error: {error.message}</p>}
      {status === 'success' && <p className="success">Success! Result: {data.id}</p>}
    </div>
  );
}

