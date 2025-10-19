# REIMS API Client

Centralized API client for the REIMS frontend with comprehensive features for handling HTTP requests, authentication, error handling, and loading states.

## Features

- ✅ **Base URL Configuration** - Environment-based URL with fallback
- ✅ **Request/Response Interceptors** - Modify requests and responses globally
- ✅ **Error Handling** - Centralized error handling with user-friendly messages
- ✅ **Loading State Management** - Track active requests automatically
- ✅ **JWT Token Management** - Automatic token injection and expiry checking
- ✅ **Timeout Handling** - 30-second default timeout with abort support
- ✅ **Fetch API** - No external dependencies (axios-free)
- ✅ **TypeScript Ready** - Fully documented with JSDoc

## Installation

The API client is already included in the project. Just import it:

```javascript
import api from '@/api/client';
```

## Configuration

Set the API base URL in your `.env` file:

```env
VITE_API_URL=http://localhost:8001
```

If not set, defaults to `http://localhost:8001`.

## Basic Usage

### GET Request

```javascript
import api from '@/api/client';

// Simple GET
const response = await api.get('/properties');
console.log(response.data); // Array of properties

// GET with error handling
try {
  const response = await api.get('/properties/123');
  console.log(response.data);
} catch (error) {
  const message = api.getErrorMessage(error);
  console.error(message);
}
```

### POST Request

```javascript
// Create new property
const newProperty = {
  name: 'Downtown Office Commons',
  address: '123 Main St',
  city: 'Los Angeles',
  state: 'CA',
};

const response = await api.post('/properties', newProperty);
console.log(response.data); // Created property with ID
```

### PUT Request

```javascript
// Update property
const updates = {
  occupancy_rate: 95.5,
  annual_noi: 850000,
};

const response = await api.put('/properties/123', updates);
console.log(response.data); // Updated property
```

### DELETE Request

```javascript
// Delete property
await api.delete('/properties/123');
```

### File Upload

```javascript
// Upload file with FormData
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('property_id', '123');

const response = await api.post('/documents/upload', formData);
console.log(response.data); // Uploaded document info
```

## Authentication

### Set Token (after login)

```javascript
// Login
const credentials = { email: 'user@example.com', password: 'password' };
const response = await api.post('/auth/login', credentials);

// Store tokens
api.setToken(response.data.access_token, response.data.refresh_token);

// Now all subsequent requests will include the token automatically
```

### Check Authentication

```javascript
if (api.isAuthenticated()) {
  console.log('User is authenticated');
} else {
  console.log('User needs to log in');
}
```

### Logout

```javascript
// Clear tokens
api.clearAuth();

// Or logout via API
await api.post('/auth/logout');
api.clearAuth();
```

## Error Handling

### User-Friendly Error Messages

```javascript
try {
  const response = await api.get('/properties/999');
} catch (error) {
  const message = api.getErrorMessage(error);
  console.error(message); // "The requested resource was not found."
}
```

### Error Codes

```javascript
import { ERROR_CODES } from '@/api/client';

try {
  await api.post('/documents/upload', data);
} catch (error) {
  switch (error.error?.code) {
    case ERROR_CODES.NETWORK_ERROR:
      alert('Network error. Please check your connection.');
      break;
    case ERROR_CODES.UNAUTHORIZED:
      // Redirect to login
      router.push('/login');
      break;
    case ERROR_CODES.VALIDATION_ERROR:
      // Show validation errors
      showValidationErrors(error.error.details);
      break;
    default:
      alert(api.getErrorMessage(error));
  }
}
```

Available error codes:
- `NETWORK_ERROR` - Network connectivity issue
- `TIMEOUT_ERROR` - Request took too long
- `UNAUTHORIZED` - 401 - Need to log in
- `FORBIDDEN` - 403 - No permission
- `NOT_FOUND` - 404 - Resource not found
- `VALIDATION_ERROR` - 422 - Invalid input
- `CLIENT_ERROR` - 4xx - Client error
- `SERVER_ERROR` - 5xx - Server error
- `UNKNOWN_ERROR` - Unexpected error

## Loading State

### Subscribe to Loading Changes

```javascript
import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/api/client';

const isLoading = ref(false);

onMounted(() => {
  // Subscribe to loading state changes
  const unsubscribe = api.onLoadingChange((loading) => {
    isLoading.value = loading;
  });
  
  // Cleanup on unmount
  onUnmounted(unsubscribe);
});
```

### Check Current Loading State

```javascript
if (api.isLoading()) {
  console.log('Requests are in progress');
}
```

## Request/Response Interceptors

### Add Request Interceptor

```javascript
// Add custom header to all requests
api.addRequestInterceptor((config) => {
  config.headers['X-Custom-Header'] = 'value';
  return config;
});

// Modify request based on user role
api.addRequestInterceptor((config) => {
  const userRole = store.state.user.role;
  config.headers['X-User-Role'] = userRole;
  return config;
});
```

### Add Response Interceptor

```javascript
// Transform all responses
api.addResponseInterceptor((response) => {
  // Log analytics
  analytics.track('api_response', {
    success: response.success,
    timestamp: response.timestamp,
  });
  
  return response;
});

// Handle token refresh
api.addResponseInterceptor(async (response) => {
  if (response.error?.code === 'UNAUTHORIZED') {
    // Try to refresh token
    const refreshed = await refreshAuthToken();
    if (!refreshed) {
      router.push('/login');
    }
  }
  return response;
});
```

## Advanced Usage

### Custom Timeout

```javascript
// 60-second timeout for large file upload
const response = await api.post('/documents/upload', formData, {
  timeout: 60000, // 60 seconds
});
```

### Custom Headers

```javascript
// Add custom headers for specific request
const response = await api.get('/analytics', {
  headers: {
    'X-Report-Type': 'summary',
    'X-Date-Range': '30d',
  },
});
```

### Direct API Call

```javascript
import apiClient from '@/api/client';

// Use apiCall method directly
const response = await apiClient.apiCall('GET', '/properties', null, {
  headers: { 'X-Custom': 'value' },
  timeout: 10000,
});
```

## Response Format

All responses follow this standard format:

```javascript
{
  success: true,        // true if successful, false if error
  data: {...},          // Response data (if successful)
  error: {              // Error details (if failed)
    code: 'NOT_FOUND',
    message: 'Resource not found.',
    details: {...}
  },
  timestamp: '2025-10-12T10:30:00.000Z'  // ISO timestamp
}
```

## React/Vue Integration

### React Hook

```javascript
import { useState, useEffect } from 'react';
import api from '@/api/client';

function useProperties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const response = await api.get('/properties');
        setProperties(response.data);
      } catch (err) {
        setError(api.getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  return { properties, loading, error };
}
```

### Vue Composable

```javascript
import { ref } from 'vue';
import api from '@/api/client';

export function useProperties() {
  const properties = ref([]);
  const loading = ref(true);
  const error = ref(null);

  const fetchProperties = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/properties');
      properties.value = response.data;
    } catch (err) {
      error.value = api.getErrorMessage(err);
    } finally {
      loading.value = false;
    }
  };

  return { properties, loading, error, fetchProperties };
}
```

## Best Practices

1. **Always handle errors**
   ```javascript
   try {
     const response = await api.get('/data');
     // Handle success
   } catch (error) {
     const message = api.getErrorMessage(error);
     // Show error to user
   }
   ```

2. **Use loading states**
   ```javascript
   const isLoading = ref(false);
   
   const fetchData = async () => {
     isLoading.value = true;
     try {
       const response = await api.get('/data');
       // Process data
     } finally {
       isLoading.value = false;
     }
   };
   ```

3. **Set tokens after login**
   ```javascript
   const login = async (credentials) => {
     const response = await api.post('/auth/login', credentials);
     api.setToken(response.data.token, response.data.refreshToken);
   };
   ```

4. **Clear tokens on logout**
   ```javascript
   const logout = async () => {
     await api.post('/auth/logout');
     api.clearAuth();
     router.push('/login');
   };
   ```

5. **Use specific error codes**
   ```javascript
   catch (error) {
     if (error.error?.code === ERROR_CODES.UNAUTHORIZED) {
       // Handle unauthorized specifically
     } else {
       // Generic error handling
     }
   }
   ```

## Testing

### Mock API Client

```javascript
import { vi } from 'vitest';

// Mock successful response
vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({
      success: true,
      data: { id: 1, name: 'Test' },
    })),
  },
}));

// Mock error response
api.get.mockRejectedValue({
  success: false,
  error: {
    code: 'NOT_FOUND',
    message: 'Not found',
  },
});
```

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure the backend has proper CORS configuration:

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # PRIMARY frontend port
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Token Expiry

The client automatically checks token expiry. If a token is expired, it won't be included in requests. Handle this with a 401 response:

```javascript
catch (error) {
  if (error.error?.code === ERROR_CODES.UNAUTHORIZED) {
    api.clearAuth();
    router.push('/login');
  }
}
```

## Support

For issues or questions, refer to:
- Backend API documentation: `/docs` endpoint
- Frontend documentation: `frontend/README.md`
- Architecture docs: `ARCHITECTURE_STATUS.md`

