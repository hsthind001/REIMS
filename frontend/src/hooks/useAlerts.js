import { useState, useCallback, useEffect } from 'react';
import { useQuery } from './useQuery';
import { useMutation } from './useMutation';
import api from '../api';

/**
 * Hook for fetching pending alerts
 * Polls every 30 seconds for real-time updates
 * 
 * @param {Object} options - Hook configuration
 * @param {number} options.pollInterval - Polling interval in ms (default: 30000)
 * @param {string} options.status - Filter by status (default: 'pending')
 * @param {string} options.level - Filter by level (critical, warning, info)
 * @param {string} options.committee - Filter by committee
 * 
 * @returns {Object} Alerts state and functions
 */
export function useAlerts(options = {}) {
  const {
    pollInterval = 30000, // 30 seconds
    status = 'pending',
    level,
    committee,
    enabled = true,
  } = options;

  // Build query params
  const queryParams = new URLSearchParams();
  if (status) queryParams.append('status', status);
  if (level) queryParams.append('level', level);
  if (committee) queryParams.append('committee', committee);

  const queryString = queryParams.toString();
  const endpoint = `/api/alerts${queryString ? `?${queryString}` : ''}`;

  // Fetch alerts with auto-refetch
  const {
    data,
    isLoading,
    error,
    refetch,
    isError,
    isSuccess,
  } = useQuery(
    `alerts-${status}-${level || 'all'}-${committee || 'all'}`,
    async () => {
      const response = await api.get(endpoint);
      return response.data || response;
    },
    {
      refetchInterval: pollInterval,
      staleTime: 10000, // 10 seconds
      enabled,
      retry: 2,
    }
  );

  // Parse alerts data
  const alerts = data?.alerts || [];
  const total = data?.total || alerts.length;

  // Group alerts by level
  const criticalAlerts = alerts.filter(a => a.level === 'critical');
  const warningAlerts = alerts.filter(a => a.level === 'warning');
  const infoAlerts = alerts.filter(a => a.level === 'info');

  // Group by committee
  const alertsByCommittee = alerts.reduce((acc, alert) => {
    const committee = alert.committee || 'Other';
    if (!acc[committee]) acc[committee] = [];
    acc[committee].push(alert);
    return acc;
  }, {});

  return {
    alerts,
    total,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    alertsByCommittee,
    criticalCount: criticalAlerts.length,
    warningCount: warningAlerts.length,
    infoCount: infoAlerts.length,
    isLoading,
    error,
    isError,
    isSuccess,
    refetch,
  };
}

/**
 * Hook for handling alert decisions (approve/reject)
 * 
 * @param {Object} options - Hook configuration
 * @param {Function} options.onSuccess - Callback on successful decision
 * @param {Function} options.onError - Callback on error
 * 
 * @returns {Object} Decision mutation functions
 */
export function useAlertDecision(options = {}) {
  const { onSuccess, onError } = options;

  // Approve mutation
  const {
    mutate: approve,
    isLoading: isApproving,
    error: approveError,
  } = useMutation(
    async ({ alertId, userId, notes }) => {
      return await api.post(`/api/alerts/${alertId}/approve`, {
        decision: 'approved',
        user_id: userId,
        notes,
      });
    },
    {
      onSuccess: (data) => {
        console.log('Alert approved:', data);
        if (onSuccess) onSuccess(data, 'approved');
      },
      onError: (error) => {
        console.error('Failed to approve alert:', error);
        if (onError) onError(error, 'approved');
      },
    }
  );

  // Reject mutation
  const {
    mutate: reject,
    isLoading: isRejecting,
    error: rejectError,
  } = useMutation(
    async ({ alertId, userId, notes, reason }) => {
      return await api.post(`/api/alerts/${alertId}/reject`, {
        decision: 'rejected',
        user_id: userId,
        notes,
        reason,
      });
    },
    {
      onSuccess: (data) => {
        console.log('Alert rejected:', data);
        if (onSuccess) onSuccess(data, 'rejected');
      },
      onError: (error) => {
        console.error('Failed to reject alert:', error);
        if (onError) onError(error, 'rejected');
      },
    }
  );

  return {
    approve,
    reject,
    isApproving,
    isRejecting,
    isProcessing: isApproving || isRejecting,
    approveError,
    rejectError,
    error: approveError || rejectError,
  };
}

/**
 * Hook for fetching alert history for a property
 * 
 * @param {string} propertyId - Property ID
 * @param {Object} options - Hook configuration
 * 
 * @returns {Object} Alert history state
 */
export function usePropertyAlerts(propertyId, options = {}) {
  const {
    limit = 50,
    enabled = true,
  } = options;

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery(
    `property-alerts-${propertyId}`,
    async () => {
      const response = await api.get(`/api/properties/${propertyId}/alerts?limit=${limit}`);
      return response.data || response;
    },
    {
      enabled: enabled && !!propertyId,
      staleTime: 60000, // 1 minute
      retry: 1,
    }
  );

  const alerts = data?.alerts || [];

  return {
    alerts,
    total: data?.total || alerts.length,
    isLoading,
    error,
    refetch,
  };
}

/**
 * Hook for real-time alert notifications
 * Shows browser notifications for new alerts
 * 
 * @param {Object} options - Hook configuration
 * 
 * @returns {Object} Notification state and functions
 */
export function useAlertNotifications(options = {}) {
  const {
    enabled = true,
    soundEnabled = true,
  } = options;

  const [notificationPermission, setNotificationPermission] = useState('default');
  const [lastAlertCount, setLastAlertCount] = useState(0);

  // Request notification permission
  useEffect(() => {
    if (!enabled || !('Notification' in window)) return;

    if (Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        setNotificationPermission(permission);
      });
    } else {
      setNotificationPermission(Notification.permission);
    }
  }, [enabled]);

  // Monitor alert count changes
  const { total: currentAlertCount } = useAlerts({
    enabled,
    pollInterval: 30000,
  });

  useEffect(() => {
    if (!enabled || currentAlertCount === 0) return;

    // Check if new alerts appeared
    if (currentAlertCount > lastAlertCount && lastAlertCount > 0) {
      const newAlertsCount = currentAlertCount - lastAlertCount;
      
      // Show browser notification
      if (notificationPermission === 'granted') {
        new Notification('New Alert', {
          body: `${newAlertsCount} new alert${newAlertsCount > 1 ? 's' : ''} require your attention`,
          icon: '/alert-icon.png',
          tag: 'reims-alert',
        });
      }

      // Play sound
      if (soundEnabled) {
        try {
          const audio = new Audio('/alert-sound.mp3');
          audio.play().catch(() => {
            // Ignore audio play errors
          });
        } catch (err) {
          console.warn('Failed to play alert sound:', err);
        }
      }
    }

    setLastAlertCount(currentAlertCount);
  }, [currentAlertCount, lastAlertCount, notificationPermission, soundEnabled, enabled]);

  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      return 'unsupported';
    }

    const permission = await Notification.requestPermission();
    setNotificationPermission(permission);
    return permission;
  }, []);

  return {
    notificationPermission,
    isSupported: 'Notification' in window,
    isEnabled: notificationPermission === 'granted',
    requestPermission,
    newAlertsCount: Math.max(0, currentAlertCount - lastAlertCount),
  };
}

/**
 * Hook for alert statistics
 * 
 * @returns {Object} Alert statistics
 */
export function useAlertStats() {
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery(
    'alert-stats',
    async () => {
      const response = await api.get('/api/alerts/stats');
      return response.data || response;
    },
    {
      refetchInterval: 60000, // 1 minute
      staleTime: 30000, // 30 seconds
      retry: 2,
    }
  );

  const stats = data || {
    total_pending: 0,
    total_approved: 0,
    total_rejected: 0,
    by_level: {
      critical: 0,
      warning: 0,
      info: 0,
    },
    by_committee: {},
    avg_response_time_hours: 0,
    oldest_pending_days: 0,
  };

  return {
    stats,
    isLoading,
    error,
    refetch,
    totalPending: stats.total_pending,
    totalApproved: stats.total_approved,
    totalRejected: stats.total_rejected,
    criticalCount: stats.by_level?.critical || 0,
    warningCount: stats.by_level?.warning || 0,
    infoCount: stats.by_level?.info || 0,
  };
}

/**
 * Mock alerts data for demo/testing
 */
export const MOCK_ALERTS_DATA = {
  alerts: [
    {
      id: 'alert-001',
      property_id: 'prop-001',
      property_name: 'Downtown Office Commons',
      alert_type: 'dscr_low',
      value: 1.15,
      threshold: 1.25,
      level: 'critical',
      committee: 'Finance Sub-Committee',
      status: 'pending',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      description: 'DSCR has fallen below the required threshold of 1.25',
    },
    {
      id: 'alert-002',
      property_id: 'prop-002',
      property_name: 'Sunset Plaza Retail',
      alert_type: 'occupancy_low',
      value: 0.82,
      threshold: 0.85,
      level: 'warning',
      committee: 'Occupancy Sub-Committee',
      status: 'pending',
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
      description: 'Occupancy rate has dropped below 85%',
    },
    {
      id: 'alert-003',
      property_id: 'prop-003',
      property_name: 'Harbor View Apartments',
      alert_type: 'anomaly_detected',
      value: 2.3,
      threshold: 2.0,
      level: 'info',
      committee: 'Risk Committee',
      status: 'pending',
      created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
      description: 'Statistical anomaly detected in NOI trend (Z-score: 2.3)',
    },
  ],
  total: 3,
};

export default useAlerts;

