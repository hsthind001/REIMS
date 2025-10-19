// REIMS API Configuration - Optimized Production Version
// High-performance API client with caching, retry logic, and error handling

export const API_CONFIG = {
  // Backend API base URL - FIXED PORT 8001
  BASE_URL: 'http://localhost:8001',
  
  // Request timeout settings
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Cache settings
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Full API endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    SYSTEM_STATS: '/api/system/stats',
    DOCUMENTS_UPLOAD: '/api/documents/upload',
    DOCUMENTS_LIST: '/api/documents',
    DOCUMENTS_PROCESSED: (documentId) => `/api/documents/${documentId}/processed`,
    AI_PROCESS_STATUS: (documentId) => `/ai/process/${documentId}/status`,
    AI_PROCESSED_DATA: (documentId) => `/ai/processed-data/${documentId}`,
    PROPERTIES: '/api/properties',
    PROPERTY_ENDPOINTS: (endpoint) => `/api/property/${endpoint}`,
    ANALYTICS: '/api/analytics'
  }
};

// Simple in-memory cache
class APICache {
  constructor() {
    this.cache = new Map();
    this.timestamps = new Map();
  }
  
  set(key, data) {
    this.cache.set(key, data);
    this.timestamps.set(key, Date.now());
  }
  
  get(key) {
    const timestamp = this.timestamps.get(key);
    if (!timestamp || Date.now() - timestamp > API_CONFIG.CACHE_DURATION) {
      this.cache.delete(key);
      this.timestamps.delete(key);
      return null;
    }
    return this.cache.get(key);
  }
  
  clear() {
    this.cache.clear();
    this.timestamps.clear();
  }
  
  has(key) {
    return this.get(key) !== null;
  }
}

const apiCache = new APICache();

// Request queue for handling concurrent requests
const requestQueue = new Map();

// Helper function to build full URL
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper function to generate cache key
const getCacheKey = (url, options = {}) => {
  const method = options.method || 'GET';
  const body = options.body ? JSON.stringify(options.body) : '';
  return `${method}:${url}:${body}`;
};

// Sleep function for retry delays
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Enhanced fetch with retry logic
const fetchWithRetry = async (url, options = {}, attempts = API_CONFIG.RETRY_ATTEMPTS) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    if (attempts > 1 && !error.name === 'AbortError') {
      console.warn(`Request failed, retrying... (${API_CONFIG.RETRY_ATTEMPTS - attempts + 1}/${API_CONFIG.RETRY_ATTEMPTS})`);
      await sleep(API_CONFIG.RETRY_DELAY);
      return fetchWithRetry(url, options, attempts - 1);
    }
    throw error;
  }
};

// Enhanced API request function with caching and deduplication
export const apiRequest = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);
  const cacheKey = getCacheKey(url, options);
  const method = options.method || 'GET';
  
  // Only cache GET requests
  if (method === 'GET') {
    // Check cache first
    const cachedData = apiCache.get(cacheKey);
    if (cachedData) {
      console.log(`Cache hit for: ${endpoint}`);
      return { ...cachedData, fromCache: true };
    }
    
    // Check if same request is already in progress
    if (requestQueue.has(cacheKey)) {
      console.log(`Deduplicating request for: ${endpoint}`);
      return requestQueue.get(cacheKey);
    }
  }
  
  // Default headers with optimizations
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Cache-Control': method === 'GET' ? 'max-age=300' : 'no-cache',
    ...options.headers,
  };
  
  // Create request promise
  const requestPromise = (async () => {
    try {
      console.log(`API Request: ${method} ${endpoint}`);
      const startTime = performance.now();
      
      const response = await fetchWithRetry(url, {
        method,
        headers: defaultHeaders,
        ...options,
      });
      
      const endTime = performance.now();
      console.log(`API Response: ${method} ${endpoint} (${Math.round(endTime - startTime)}ms)`);
      
      // Parse response
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
      
      // Add metadata
      const result = {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        responseTime: Math.round(endTime - startTime),
        fromCache: false
      };
      
      // Cache GET requests
      if (method === 'GET' && response.ok) {
        apiCache.set(cacheKey, result);
      }
      
      return result;
      
    } catch (error) {
      console.error(`API Error: ${method} ${endpoint}`, error);
      
      // Enhanced error information
      const enhancedError = new Error(`API request failed: ${error.message}`);
      enhancedError.originalError = error;
      enhancedError.endpoint = endpoint;
      enhancedError.method = method;
      enhancedError.timestamp = new Date().toISOString();
      
      throw enhancedError;
    } finally {
      // Remove from request queue
      if (method === 'GET') {
        requestQueue.delete(cacheKey);
      }
    }
  })();
  
  // Add to request queue for deduplication
  if (method === 'GET') {
    requestQueue.set(cacheKey, requestPromise);
  }
  
  return requestPromise;
};

// Convenience methods for different HTTP verbs
export const apiGet = (endpoint, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
  return apiRequest(fullEndpoint, { method: 'GET' });
};

export const apiPost = (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

export const apiPut = (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
};

export const apiDelete = (endpoint) => {
  return apiRequest(endpoint, { method: 'DELETE' });
};

// Upload function with progress tracking
export const apiUpload = async (endpoint, formData, onProgress = null) => {
  const url = buildApiUrl(endpoint);
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    // Progress tracking
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          onProgress(percentComplete);
        }
      });
    }
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve({
            data: response,
            status: xhr.status,
            statusText: xhr.statusText,
            fromCache: false
          });
        } catch (e) {
          resolve({
            data: xhr.responseText,
            status: xhr.status,
            statusText: xhr.statusText,
            fromCache: false
          });
        }
      } else {
        reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
      }
    });
    
    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed: Network error'));
    });
    
    xhr.addEventListener('timeout', () => {
      reject(new Error('Upload failed: Timeout'));
    });
    
    xhr.timeout = API_CONFIG.TIMEOUT;
    xhr.open('POST', url);
    xhr.send(formData);
  });
};

// Health check function
export const checkBackendHealth = async () => {
  try {
    const response = await apiGet(API_CONFIG.ENDPOINTS.HEALTH);
    return {
      healthy: true,
      data: response.data,
      responseTime: response.responseTime
    };
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

// Cache management
export const clearCache = () => {
  apiCache.clear();
  console.log('API cache cleared');
};

export const getCacheStats = () => {
  return {
    size: apiCache.cache.size,
    keys: Array.from(apiCache.cache.keys())
  };
};

// Global error handler
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason && event.reason.endpoint) {
    console.error('Unhandled API error:', event.reason);
    // You could send this to an error reporting service
  }
});

// Preload critical data
export const preloadCriticalData = async () => {
  try {
    console.log('Preloading critical data...');
    const promises = [
      checkBackendHealth(),
      apiGet(API_CONFIG.ENDPOINTS.ANALYTICS),
      apiGet(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST, { limit: 10 })
    ];
    
    await Promise.allSettled(promises);
    console.log('Critical data preloaded');
  } catch (error) {
    console.warn('Failed to preload some critical data:', error);
  }
};