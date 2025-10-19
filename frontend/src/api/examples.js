/**
 * REIMS API Client - Usage Examples
 * 
 * This file contains practical examples of using the API client
 * in various scenarios.
 */

import api, { ERROR_CODES } from './client';

/**
 * Example 1: Simple GET request
 */
export async function example1_SimpleGet() {
  try {
    const response = await api.get('/properties');
    console.log('Properties:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 2: GET with query parameters
 */
export async function example2_GetWithParams() {
  const endpoint = '/properties?city=Los Angeles&status=active';
  
  try {
    const response = await api.get(endpoint);
    return response.data;
  } catch (error) {
    console.error('Error:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 3: POST - Create new property
 */
export async function example3_CreateProperty() {
  const newProperty = {
    name: 'Downtown Office Commons',
    address: '123 Main Street',
    city: 'Los Angeles',
    state: 'CA',
    zip_code: '90012',
    total_sqft: 50000,
    property_type: 'office',
    occupancy_rate: 92.5,
  };

  try {
    const response = await api.post('/properties', newProperty);
    console.log('Created property:', response.data);
    return response.data;
  } catch (error) {
    // Handle specific error types
    switch (error.error?.code) {
      case ERROR_CODES.VALIDATION_ERROR:
        console.error('Validation failed:', error.error.details);
        break;
      case ERROR_CODES.UNAUTHORIZED:
        console.error('Please log in first');
        break;
      default:
        console.error('Error:', api.getErrorMessage(error));
    }
    throw error;
  }
}

/**
 * Example 4: PUT - Update property
 */
export async function example4_UpdateProperty(propertyId, updates) {
  try {
    const response = await api.put(`/properties/${propertyId}`, updates);
    console.log('Updated property:', response.data);
    return response.data;
  } catch (error) {
    if (error.error?.code === ERROR_CODES.NOT_FOUND) {
      console.error(`Property ${propertyId} not found`);
    }
    throw error;
  }
}

/**
 * Example 5: DELETE - Delete property
 */
export async function example5_DeleteProperty(propertyId) {
  try {
    await api.delete(`/properties/${propertyId}`);
    console.log(`Property ${propertyId} deleted successfully`);
    return true;
  } catch (error) {
    console.error('Delete failed:', api.getErrorMessage(error));
    return false;
  }
}

/**
 * Example 6: File upload with FormData
 */
export async function example6_UploadDocument(file, propertyId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('property_id', propertyId);
  formData.append('document_type', 'financial');

  try {
    // Custom timeout for large files
    const response = await api.post('/documents/upload', formData, {
      timeout: 60000, // 60 seconds
    });
    console.log('Document uploaded:', response.data);
    return response.data;
  } catch (error) {
    if (error.error?.code === ERROR_CODES.TIMEOUT_ERROR) {
      console.error('Upload timed out. Try a smaller file.');
    } else if (error.error?.code === ERROR_CODES.VALIDATION_ERROR) {
      console.error('Invalid file type or size');
    }
    throw error;
  }
}

/**
 * Example 7: Authentication - Login
 */
export async function example7_Login(email, password) {
  try {
    const response = await api.post('/auth/login', { email, password });
    
    // Store tokens
    api.setToken(response.data.access_token, response.data.refresh_token);
    
    console.log('Login successful');
    return response.data.user;
  } catch (error) {
    if (error.error?.code === ERROR_CODES.UNAUTHORIZED) {
      console.error('Invalid email or password');
    } else {
      console.error('Login failed:', api.getErrorMessage(error));
    }
    throw error;
  }
}

/**
 * Example 8: Authentication - Logout
 */
export async function example8_Logout() {
  try {
    await api.post('/auth/logout');
    api.clearAuth();
    console.log('Logout successful');
  } catch (error) {
    // Clear auth even if API call fails
    api.clearAuth();
    console.error('Logout error:', api.getErrorMessage(error));
  }
}

/**
 * Example 9: Check authentication status
 */
export function example9_CheckAuth() {
  if (api.isAuthenticated()) {
    console.log('User is authenticated');
    const token = api.getToken();
    console.log('Token:', token);
    return true;
  } else {
    console.log('User is not authenticated');
    return false;
  }
}

/**
 * Example 10: Parallel requests
 */
export async function example10_ParallelRequests() {
  try {
    // Fetch multiple resources in parallel
    const [properties, documents, alerts] = await Promise.all([
      api.get('/properties'),
      api.get('/documents'),
      api.get('/alerts'),
    ]);

    return {
      properties: properties.data,
      documents: documents.data,
      alerts: alerts.data,
    };
  } catch (error) {
    console.error('One or more requests failed:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 11: Sequential requests with dependencies
 */
export async function example11_SequentialRequests(propertyId) {
  try {
    // Get property details
    const propertyResponse = await api.get(`/properties/${propertyId}`);
    const property = propertyResponse.data;

    // Get documents for this property
    const documentsResponse = await api.get(`/documents?property_id=${propertyId}`);
    const documents = documentsResponse.data;

    // Get alerts for this property
    const alertsResponse = await api.get(`/alerts?property_id=${propertyId}`);
    const alerts = alertsResponse.data;

    return {
      property,
      documents,
      alerts,
    };
  } catch (error) {
    console.error('Request chain failed:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 12: Retry logic
 */
export async function example12_RetryRequest(endpoint, maxRetries = 3) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      lastError = error;
      
      // Only retry on network or timeout errors
      if (
        error.error?.code === ERROR_CODES.NETWORK_ERROR ||
        error.error?.code === ERROR_CODES.TIMEOUT_ERROR
      ) {
        console.log(`Attempt ${attempt} failed, retrying...`);
        
        if (attempt < maxRetries) {
          // Wait before retry (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      } else {
        // Don't retry on other errors
        throw error;
      }
    }
  }

  throw lastError;
}

/**
 * Example 13: Pagination
 */
export async function example13_PaginatedRequest(page = 1, limit = 10) {
  try {
    const response = await api.get(`/properties?page=${page}&limit=${limit}`);
    
    return {
      data: response.data,
      pagination: {
        page,
        limit,
        total: response.data.total || 0,
        hasMore: response.data.length === limit,
      },
    };
  } catch (error) {
    console.error('Pagination failed:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 14: Download file
 */
export async function example14_DownloadReport(reportType, filters) {
  try {
    const response = await api.post('/reports/export', {
      type: reportType,
      filters,
      format: 'pdf',
    });

    // Backend should return a download URL
    const downloadUrl = response.data.download_url;
    
    // Trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = response.data.filename;
    link.click();

    return true;
  } catch (error) {
    console.error('Download failed:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 15: Batch operations
 */
export async function example15_BatchUpdate(updates) {
  try {
    const response = await api.post('/properties/batch-update', {
      updates,
    });

    console.log(`Updated ${response.data.updated_count} properties`);
    return response.data;
  } catch (error) {
    console.error('Batch update failed:', api.getErrorMessage(error));
    throw error;
  }
}

/**
 * Example 16: Search with debounce
 */
export async function example16_SearchProperties(query) {
  try {
    const response = await api.get(`/properties/search?q=${encodeURIComponent(query)}`);
    return response.data;
  } catch (error) {
    // Ignore errors if user is still typing
    if (error.error?.code === ERROR_CODES.TIMEOUT_ERROR) {
      console.log('Search cancelled or timed out');
      return [];
    }
    throw error;
  }
}

/**
 * Example 17: Loading state integration
 */
export function example17_LoadingStateHook() {
  let isLoading = false;

  // Subscribe to loading changes
  const unsubscribe = api.onLoadingChange((loading) => {
    isLoading = loading;
    console.log('Loading state:', loading);
    
    // Update UI
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
      spinner.style.display = loading ? 'block' : 'none';
    }
  });

  // Return cleanup function
  return unsubscribe;
}

/**
 * Example 18: Custom error handling per component
 */
export async function example18_ComponentWithErrorHandling() {
  try {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  } catch (error) {
    // Component-specific error handling
    const errorCode = error.error?.code;
    const errorMessage = api.getErrorMessage(error);

    // Show notification
    showNotification({
      type: 'error',
      title: getErrorTitle(errorCode),
      message: errorMessage,
      duration: 5000,
    });

    // Log to analytics
    logErrorEvent({
      code: errorCode,
      message: errorMessage,
      endpoint: '/analytics/dashboard',
    });

    // Return fallback data or throw
    if (errorCode === ERROR_CODES.NOT_FOUND) {
      return {}; // Empty dashboard
    }
    throw error;
  }
}

/**
 * Helper function for error titles
 */
function getErrorTitle(errorCode) {
  switch (errorCode) {
    case ERROR_CODES.NETWORK_ERROR:
      return 'Connection Error';
    case ERROR_CODES.TIMEOUT_ERROR:
      return 'Request Timeout';
    case ERROR_CODES.UNAUTHORIZED:
      return 'Authentication Required';
    case ERROR_CODES.FORBIDDEN:
      return 'Access Denied';
    case ERROR_CODES.NOT_FOUND:
      return 'Not Found';
    case ERROR_CODES.VALIDATION_ERROR:
      return 'Validation Error';
    case ERROR_CODES.SERVER_ERROR:
      return 'Server Error';
    default:
      return 'Error';
  }
}

/**
 * Placeholder functions (implement based on your UI framework)
 */
function showNotification() {
  // Implement with your notification system
}

function logErrorEvent() {
  // Implement with your analytics system
}

/**
 * Export all examples
 */
export default {
  example1_SimpleGet,
  example2_GetWithParams,
  example3_CreateProperty,
  example4_UpdateProperty,
  example5_DeleteProperty,
  example6_UploadDocument,
  example7_Login,
  example8_Logout,
  example9_CheckAuth,
  example10_ParallelRequests,
  example11_SequentialRequests,
  example12_RetryRequest,
  example13_PaginatedRequest,
  example14_DownloadReport,
  example15_BatchUpdate,
  example16_SearchProperties,
  example17_LoadingStateHook,
  example18_ComponentWithErrorHandling,
};

