import React, { useState } from 'react';
import { useAlerts, useAlertStats } from '../hooks/useAlerts';
import AlertCard, { AlertBadge } from '../components/AlertCard';

/**
 * Alerts Center Page
 * 
 * Central hub for viewing and managing all alerts
 * 
 * Features:
 * - Real-time alert polling (every 30s)
 * - Filter by level (critical, warning, info)
 * - Filter by committee
 * - Alert statistics
 * - Approve/reject actions
 * - Auto-refresh
 */
export default function AlertsCenter() {
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedCommittee, setSelectedCommittee] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('pending');

  // Fetch alerts with filters
  const {
    alerts,
    total,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    criticalCount,
    warningCount,
    infoCount,
    alertsByCommittee,
    isLoading,
    error,
    refetch,
  } = useAlerts({
    pollInterval: 30000, // 30 seconds
    status: selectedStatus !== 'all' ? selectedStatus : undefined,
    level: selectedLevel !== 'all' ? selectedLevel : undefined,
    committee: selectedCommittee !== 'all' ? selectedCommittee : undefined,
  });

  // Fetch statistics
  const { stats, isLoading: statsLoading } = useAlertStats();

  // Get unique committees
  const committees = Object.keys(alertsByCommittee);

  // Handle alert decision
  const handleAlertDecision = (alert, decision) => {
    console.log('Alert decision:', alert.id, decision);
    
    // Show success message
    const message = decision === 'approved' 
      ? '✓ Alert approved successfully'
      : '✗ Alert rejected successfully';
    
    // You can implement toast notifications here
    alert(message);

    // Refetch alerts
    setTimeout(() => {
      refetch();
    }, 500);
  };

  // Get filtered alerts for display
  const getFilteredAlerts = () => {
    if (selectedLevel === 'all') {
      return alerts;
    }

    switch (selectedLevel) {
      case 'critical':
        return criticalAlerts;
      case 'warning':
        return warningAlerts;
      case 'info':
        return infoAlerts;
      default:
        return alerts;
    }
  };

  const filteredAlerts = getFilteredAlerts();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Alerts Center
              </h1>
              <p className="text-gray-600 mt-1">
                Monitor and manage property alerts requiring committee review
              </p>
            </div>

            <button
              onClick={refetch}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                  Refresh
                </>
              )}
            </button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <StatCard
              label="Total Pending"
              value={stats.total_pending || total}
              color="blue"
              icon="📋"
            />
            <StatCard
              label="Critical"
              value={criticalCount}
              color="red"
              icon="🚨"
            />
            <StatCard
              label="Warning"
              value={warningCount}
              color="yellow"
              icon="⚠️"
            />
            <StatCard
              label="Avg Response Time"
              value={`${stats.avg_response_time_hours || 0}h`}
              color="green"
              icon="⏱️"
            />
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Alert Level
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedLevel('all')}
                  className={`
                    flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                    ${selectedLevel === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }
                  `}
                >
                  All <AlertBadge count={total} />
                </button>
                <button
                  onClick={() => setSelectedLevel('critical')}
                  className={`
                    flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                    ${selectedLevel === 'critical'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }
                  `}
                >
                  Critical <AlertBadge count={criticalCount} level="critical" />
                </button>
                <button
                  onClick={() => setSelectedLevel('warning')}
                  className={`
                    flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                    ${selectedLevel === 'warning'
                      ? 'bg-yellow-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }
                  `}
                >
                  Warning <AlertBadge count={warningCount} level="warning" />
                </button>
              </div>
            </div>

            {/* Committee Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Committee
              </label>
              <select
                value={selectedCommittee}
                onChange={(e) => setSelectedCommittee(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Committees</option>
                {committees.map((committee) => (
                  <option key={committee} value={committee}>
                    {committee} ({alertsByCommittee[committee].length})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="font-medium text-red-900">Failed to load alerts</h4>
                <p className="text-sm text-red-700 mt-1">{error.message || error}</p>
                <button
                  onClick={refetch}
                  className="text-sm text-red-600 font-medium hover:text-red-700 mt-2"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && !filteredAlerts.length && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredAlerts.length === 0 && (
          <div className="bg-white rounded-lg p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No alerts found
            </h3>
            <p className="text-gray-600">
              {selectedLevel !== 'all' || selectedCommittee !== 'all'
                ? 'Try adjusting your filters'
                : 'All properties are within acceptable thresholds'}
            </p>
          </div>
        )}

        {/* Alerts List */}
        {!isLoading && filteredAlerts.length > 0 && (
          <div className="space-y-4">
            {filteredAlerts.map((alert) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onDecision={handleAlertDecision}
                userId="current-user-id" // Replace with actual user ID
              />
            ))}
          </div>
        )}

        {/* Auto-refresh indicator */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Auto-refreshing every 30 seconds
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Stat Card Component
 */
function StatCard({ label, value, color, icon }) {
  const getColorClasses = () => {
    switch (color) {
      case 'red':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'yellow':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      case 'green':
        return 'bg-green-50 border-green-200 text-green-900';
      case 'blue':
        return 'bg-blue-50 border-blue-200 text-blue-900';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-900';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getColorClasses()}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm opacity-80">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-3xl opacity-60">{icon}</div>
      </div>
    </div>
  );
}

