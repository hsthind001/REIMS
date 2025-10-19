import React, { useState } from 'react';
import { useAlertDecision } from '../hooks/useAlerts';

/**
 * Alert Card Component
 * 
 * Displays an alert with approve/reject actions
 * 
 * Props:
 * - alert: Alert object
 * - onDecision: Callback when decision is made
 * - userId: Current user ID
 * - compact: Show compact version
 */
export default function AlertCard({ alert, onDecision, userId, compact = false }) {
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [notes, setNotes] = useState('');
  const [rejectReason, setRejectReason] = useState('');

  const { approve, reject, isApproving, isRejecting, isProcessing } = useAlertDecision({
    onSuccess: (data, decision) => {
      if (onDecision) {
        onDecision(alert, decision);
      }
      setShowRejectModal(false);
      setNotes('');
      setRejectReason('');
    },
    onError: (error) => {
      console.error('Decision failed:', error);
      alert('Failed to process decision. Please try again.');
    },
  });

  const handleApprove = () => {
    approve({
      alertId: alert.id,
      userId,
      notes,
    });
  };

  const handleReject = () => {
    if (!rejectReason) {
      alert('Please select a reason for rejection');
      return;
    }

    reject({
      alertId: alert.id,
      userId,
      notes,
      reason: rejectReason,
    });
  };

  // Get level color
  const getLevelColor = () => {
    switch (alert.level) {
      case 'critical':
        return 'red';
      case 'warning':
        return 'yellow';
      case 'info':
        return 'blue';
      default:
        return 'gray';
    }
  };

  const color = getLevelColor();

  // Get alert icon
  const getAlertIcon = () => {
    if (alert.level === 'critical') {
      return (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    }

    if (alert.level === 'warning') {
      return (
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      );
    }

    return (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
    );
  };

  // Format time ago
  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  if (compact) {
    return (
      <div
        className={`
          bg-white border-l-4 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow
          ${color === 'red' ? 'border-red-500' : ''}
          ${color === 'yellow' ? 'border-yellow-500' : ''}
          ${color === 'blue' ? 'border-blue-500' : ''}
        `}
      >
        <div className="flex items-start gap-3">
          <div className={`
            ${color === 'red' ? 'text-red-600' : ''}
            ${color === 'yellow' ? 'text-yellow-600' : ''}
            ${color === 'blue' ? 'text-blue-600' : ''}
          `}>
            {getAlertIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 truncate">
              {alert.property_name}
            </h4>
            <p className="text-sm text-gray-600 mt-1">
              {alert.description}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div
        className={`
          bg-white border-l-4 rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow
          ${color === 'red' ? 'border-red-500' : ''}
          ${color === 'yellow' ? 'border-yellow-500' : ''}
          ${color === 'blue' ? 'border-blue-500' : ''}
        `}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            <div className={`
              ${color === 'red' ? 'text-red-600' : ''}
              ${color === 'yellow' ? 'text-yellow-600' : ''}
              ${color === 'blue' ? 'text-blue-600' : ''}
            `}>
              {getAlertIcon()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span
                  className={`
                    px-2 py-1 rounded text-xs font-semibold uppercase
                    ${color === 'red' ? 'bg-red-100 text-red-800' : ''}
                    ${color === 'yellow' ? 'bg-yellow-100 text-yellow-800' : ''}
                    ${color === 'blue' ? 'bg-blue-100 text-blue-800' : ''}
                  `}
                >
                  {alert.level}
                </span>
                <span className="text-sm text-gray-500">
                  {formatTimeAgo(alert.created_at)}
                </span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mt-2">
                {alert.property_name}
              </h3>
            </div>
          </div>
        </div>

        {/* Alert Details */}
        <div className="space-y-3 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700">{alert.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Current Value</p>
              <p className="text-lg font-semibold text-gray-900">
                {typeof alert.value === 'number' && alert.value < 1
                  ? `${(alert.value * 100).toFixed(1)}%`
                  : alert.value}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Threshold</p>
              <p className="text-lg font-semibold text-gray-900">
                {typeof alert.threshold === 'number' && alert.threshold < 1
                  ? `${(alert.threshold * 100).toFixed(1)}%`
                  : alert.threshold}
              </p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-500">Committee</p>
            <p className="font-medium text-gray-900">{alert.committee}</p>
          </div>
        </div>

        {/* Actions */}
        {alert.status === 'pending' && (
          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              disabled={isProcessing}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isApproving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Approving...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Approve
                </>
              )}
            </button>

            <button
              onClick={() => setShowRejectModal(true)}
              disabled={isProcessing}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Reject
            </button>
          </div>
        )}

        {alert.status !== 'pending' && (
          <div className={`
            px-4 py-3 rounded-lg text-center font-medium
            ${alert.status === 'approved' ? 'bg-green-100 text-green-800' : ''}
            ${alert.status === 'rejected' ? 'bg-red-100 text-red-800' : ''}
          `}>
            {alert.status === 'approved' ? '✓ Approved' : '✗ Rejected'}
            {alert.approved_by && (
              <span className="text-sm ml-2">by {alert.approved_by}</span>
            )}
          </div>
        )}
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Reject Alert
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Rejection *
                </label>
                <select
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  <option value="">Select a reason...</option>
                  <option value="data_incorrect">Data is incorrect</option>
                  <option value="already_addressed">Already addressed</option>
                  <option value="not_urgent">Not urgent</option>
                  <option value="requires_review">Requires further review</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Add any additional context..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowRejectModal(false)}
                disabled={isRejecting}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 disabled:opacity-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={isRejecting || !rejectReason}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {isRejecting ? 'Rejecting...' : 'Confirm Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/**
 * Alert Badge Component
 * Shows alert count in navigation
 */
export function AlertBadge({ count, level = 'all' }) {
  if (!count || count === 0) return null;

  const getColor = () => {
    if (level === 'critical') return 'bg-red-600';
    if (level === 'warning') return 'bg-yellow-500';
    return 'bg-blue-600';
  };

  return (
    <span
      className={`
        ${getColor()}
        text-white text-xs font-bold rounded-full
        px-2 py-0.5 min-w-[20px] text-center
        animate-pulse
      `}
    >
      {count > 99 ? '99+' : count}
    </span>
  );
}

