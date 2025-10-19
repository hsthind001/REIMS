/**
 * Custom React Hooks
 * 
 * Export all custom hooks from this centralized location
 */

// Data fetching
export { useQuery, clearQueryCache, clearAllQueryCache } from './useQuery';

// Mutations (enhanced version)
export {
  useMutation,
  useOptimisticMutation,
  useQueryClient,
  useOptimisticUpdate,
  useBatchMutation,
  queryClient,
  createQueryClient,
} from './useMutation';

// Analytics and KPI data fetching
export {
  default as useAnalytics,
  useKPIs,
  useAnalyticsWithErrorBoundary,
  useRealTimeAnalytics,
  MOCK_ANALYTICS_DATA,
} from './useAnalytics';

// Properties list fetching (with pagination, filtering, sorting)
export {
  default as useProperties,
  useProperty,
  useInfiniteProperties,
  MOCK_PROPERTIES_DATA,
} from './useProperties';

// Document upload and processing status
export {
  default as useDocumentUpload,
  useDocumentStatus,
  useBatchDocumentUpload,
} from './useDocumentUpload';

// Alerts management and monitoring
export {
  default as useAlerts,
  useAlertDecision,
  usePropertyAlerts,
  useAlertNotifications,
  useAlertStats,
  MOCK_ALERTS_DATA,
} from './useAlerts';

// Lazy chart loading (performance optimization)
export { default as useLazyChart } from './useLazyChart';

// Re-export defaults
import useQuery from './useQuery';
export default useQuery;

