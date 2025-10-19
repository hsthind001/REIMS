import React, { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Home,
  Users,
  Bell,
  Volume2,
  VolumeX,
  Filter,
  X
} from 'lucide-react'

/**
 * REIMS Alerts Center
 * 
 * Features:
 * - Critical alerts (red, animated)
 * - Warning alerts (yellow)
 * - Info alerts (blue)
 * - Property name & triggering metric
 * - Current value vs threshold
 * - Committee responsible
 * - Approve/Reject actions
 * - Time created
 * - Sliding animations
 * - Sound notifications
 */

// Alert types
const ALERT_TYPES = {
  CRITICAL: 'critical',
  WARNING: 'warning',
  INFO: 'info'
}

// Committees
const COMMITTEES = {
  FINANCE: 'Finance Committee',
  OPERATIONS: 'Operations Committee',
  ASSET_MANAGEMENT: 'Asset Management Committee',
  EXECUTIVE: 'Executive Committee',
  RISK: 'Risk Management Committee'
}

// Generate sample alerts - using real property data
const generateSampleAlerts = () => [
  {
    id: 1,
    type: ALERT_TYPES.INFO,
    propertyName: 'Empire State Plaza',
    metric: 'Document Processing',
    currentValue: 6,
    threshold: 5,
    unit: 'docs',
    direction: 'above',
    committee: COMMITTEES.OPERATIONS,
    createdAt: new Date(Date.now() - 5 * 60000), // 5 minutes ago
    description: 'All ESP financial documents processed successfully',
    icon: Home
  },
  {
    id: 2,
    type: ALERT_TYPES.INFO,
    propertyName: 'Empire State Plaza',
    metric: 'Occupancy Rate',
    currentValue: 95,
    threshold: 85,
    unit: '%',
    direction: 'above',
    committee: COMMITTEES.ASSET_MANAGEMENT,
    createdAt: new Date(Date.now() - 12 * 60000), // 12 minutes ago
    description: 'Excellent occupancy rate maintained',
    icon: TrendingUp
  },
  {
    id: 3,
    type: ALERT_TYPES.INFO,
    propertyName: 'Empire State Plaza',
    metric: 'NOI',
    currentValue: 2726029.62,
    threshold: 2000000,
    unit: '$',
    direction: 'above',
    committee: COMMITTEES.FINANCE,
    createdAt: new Date(Date.now() - 25 * 60000), // 25 minutes ago
    description: 'Net operating income exceeding targets',
    icon: DollarSign
  },
  {
    id: 4,
    type: ALERT_TYPES.INFO,
    propertyName: 'Empire State Plaza',
    metric: 'DSCR',
    currentValue: 1.5,
    threshold: 1.2,
    unit: 'x',
    direction: 'above',
    committee: COMMITTEES.FINANCE,
    createdAt: new Date(Date.now() - 45 * 60000), // 45 minutes ago
    description: 'Debt service coverage ratio healthy',
    icon: TrendingUp
  },
  {
    id: 5,
    type: ALERT_TYPES.INFO,
    propertyName: 'Industrial Park A',
    metric: 'New Lease Signed',
    currentValue: 5,
    threshold: 3,
    unit: 'units',
    direction: 'above',
    committee: COMMITTEES.EXECUTIVE,
    createdAt: new Date(Date.now() - 60 * 60000), // 1 hour ago
    description: 'Multiple new leases signed this month',
    icon: Users
  },
  {
    id: 6,
    type: ALERT_TYPES.INFO,
    propertyName: 'Retail Hub B',
    metric: 'Tenant Satisfaction',
    currentValue: 4.7,
    threshold: 4.0,
    unit: '/5',
    direction: 'above',
    committee: COMMITTEES.OPERATIONS,
    createdAt: new Date(Date.now() - 90 * 60000), // 1.5 hours ago
    description: 'Tenant satisfaction survey results excellent',
    icon: CheckCircle
  }
]

// Sound notification function
const playNotificationSound = (type) => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    // Different frequencies for different alert types
    const frequencies = {
      critical: [800, 1000, 800], // Urgent beeps
      warning: [600, 700], // Medium beeps
      info: [400] // Gentle beep
    }

    const freq = frequencies[type] || frequencies.info
    let currentFreq = 0

    oscillator.frequency.value = freq[currentFreq]
    oscillator.type = 'sine'
    gainNode.gain.value = 0.3

    oscillator.start()
    
    // Play multiple tones for critical
    if (type === ALERT_TYPES.CRITICAL) {
      setTimeout(() => {
        oscillator.frequency.value = freq[1]
      }, 100)
      setTimeout(() => {
        oscillator.frequency.value = freq[2]
      }, 200)
      setTimeout(() => {
        oscillator.stop()
      }, 300)
    } else if (type === ALERT_TYPES.WARNING) {
      setTimeout(() => {
        oscillator.frequency.value = freq[1]
      }, 150)
      setTimeout(() => {
        oscillator.stop()
      }, 300)
    } else {
      setTimeout(() => {
        oscillator.stop()
      }, 200)
    }
  } catch (error) {
    console.warn('Sound notification not supported:', error)
  }
}

// Time ago formatter
const formatTimeAgo = (date) => {
  const seconds = Math.floor((new Date() - date) / 1000)
  
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

// Alert Card Component
function AlertCard({ alert, onApprove, onReject, onDismiss }) {
  const Icon = alert.icon
  
  const getAlertConfig = () => {
    switch (alert.type) {
      case ALERT_TYPES.CRITICAL:
        return {
          bgColor: 'bg-gradient-to-r from-red-50 to-orange-50',
          borderColor: 'border-red-500',
          iconBg: 'bg-red-500',
          iconColor: 'text-white',
          textColor: 'text-red-900',
          accentColor: 'text-red-600',
          buttonHover: 'hover:bg-red-600'
        }
      case ALERT_TYPES.WARNING:
        return {
          bgColor: 'bg-gradient-to-r from-yellow-50 to-amber-50',
          borderColor: 'border-yellow-500',
          iconBg: 'bg-yellow-500',
          iconColor: 'text-white',
          textColor: 'text-yellow-900',
          accentColor: 'text-yellow-600',
          buttonHover: 'hover:bg-yellow-600'
        }
      case ALERT_TYPES.INFO:
        return {
          bgColor: 'bg-gradient-to-r from-blue-50 to-cyan-50',
          borderColor: 'border-blue-500',
          iconBg: 'bg-blue-500',
          iconColor: 'text-white',
          textColor: 'text-blue-900',
          accentColor: 'text-blue-600',
          buttonHover: 'hover:bg-blue-600'
        }
    }
  }

  const config = getAlertConfig()

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -100, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.9 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`
        ${config.bgColor} ${config.borderColor}
        border-l-4 rounded-xl p-6 shadow-lg
        hover:shadow-xl transition-all duration-300
        relative overflow-hidden
      `}
    >
      {/* Animated background for critical alerts */}
      {alert.type === ALERT_TYPES.CRITICAL && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent"
          animate={{ opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div className={`${config.iconBg} p-3 rounded-lg ${config.iconColor} flex-shrink-0`}>
              <Icon className="w-6 h-6" />
            </div>

            {/* Alert Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className={`text-lg font-bold ${config.textColor}`}>
                  {alert.propertyName}
                </h3>
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${config.iconBg} ${config.iconColor}`}>
                  {alert.type.toUpperCase()}
                </span>
              </div>
              
              <p className={`text-sm font-semibold ${config.accentColor}`}>
                {alert.metric} Alert
              </p>
              
              <p className="text-sm text-gray-600 mt-1">
                {alert.description}
              </p>
            </div>
          </div>

          {/* Dismiss Button */}
          <button
            onClick={() => onDismiss(alert.id)}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metrics */}
        <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 mb-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1 font-semibold">Current Value</p>
              <p className={`text-lg font-bold ${config.accentColor}`}>
                {alert.unit === '$' ? '$' : ''}{alert.currentValue.toLocaleString()}{alert.unit !== '$' ? alert.unit : ''}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1 font-semibold">Threshold</p>
              <p className="text-lg font-bold text-gray-700">
                {alert.unit === '$' ? '$' : ''}{alert.threshold.toLocaleString()}{alert.unit !== '$' ? alert.unit : ''}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1 font-semibold">Variance</p>
              <p className={`text-lg font-bold ${
                alert.direction === 'below' ? 'text-red-600' : 'text-green-600'
              }`}>
                {alert.direction === 'below' ? '↓' : '↑'} {Math.abs(alert.currentValue - alert.threshold).toFixed(1)}{alert.unit !== '$' ? alert.unit : ''}
              </p>
            </div>
          </div>
        </div>

        {/* Committee & Time */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="w-4 h-4" />
            <span className="font-semibold">{alert.committee}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>{formatTimeAgo(alert.createdAt)}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => onApprove(alert.id)}
            className={`
              flex-1 flex items-center justify-center gap-2
              bg-green-500 text-white px-4 py-2.5 rounded-lg
              font-semibold text-sm
              hover:bg-green-600 active:scale-95
              transition-all duration-200
              shadow-md hover:shadow-lg
            `}
          >
            <CheckCircle className="w-4 h-4" />
            Approve Action
          </button>
          <button
            onClick={() => onReject(alert.id)}
            className={`
              flex-1 flex items-center justify-center gap-2
              bg-gray-500 text-white px-4 py-2.5 rounded-lg
              font-semibold text-sm
              hover:bg-gray-600 active:scale-95
              transition-all duration-200
              shadow-md hover:shadow-lg
            `}
          >
            <XCircle className="w-4 h-4" />
            Reject Action
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// Main Alerts Center Component
export default function AlertsCenter() {
  const [alerts, setAlerts] = useState(generateSampleAlerts())
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [filterType, setFilterType] = useState('all')
  const [showStats, setShowStats] = useState(true)
  const prevAlertsCount = useRef(alerts.length)

  // Play sound when new alert arrives
  useEffect(() => {
    if (alerts.length > prevAlertsCount.current && soundEnabled) {
      const newAlert = alerts[0]
      playNotificationSound(newAlert.type)
    }
    prevAlertsCount.current = alerts.length
  }, [alerts.length, soundEnabled])

  // Simulate new alerts arriving
  useEffect(() => {
    const interval = setInterval(() => {
      // 20% chance to add a new alert every 10 seconds
      if (Math.random() > 0.8) {
        const newAlert = {
          id: Date.now(),
          type: [ALERT_TYPES.CRITICAL, ALERT_TYPES.WARNING, ALERT_TYPES.INFO][Math.floor(Math.random() * 3)],
          propertyName: ['New Property', 'Test Building', 'Sample Complex'][Math.floor(Math.random() * 3)],
          metric: ['Occupancy', 'NOI', 'DSCR', 'Maintenance'][Math.floor(Math.random() * 4)],
          currentValue: Math.random() * 100,
          threshold: Math.random() * 100,
          unit: '%',
          direction: Math.random() > 0.5 ? 'above' : 'below',
          committee: Object.values(COMMITTEES)[Math.floor(Math.random() * Object.values(COMMITTEES).length)],
          createdAt: new Date(),
          description: 'New alert detected in the system',
          icon: AlertTriangle
        }
        setAlerts(prev => [newAlert, ...prev])
      }
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  const handleApprove = (alertId) => {
    setAlerts(prev => prev.filter(a => a.id !== alertId))
    // Here you would typically send approval to backend
    console.log('Approved alert:', alertId)
  }

  const handleReject = (alertId) => {
    setAlerts(prev => prev.filter(a => a.id !== alertId))
    // Here you would typically send rejection to backend
    console.log('Rejected alert:', alertId)
  }

  const handleDismiss = (alertId) => {
    setAlerts(prev => prev.filter(a => a.id !== alertId))
  }

  // Filter alerts
  const filteredAlerts = filterType === 'all' 
    ? alerts 
    : alerts.filter(a => a.type === filterType)

  // Sort by type priority (critical > warning > info) and then by time
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    const typePriority = { critical: 0, warning: 1, info: 2 }
    const priorityDiff = typePriority[a.type] - typePriority[b.type]
    if (priorityDiff !== 0) return priorityDiff
    return b.createdAt - a.createdAt
  })

  // Calculate stats
  const stats = {
    critical: alerts.filter(a => a.type === ALERT_TYPES.CRITICAL).length,
    warning: alerts.filter(a => a.type === ALERT_TYPES.WARNING).length,
    info: alerts.filter(a => a.type === ALERT_TYPES.INFO).length,
    total: alerts.length
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-black text-gray-900 mb-2 flex items-center gap-3">
                <Bell className="w-10 h-10 text-blue-600" />
                Alerts Center
              </h1>
              <p className="text-gray-600">
                Monitor and manage property portfolio alerts in real-time
              </p>
            </div>

            {/* Sound Toggle */}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg font-semibold
                transition-all duration-200
                ${soundEnabled 
                  ? 'bg-blue-500 text-white hover:bg-blue-600' 
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }
              `}
            >
              {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              {soundEnabled ? 'Sound On' : 'Sound Off'}
            </button>
          </div>

          {/* Stats */}
          {showStats && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="grid grid-cols-4 gap-4 mb-6"
            >
              <div className="bg-white rounded-xl p-4 shadow-md border-l-4 border-gray-300">
                <p className="text-sm text-gray-600 mb-1 font-semibold">Total Alerts</p>
                <p className="text-3xl font-black text-gray-900">{stats.total}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-md border-l-4 border-red-500">
                <p className="text-sm text-gray-600 mb-1 font-semibold">Critical</p>
                <p className="text-3xl font-black text-red-600">{stats.critical}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-md border-l-4 border-yellow-500">
                <p className="text-sm text-gray-600 mb-1 font-semibold">Warnings</p>
                <p className="text-3xl font-black text-yellow-600">{stats.warning}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-md border-l-4 border-blue-500">
                <p className="text-sm text-gray-600 mb-1 font-semibold">Info</p>
                <p className="text-3xl font-black text-blue-600">{stats.info}</p>
              </div>
            </motion.div>
          )}

          {/* Filters */}
          <div className="flex gap-3">
            {[
              { value: 'all', label: 'All Alerts', count: stats.total },
              { value: ALERT_TYPES.CRITICAL, label: 'Critical', count: stats.critical, color: 'red' },
              { value: ALERT_TYPES.WARNING, label: 'Warning', count: stats.warning, color: 'yellow' },
              { value: ALERT_TYPES.INFO, label: 'Info', count: stats.info, color: 'blue' }
            ].map(filter => (
              <button
                key={filter.value}
                onClick={() => setFilterType(filter.value)}
                className={`
                  px-4 py-2 rounded-lg font-semibold text-sm
                  transition-all duration-200
                  ${filterType === filter.value
                    ? filter.color === 'red' ? 'bg-red-500 text-white'
                      : filter.color === 'yellow' ? 'bg-yellow-500 text-white'
                      : filter.color === 'blue' ? 'bg-blue-500 text-white'
                      : 'bg-gray-800 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                  }
                  shadow-md hover:shadow-lg active:scale-95
                `}
              >
                {filter.label} ({filter.count})
              </button>
            ))}
          </div>
        </motion.div>

        {/* Alerts List */}
        <div className="space-y-4">
          <AnimatePresence mode="popLayout">
            {sortedAlerts.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-16"
              >
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 mb-2">All Clear!</h3>
                <p className="text-gray-600">No alerts at this time</p>
              </motion.div>
            ) : (
              sortedAlerts.map(alert => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onDismiss={handleDismiss}
                />
              ))
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}














