/**
 * REIMS API Module
 * 
 * Central export point for all API-related functionality
 */

// Export default API client
export { default } from './client';

// Export named exports
export { APIClient, api, ERROR_CODES } from './client';

// Export examples (optional - for development reference)
export { default as examples } from './examples';

