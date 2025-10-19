import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  CheckCircle,
  Loader,
  XCircle,
  HardDrive,
  Clock,
  TrendingUp,
  Activity,
  Database,
  Zap
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

/**
 * REIMS Processing Status Dashboard
 * 
 * Features:
 * - Total documents (animated counter)
 * - Processed count with checkmark
 * - In-progress with spinner
 * - Failed with error icon
 * - Storage usage pie chart
 * - Timeline view of recent events
 */

// Animated Number Component
const AnimatedCounter = ({ value, duration = 1500, prefix = '', suffix = '' }) => {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime = null
    let animationFrame = null

    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      
      const easeOut = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(value * easeOut))

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])

  return (
    <span>
      {prefix}{count.toLocaleString()}{suffix}
    </span>
  )
}

// Generate sample timeline events
const generateTimelineEvents = () => [
  {
    id: 1,
    type: 'success',
    document: 'Financial_Report_Q4.pdf',
    action: 'Successfully processed',
    timestamp: new Date(Date.now() - 5 * 60000), // 5 mins ago
    metricsExtracted: 24
  },
  {
    id: 2,
    type: 'success',
    document: 'Property_Data.xlsx',
    action: 'Successfully processed',
    timestamp: new Date(Date.now() - 15 * 60000), // 15 mins ago
    metricsExtracted: 42
  },
  {
    id: 3,
    type: 'processing',
    document: 'Maintenance_Report.pdf',
    action: 'Processing started',
    timestamp: new Date(Date.now() - 2 * 60000), // 2 mins ago
    metricsExtracted: 0
  },
  {
    id: 4,
    type: 'failed',
    document: 'Tenant_Complaints.csv',
    action: 'Processing failed',
    timestamp: new Date(Date.now() - 30 * 60000), // 30 mins ago
    error: 'Invalid file format'
  },
  {
    id: 5,
    type: 'success',
    document: 'Occupancy_Rates.csv',
    action: 'Successfully processed',
    timestamp: new Date(Date.now() - 45 * 60000), // 45 mins ago
    metricsExtracted: 18
  },
  {
    id: 6,
    type: 'success',
    document: 'Budget_Analysis.xlsx',
    action: 'Successfully processed',
    timestamp: new Date(Date.now() - 60 * 60000), // 1 hour ago
    metricsExtracted: 35
  }
]

// Format timestamp
const formatTimestamp = (date) => {
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return date.toLocaleDateString()
}

// Timeline Event Component
const TimelineEvent = ({ event }) => {
  const config = {
    success: {
      icon: CheckCircle,
      iconColor: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      dotColor: 'bg-green-500'
    },
    processing: {
      icon: Loader,
      iconColor: 'text-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      dotColor: 'bg-blue-500'
    },
    failed: {
      icon: XCircle,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      dotColor: 'bg-red-500'
    }
  }

  const { icon: Icon, iconColor, bgColor, borderColor, dotColor } = config[event.type]

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="relative pl-8"
    >
      {/* Timeline dot */}
      <div className={`absolute left-0 top-2 w-3 h-3 rounded-full ${dotColor} ring-4 ring-white`} />
      
      {/* Timeline line */}
      <div className="absolute left-[5px] top-5 bottom-0 w-0.5 bg-gray-200" />

      {/* Event card */}
      <div className={`mb-6 p-4 rounded-lg border-2 ${borderColor} ${bgColor}`}>
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg bg-white`}>
            <Icon className={`w-5 h-5 ${iconColor} ${event.type === 'processing' ? 'animate-spin' : ''}`} />
          </div>
          
          <div className="flex-1">
            <div className="flex items-start justify-between mb-1">
              <h4 className="font-bold text-gray-900">{event.document}</h4>
              <span className="text-xs text-gray-500">{formatTimestamp(event.timestamp)}</span>
            </div>
            
            <p className="text-sm text-gray-600 mb-2">{event.action}</p>
            
            {event.metricsExtracted > 0 && (
              <div className="flex items-center gap-2 text-xs text-green-600 font-semibold">
                <Zap className="w-3 h-3" />
                <span>{event.metricsExtracted} metrics extracted</span>
              </div>
            )}
            
            {event.error && (
              <div className="text-xs text-red-600 font-semibold">
                Error: {event.error}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Main Component
export default function ProcessingStatus() {
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    inProgress: 0,
    failed: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [storageData, setStorageData] = useState([
    { name: 'Used', value: 42.3, color: '#8b5cf6' },
    { name: 'Available', value: 57.7, color: '#e9d5ff' }
  ])

  const [timelineEvents] = useState(generateTimelineEvents())

  // Fetch real document data from API
  useEffect(() => {
    const fetchDocumentStats = async () => {
      try {
        console.log('🔄 Fetching document processing stats...')
        setLoading(true)
        
        const response = await fetch('http://localhost:8001/api/documents')
        if (!response.ok) {
          throw new Error('Failed to fetch document stats')
        }
        
        const data = await response.json()
        console.log('✅ Document Data:', data)
        
        // Calculate stats from real data
        const documents = data.data?.documents || []
        const total = documents.length
        const processed = documents.filter(doc => doc.status === 'completed').length
        const inProgress = documents.filter(doc => doc.status === 'processing').length
        const failed = documents.filter(doc => doc.status === 'failed').length
        
        // Calculate property breakdown
        const propertyStats = {}
        documents.forEach(doc => {
          const propName = doc.property_name || 'Unknown Property'
          if (!propertyStats[propName]) {
            propertyStats[propName] = { total: 0, completed: 0 }
          }
          propertyStats[propName].total++
          if (doc.status === 'completed') {
            propertyStats[propName].completed++
          }
        })

        const realStats = {
          total,
          processed,
          inProgress,
          failed,
          propertyBreakdown: propertyStats
        }
        
        console.log('📊 Real Processing Stats:', realStats)
        setStats(realStats)
      } catch (err) {
        console.error('❌ Error fetching document stats:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchDocumentStats()
  }, [])

  const usedStorage = storageData[0].value
  const totalStorage = 100 // GB

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-black text-gray-900 mb-2 flex items-center gap-3">
            <Activity className="w-10 h-10 text-purple-600" />
            Processing Status Dashboard
          </h1>
          <p className="text-gray-600">
            Monitor document processing and system capacity in real-time
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Documents */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-purple-500 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Total Documents</h3>
            <p className="text-4xl font-black text-purple-600">
              <AnimatedCounter value={stats.total} />
            </p>
            <p className="text-xs text-gray-500 mt-2">All uploaded files</p>
          </motion.div>

          {/* Processed */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-green-500 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm font-semibold text-green-600">
                {((stats.processed / stats.total) * 100).toFixed(1)}%
              </span>
            </div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Processed</h3>
            <p className="text-4xl font-black text-green-600">
              <AnimatedCounter value={stats.processed} />
            </p>
            <p className="text-xs text-gray-500 mt-2">Successfully completed</p>
          </motion.div>

          {/* In Progress */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-blue-500 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Loader className="w-6 h-6 text-blue-600 animate-spin" />
              </div>
              <motion.div
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-2 h-2 bg-blue-500 rounded-full"
              />
            </div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2">In Progress</h3>
            <p className="text-4xl font-black text-blue-600">
              <AnimatedCounter value={stats.inProgress} />
            </p>
            <p className="text-xs text-gray-500 mt-2">Currently processing</p>
          </motion.div>

          {/* Failed */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-red-500 hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              {stats.failed > 0 && (
                <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full">
                  Attention
                </span>
              )}
            </div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Failed</h3>
            <p className="text-4xl font-black text-red-600">
              <AnimatedCounter value={stats.failed} />
            </p>
            <p className="text-xs text-gray-500 mt-2">Processing errors</p>
          </motion.div>
        </div>

        {/* Property Breakdown Section */}
        {stats.propertyBreakdown && Object.keys(stats.propertyBreakdown).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-6 bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-indigo-100 rounded-lg">
                <Database className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Documents by Property</h2>
                <p className="text-sm text-gray-600">Processing status breakdown</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(stats.propertyBreakdown).map(([propertyName, propertyData]) => (
                <div key={propertyName} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-900">{propertyName}</h3>
                    <span className="text-sm text-gray-600">
                      {propertyData.completed}/{propertyData.total} completed
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${(propertyData.completed / propertyData.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>Total: {propertyData.total}</span>
                    <span>Completed: {propertyData.completed}</span>
                    <span>Pending: {propertyData.total - propertyData.completed}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Storage Usage */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-purple-100 rounded-lg">
                <HardDrive className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Storage Usage</h2>
                <p className="text-sm text-gray-600">System capacity</p>
              </div>
            </div>

            {/* Pie Chart */}
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={storageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {storageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `${value.toFixed(1)} GB`}
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Storage Stats */}
            <div className="space-y-3 mt-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-600">Used</span>
                <span className="text-sm font-bold text-purple-600">
                  {usedStorage.toFixed(1)} GB
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-600">Available</span>
                <span className="text-sm font-bold text-gray-900">
                  {(totalStorage - usedStorage).toFixed(1)} GB
                </span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-gray-600">Total Capacity</span>
                  <span className="text-sm font-bold text-gray-900">{totalStorage} GB</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden mt-4">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${usedStorage}%` }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                />
              </div>
            </div>
          </motion.div>

          {/* Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="lg:col-span-2 bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Recent Processing Events</h2>
                <p className="text-sm text-gray-600">Document processing timeline</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              <div className="relative">
                <AnimatePresence>
                  {timelineEvents.map((event) => (
                    <TimelineEvent key={event.id} event={event} />
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Timeline Summary */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-black text-green-600">
                    {timelineEvents.filter(e => e.type === 'success').length}
                  </p>
                  <p className="text-xs text-gray-600 font-semibold">Successful</p>
                </div>
                <div>
                  <p className="text-2xl font-black text-blue-600">
                    {timelineEvents.filter(e => e.type === 'processing').length}
                  </p>
                  <p className="text-xs text-gray-600 font-semibold">Processing</p>
                </div>
                <div>
                  <p className="text-2xl font-black text-red-600">
                    {timelineEvents.filter(e => e.type === 'failed').length}
                  </p>
                  <p className="text-xs text-gray-600 font-semibold">Failed</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* System Health Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 shadow-lg text-white"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Database className="w-8 h-8" />
              <div>
                <h3 className="text-lg font-bold">System Health: Excellent</h3>
                <p className="text-sm text-green-100">
                  All processing services operational • {stats.processed} documents processed today
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-3 h-3 bg-white rounded-full"
              />
              <span className="font-semibold">Live</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #8b5cf6;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #7c3aed;
        }
      `}</style>
    </div>
  )
}














