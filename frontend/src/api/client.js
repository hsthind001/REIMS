/**
 * REIMS API Client
 * 
 * Centralized API client with request/response interceptors,
 * error handling, loading state management, and JWT token support.
 * 
 * Features:
 * - Base URL configuration with environment fallback
 * - Request/response interceptors
 * - Centralized error handling with user-friendly messages
 * - Loading state management
 * - JWT token management for authentication
 * - 30-second request timeout
 * - Standardized response format handling
 * 
 * Usage:
 *   import api from '@/api/client';
 *   
 *   const data = await api.get('/properties');
 *   const result = await api.post('/documents/upload', formData);
 *   const updated = await api.put('/properties/123', updateData);
 *   await api.delete('/properties/123');
 */

/**
 * API Configuration
 */
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Error Codes
 */
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  CLIENT_ERROR: 'CLIENT_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

/**
 * Loading State Manager
 * Tracks active requests to manage loading states
 */
class LoadingStateManager {
  constructor() {
    this.activeRequests = new Set();
    this.listeners = new Set();
  }

  startRequest(requestId) {
    this.activeRequests.add(requestId);
    this.notifyListeners();
  }

  endRequest(requestId) {
    this.activeRequests.delete(requestId);
    this.notifyListeners();
  }

  isLoading() {
    return this.activeRequests.size > 0;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners() {
    const isLoading = this.isLoading();
    this.listeners.forEach(listener => listener(isLoading));
  }
}

/**
 * Token Manager
 * Handles JWT token storage and retrieval
 */
class TokenManager {
  constructor() {
    this.storageKey = 'reims_auth_token';
    this.refreshTokenKey = 'reims_refresh_token';
  }

  getToken() {
    return localStorage.getItem(this.storageKey);
  }

  setToken(token) {
    if (token) {
      localStorage.setItem(this.storageKey, token);
    } else {
      localStorage.removeItem(this.storageKey);
    }
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  setRefreshToken(token) {
    if (token) {
      localStorage.setItem(this.refreshTokenKey, token);
    } else {
      localStorage.removeItem(this.refreshTokenKey);
    }
  }

  clearTokens() {
    localStorage.removeItem(this.storageKey);
    localStorage.removeItem(this.refreshTokenKey);
  }

  isTokenExpired(token) {
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = payload.exp * 1000; // Convert to milliseconds
      return Date.now() >= expiry;
    } catch (error) {
      return true;
    }
  }
}

/**
 * API Client Class
 */
class APIClient {
  constructor(config = {}) {
    this.config = { ...API_CONFIG, ...config };
    this.loadingManager = new LoadingStateManager();
    this.tokenManager = new TokenManager();
    this.requestInterceptors = [];
    this.responseInterceptors = [];
  }

  /**
   * Add request interceptor
   * @param {Function} interceptor - Function that receives and returns config
   */
  addRequestInterceptor(interceptor) {
    this.requestInterceptors.push(interceptor);
  }

  /**
   * Add response interceptor
   * @param {Function} interceptor - Function that receives and returns response
   */
  addResponseInterceptor(interceptor) {
    this.responseInterceptors.push(interceptor);
  }

  /**
   * Apply request interceptors
   */
  async applyRequestInterceptors(config) {
    let modifiedConfig = { ...config };
    
    for (const interceptor of this.requestInterceptors) {
      modifiedConfig = await interceptor(modifiedConfig);
    }
    
    return modifiedConfig;
  }

  /**
   * Apply response interceptors
   */
  async applyResponseInterceptors(response) {
    let modifiedResponse = response;
    
    for (const interceptor of this.responseInterceptors) {
      modifiedResponse = await interceptor(modifiedResponse);
    }
    
    return modifiedResponse;
  }

  /**
   * Build full URL
   */
  buildURL(endpoint) {
    const baseURL = this.config.baseURL.replace(/\/$/, '');
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${baseURL}${path}`;
  }

  /**
   * Build request headers
   */
  buildHeaders(customHeaders = {}) {
    const headers = { ...this.config.headers };
    
    // Add authorization token if available
    const token = this.tokenManager.getToken();
    if (token && !this.tokenManager.isTokenExpired(token)) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Merge custom headers
    Object.keys(customHeaders).forEach(key => {
      if (customHeaders[key] !== undefined) {
        headers[key] = customHeaders[key];
      }
    });
    
    return headers;
  }

  /**
   * Create timeout promise
   */
  createTimeoutPromise(timeout) {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error('Request timeout'));
      }, timeout);
    });
  }

  /**
   * Handle API errors
   */
  handleError(error, response = null) {
    const errorResponse = {
      success: false,
      error: {
        code: ERROR_CODES.UNKNOWN_ERROR,
        message: 'An unexpected error occurred',
        details: null,
      },
      timestamp: new Date().toISOString(),
    };

    // Network error
    if (error.message === 'Failed to fetch') {
      errorResponse.error.code = ERROR_CODES.NETWORK_ERROR;
      errorResponse.error.message = 'Network error. Please check your connection.';
    }
    // Timeout error
    else if (error.message === 'Request timeout') {
      errorResponse.error.code = ERROR_CODES.TIMEOUT_ERROR;
      errorResponse.error.message = 'Request timed out. Please try again.';
    }
    // HTTP errors
    else if (response) {
      const status = response.status;
      
      if (status === 401) {
        errorResponse.error.code = ERROR_CODES.UNAUTHORIZED;
        errorResponse.error.message = 'Unauthorized. Please log in.';
      } else if (status === 403) {
        errorResponse.error.code = ERROR_CODES.FORBIDDEN;
        errorResponse.error.message = 'Access forbidden. You do not have permission.';
      } else if (status === 404) {
        errorResponse.error.code = ERROR_CODES.NOT_FOUND;
        errorResponse.error.message = 'Resource not found.';
      } else if (status === 422) {
        errorResponse.error.code = ERROR_CODES.VALIDATION_ERROR;
        errorResponse.error.message = 'Validation error. Please check your input.';
      } else if (status >= 400 && status < 500) {
        errorResponse.error.code = ERROR_CODES.CLIENT_ERROR;
        errorResponse.error.message = 'Client error. Please check your request.';
      } else if (status >= 500) {
        errorResponse.error.code = ERROR_CODES.SERVER_ERROR;
        errorResponse.error.message = 'Server error. Please try again later.';
      }
    }
    // Generic error
    else if (error.message) {
      errorResponse.error.message = error.message;
      errorResponse.error.details = error.toString();
    }

    return errorResponse;
  }

  /**
   * Get user-friendly error message
   */
  getErrorMessage(error) {
    if (typeof error === 'string') {
      return error;
    }

    if (error?.error?.message) {
      return error.error.message;
    }

    if (error?.message) {
      return error.message;
    }

    switch (error?.error?.code) {
      case ERROR_CODES.NETWORK_ERROR:
        return 'Unable to connect to the server. Please check your internet connection.';
      case ERROR_CODES.TIMEOUT_ERROR:
        return 'The request took too long. Please try again.';
      case ERROR_CODES.UNAUTHORIZED:
        return 'You need to log in to access this resource.';
      case ERROR_CODES.FORBIDDEN:
        return 'You do not have permission to perform this action.';
      case ERROR_CODES.NOT_FOUND:
        return 'The requested resource was not found.';
      case ERROR_CODES.VALIDATION_ERROR:
        return 'Please check your input and try again.';
      case ERROR_CODES.SERVER_ERROR:
        return 'A server error occurred. Please try again later.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }

  /**
   * Main API call function
   * @param {string} method - HTTP method (GET, POST, PUT, DELETE, PATCH)
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request payload
   * @param {Object} options - Additional options (headers, timeout, etc.)
   */
  async apiCall(method, endpoint, data = null, options = {}) {
    const requestId = `${method}-${endpoint}-${Date.now()}`;
    
    try {
      // Start loading
      this.loadingManager.startRequest(requestId);

      // Build request config
      let config = {
        method: method.toUpperCase(),
        headers: this.buildHeaders(options.headers),
      };

      // Add body for non-GET requests
      if (data && method.toUpperCase() !== 'GET') {
        // Handle FormData (for file uploads)
        if (data instanceof FormData) {
          delete config.headers['Content-Type']; // Let browser set it with boundary
          config.body = data;
        } else {
          config.body = JSON.stringify(data);
        }
      }

      // Apply request interceptors
      config = await this.applyRequestInterceptors(config);

      // Build full URL
      const url = this.buildURL(endpoint);

      // Create fetch promise with timeout
      const timeout = options.timeout || this.config.timeout;
      const fetchPromise = fetch(url, config);
      const timeoutPromise = this.createTimeoutPromise(timeout);

      // Race between fetch and timeout
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      // Parse response
      let responseData;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      // Check if response is OK
      if (!response.ok) {
        // Handle HTTP errors
        const errorResponse = this.handleError(
          new Error(`HTTP ${response.status}`),
          response
        );
        
        // If backend provides error details, use them
        if (responseData && typeof responseData === 'object') {
          errorResponse.error.message = responseData.message || responseData.error || errorResponse.error.message;
          errorResponse.error.details = responseData.details || responseData;
        }
        
        throw errorResponse;
      }

      // Normalize response format
      let normalizedResponse;
      
      if (typeof responseData === 'object' && responseData !== null) {
        // If response already has our format
        if ('success' in responseData || 'error' in responseData) {
          normalizedResponse = responseData;
        } else {
          // Wrap in standard format
          normalizedResponse = {
            success: true,
            data: responseData,
            timestamp: new Date().toISOString(),
          };
        }
      } else {
        // Handle non-object responses
        normalizedResponse = {
          success: true,
          data: responseData,
          timestamp: new Date().toISOString(),
        };
      }

      // Apply response interceptors
      normalizedResponse = await this.applyResponseInterceptors(normalizedResponse);

      return normalizedResponse;

    } catch (error) {
      // Handle errors
      if (error.success === false) {
        // Already formatted error from handleError
        throw error;
      } else {
        // Unhandled error
        const errorResponse = this.handleError(error);
        throw errorResponse;
      }
    } finally {
      // End loading
      this.loadingManager.endRequest(requestId);
    }
  }

  /**
   * Convenience methods
   */

  async get(endpoint, options = {}) {
    return this.apiCall('GET', endpoint, null, options);
  }

  async post(endpoint, data, options = {}) {
    return this.apiCall('POST', endpoint, data, options);
  }

  async put(endpoint, data, options = {}) {
    return this.apiCall('PUT', endpoint, data, options);
  }

  async patch(endpoint, data, options = {}) {
    return this.apiCall('PATCH', endpoint, data, options);
  }

  async delete(endpoint, options = {}) {
    return this.apiCall('DELETE', endpoint, null, options);
  }

  /**
   * Authentication methods
   */

  setAuthToken(token, refreshToken = null) {
    this.tokenManager.setToken(token);
    if (refreshToken) {
      this.tokenManager.setRefreshToken(refreshToken);
    }
  }

  getAuthToken() {
    return this.tokenManager.getToken();
  }

  clearAuth() {
    this.tokenManager.clearTokens();
  }

  isAuthenticated() {
    const token = this.tokenManager.getToken();
    return token && !this.tokenManager.isTokenExpired(token);
  }

  /**
   * Loading state management
   */

  isLoading() {
    return this.loadingManager.isLoading();
  }

  onLoadingChange(callback) {
    return this.loadingManager.subscribe(callback);
  }
}

/**
 * Create and export default API client instance
 */
const apiClient = new APIClient();

// Add default request interceptor for logging (development only)
if (import.meta.env.DEV) {
  apiClient.addRequestInterceptor((config) => {
    console.log('[API Request]', config.method, config);
    return config;
  });

  apiClient.addResponseInterceptor((response) => {
    console.log('[API Response]', response);
    return response;
  });
}

// Export both the class and default instance
export { APIClient, apiClient as default };

/**
 * Export utility functions for direct use
 */
export const api = {
  get: (endpoint, options) => apiClient.get(endpoint, options),
  post: (endpoint, data, options) => apiClient.post(endpoint, data, options),
  put: (endpoint, data, options) => apiClient.put(endpoint, data, options),
  patch: (endpoint, data, options) => apiClient.patch(endpoint, data, options),
  delete: (endpoint, options) => apiClient.delete(endpoint, options),
  
  // Auth helpers
  setToken: (token, refreshToken) => apiClient.setAuthToken(token, refreshToken),
  getToken: () => apiClient.getAuthToken(),
  clearAuth: () => apiClient.clearAuth(),
  isAuthenticated: () => apiClient.isAuthenticated(),
  
  // Loading state
  isLoading: () => apiClient.isLoading(),
  onLoadingChange: (callback) => apiClient.onLoadingChange(callback),
  
  // Error handling
  getErrorMessage: (error) => apiClient.getErrorMessage(error),
  ERROR_CODES,
};

