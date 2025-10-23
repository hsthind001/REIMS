import React, { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload,
  File,
  FileText,
  FileSpreadsheet,
  X,
  Check,
  AlertCircle,
  Loader,
  Eye,
  Trash2,
  Calendar,
  HardDrive,
  BarChart3,
  Clock,
  CheckCircle,
  XCircle,
  Download
} from 'lucide-react'

/**
 * REIMS Document Upload Center
 * 
 * Features:
 * - Drag & drop with animation
 * - PDF, Excel, CSV support
 * - File preview/thumbnail
 * - Upload progress bar
 * - Toast notifications
 * - Recent uploads list with actions
 * - Color-coded by file type
 */

// File type configurations
const FILE_TYPES = {
  pdf: {
    color: '#ef4444',
    bgColor: '#fee2e2',
    icon: FileText,
    accept: '.pdf',
    label: 'PDF'
  },
  excel: {
    color: '#10b981',
    bgColor: '#d1fae5',
    icon: FileSpreadsheet,
    accept: '.xlsx,.xls',
    label: 'Excel'
  },
  csv: {
    color: '#3b82f6',
    bgColor: '#dbeafe',
    icon: File,
    accept: '.csv',
    label: 'CSV'
  }
}

// Toast notification component
const Toast = ({ message, type, onClose }) => {
  const config = {
    success: {
      bg: 'from-green-500 to-emerald-600',
      icon: CheckCircle,
      iconColor: 'text-white'
    },
    error: {
      bg: 'from-red-500 to-rose-600',
      icon: XCircle,
      iconColor: 'text-white'
    },
    info: {
      bg: 'from-blue-500 to-cyan-600',
      icon: AlertCircle,
      iconColor: 'text-white'
    }
  }

  const { bg, icon: Icon, iconColor } = config[type] || config.info

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.9 }}
      className={`
        fixed top-4 right-4 z-50
        bg-gradient-to-r ${bg}
        text-white px-6 py-4 rounded-xl shadow-2xl
        flex items-center gap-3 max-w-md
      `}
    >
      <Icon className={`w-6 h-6 ${iconColor}`} />
      <p className="font-semibold">{message}</p>
      <button
        onClick={onClose}
        className="ml-4 hover:bg-white/20 p-1 rounded-lg transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  )
}

// Generate sample uploaded files
// NOTE: Demo/sample uploads removed - all uploads now use real backend API
// No more fake IDs - only real UUIDs from backend will be displayed

// Format file size
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Format date
const formatDate = (date) => {
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days === 1) return 'Yesterday'
  return date.toLocaleDateString()
}

// Detect document type from filename
const detectDocumentType = (fileName) => {
  const nameLower = fileName.toLowerCase()
  
  if (nameLower.includes('balance sheet') || nameLower.includes('balance-sheet')) {
    return 'balance_sheet'
  }
  if (nameLower.includes('income statement') || nameLower.includes('income-statement')) {
    return 'income_statement'
  }
  if (nameLower.includes('cash flow') || nameLower.includes('cashflow') || nameLower.includes('cash-flow')) {
    return 'cash_flow_statement'
  }
  if (nameLower.includes('rent roll') || nameLower.includes('rent-roll') || nameLower.includes('rentroll')) {
    return 'rent_roll'
  }
  
  return 'other'
}

// Main component
export default function DocumentUploadCenter() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadingFiles, setUploadingFiles] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [toasts, setToasts] = useState([])
  const fileInputRef = useRef(null)

  const showToast = useCallback((message, type = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 4000)
  }, [])

  const getFileType = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase()
    if (ext === 'pdf') return 'pdf'
    if (ext === 'xlsx' || ext === 'xls') return 'excel'
    if (ext === 'csv') return 'csv'
    return null
  }

  const handleDragEnter = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.currentTarget === e.target) {
      setIsDragging(false)
    }
  }, [])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  // Define handleFiles first so other handlers can reference it
  const handleFiles = useCallback(async (files) => {
    const validFiles = files.filter(file => {
      const type = getFileType(file.name)
      if (!type) {
        showToast(`${file.name} is not a supported format`, 'error')
        return false
      }
      return true
    })

    if (validFiles.length === 0) return

    // Upload each file to the backend
    for (const file of validFiles) {
      const type = getFileType(file.name)
      const uploadId = Date.now() + Math.random()
      
      // Add to uploading list
      setUploadingFiles(prev => [...prev, {
        id: uploadId,
        file,
        name: file.name,
        size: file.size,
        type,
        progress: 0
      }])

      try {
        // Create FormData for file upload
        const formData = new FormData()
        formData.append('file', file)
        // Auto-detect document type from filename
        const detectedType = detectDocumentType(file.name)
        formData.append('document_type', detectedType)

        // Simulate progress update
        const progressInterval = setInterval(() => {
          setUploadingFiles(prev => prev.map(f =>
            f.id === uploadId ? { ...f, progress: Math.min(f.progress + 10, 90) } : f
          ))
        }, 100)

        // Upload to backend
        const response = await fetch('http://localhost:8001/api/documents/upload', {
          method: 'POST',
          body: formData,
        })

        clearInterval(progressInterval)

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }

        const result = await response.json()
        const documentId = result.data.document_id

        // Complete progress
        setUploadingFiles(prev => prev.map(f =>
          f.id === uploadId ? { ...f, progress: 100 } : f
        ))

        // Remove from uploading list
        setTimeout(() => {
          setUploadingFiles(prev => prev.filter(f => f.id !== uploadId))
        }, 500)

        // Add to uploaded files with REAL document ID
        const newFile = {
          id: documentId, // Real UUID from backend
          name: file.name,
          size: file.size,
          type,
          uploadDate: new Date(),
          status: 'queued',
          metricsCount: 0,
          thumbnail: null
        }
        
        setUploadedFiles(prev => [newFile, ...prev])
        showToast(`${file.name} uploaded successfully!`, 'success')

        // Poll for processing status
        pollDocumentStatus(documentId, file.name)

      } catch (error) {
        console.error('Upload error:', error)
        setUploadingFiles(prev => prev.filter(f => f.id !== uploadId))
        showToast(`Failed to upload ${file.name}: ${error.message}`, 'error')
      }
    }
  }, [showToast, getFileType])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [handleFiles])

  const handleFileInput = useCallback((e) => {
    const files = Array.from(e.target.files || [])
    handleFiles(files)
  }, [handleFiles])

  // Poll document status after upload
  const pollDocumentStatus = async (documentId, fileName) => {
    let attempts = 0
    const maxAttempts = 30 // 30 seconds max

    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8001/api/documents/${documentId}/status`)
        if (!response.ok) return

        const result = await response.json()
        const status = result.data.status
        const metrics = result.data.metrics

        // Update file status
        setUploadedFiles(prev => prev.map(f =>
          f.id === documentId
            ? { 
                ...f, 
                status: status,
                metricsCount: metrics ? Object.keys(metrics).length : 0
              }
            : f
        ))

        // If processed, stop polling
        if (status === 'processed') {
          showToast(`${fileName} processed successfully!`, 'success')
          return
        }

        // If failed, stop polling
        if (status === 'failed') {
          showToast(`${fileName} processing failed`, 'error')
          return
        }

        // Continue polling if still queued or processing
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 1000) // Check every second
        }
      } catch (error) {
        console.error('Status polling error:', error)
      }
    }

    // Start polling after a short delay
    setTimeout(checkStatus, 1000)
  }

  const handleDelete = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
    showToast('File deleted successfully', 'info')
  }

  const handleView = (file) => {
    // Open the document in a new tab using the view endpoint
    const viewUrl = `http://localhost:8001/api/documents/${file.id}/view`
    window.open(viewUrl, '_blank')
    showToast(`Opening ${file.name}...`, 'info')
  }

  const handleDownload = (file) => {
    // Download the document using the download endpoint
    const downloadUrl = `http://localhost:8001/api/documents/${file.id}/download`
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showToast(`Downloading ${file.name}...`, 'info')
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '16px',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Compact Header */}
      <div>
        <h2 style={{ 
          fontSize: '20px', 
          fontWeight: '700', 
          marginBottom: '8px', 
          color: '#333',
          margin: '0 0 8px 0'
        }}>
          Document Upload Center
        </h2>
        <p style={{ 
          fontSize: '12px', 
          color: '#666', 
          marginBottom: '16px',
          margin: '0 0 16px 0'
        }}>
          Upload PDF, Excel, or CSV files to extract property data and metrics
        </p>
      </div>
      
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px',
        flex: '1',
        overflow: 'hidden'
      }}>

        {/* Drop Zone - Compact Design */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          style={{ flex: '0 0 auto' }}
        >
          <div
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              background: 'white',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: isDragging ? '0 8px 24px rgba(139, 92, 246, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
              border: isDragging ? '2px dashed #8b5cf6' : '2px dashed #e5e7eb',
              transition: 'all 0.3s',
              cursor: 'pointer',
              transform: isDragging ? 'scale(1.01)' : 'scale(1)',
            }}
            onMouseEnter={(e) => {
              if (!isDragging) {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.15)'
                e.currentTarget.style.borderColor = '#c084fc'
              }
            }}
            onMouseLeave={(e) => {
              if (!isDragging) {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)'
                e.currentTarget.style.borderColor = '#e5e7eb'
              }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.xlsx,.xls,.csv"
              onChange={handleFileInput}
              className="hidden"
            />

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
              {/* Animated Upload Icon */}
              <motion.div
                animate={isDragging ? {
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                } : {}}
                transition={{ duration: 0.5, repeat: isDragging ? Infinity : 0 }}
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: isDragging ? 'linear-gradient(135deg, #8b5cf6, #c026d3)' : 'linear-gradient(135deg, #a78bfa, #c084fc)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                  boxShadow: isDragging ? '0 4px 16px rgba(139, 92, 246, 0.4)' : '0 2px 8px rgba(167, 139, 250, 0.3)',
                }}
              >
                <Upload style={{ width: '24px', height: '24px', color: 'white' }} />
              </motion.div>

              {/* Text */}
              <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#333', marginBottom: '4px' }}>
                {isDragging ? '📥 Drop files here!' : '📤 Drag & drop files here'}
              </h3>
              <p style={{ fontSize: '12px', color: '#666', marginBottom: '16px' }}>
                or click to browse your computer
              </p>

              {/* Supported Formats - Compact */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {Object.values(FILE_TYPES).map((type) => {
                  const Icon = type.icon
                  return (
                    <div
                      key={type.label}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: type.bgColor,
                        border: `1px solid ${type.color}30`,
                        transition: 'all 0.3s',
                      }}
                    >
                      <Icon style={{ width: '16px', height: '16px', color: type.color }} />
                      <span style={{ fontWeight: '600', fontSize: '12px', color: type.color }}>
                        {type.label}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Uploading Files - Compact */}
        <AnimatePresence>
          {uploadingFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              style={{ flex: '0 0 auto' }}
            >
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>⏳ Uploading...</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {uploadingFiles.map((file) => {
                const typeConfig = FILE_TYPES[file.type]
                const Icon = typeConfig.icon
                
                return (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    style={{
                      background: 'white',
                      borderRadius: '8px',
                      padding: '12px',
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                      borderLeft: `3px solid ${typeConfig.color}`,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                      <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: typeConfig.bgColor }}>
                        <Icon style={{ width: '16px', height: '16px', color: typeConfig.color }} />
                      </div>
                      <div style={{ flex: '1' }}>
                        <h3 style={{ fontWeight: '700', fontSize: '12px', color: '#111827', margin: '0 0 2px 0' }}>{file.name}</h3>
                        <p style={{ fontSize: '10px', color: '#6b7280', margin: '0' }}>{formatFileSize(file.size)}</p>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <p style={{ fontSize: '16px', fontWeight: '900', color: typeConfig.color, margin: '0' }}>
                          {Math.round(file.progress)}%
                        </p>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div style={{ width: '100%', background: '#e5e7eb', borderRadius: '4px', height: '4px', overflow: 'hidden' }}>
                      <motion.div
                        style={{ 
                          height: '100%', 
                          borderRadius: '4px',
                          backgroundColor: typeConfig.color 
                        }}
                        initial={{ width: 0 }}
                        animate={{ width: `${file.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </motion.div>
                )
              })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recent Uploads - Scrollable */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ flex: '1', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
        >
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#333', marginBottom: '8px', flex: '0 0 auto' }}>📄 Recent Uploads</h3>
          
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '8px',
            flex: '1',
            overflow: 'auto',
            paddingRight: '4px'
          }}>
            <AnimatePresence>
              {uploadedFiles.map((file) => {
                const typeConfig = FILE_TYPES[file.type]
                const Icon = typeConfig.icon
                
                const statusConfig = {
                  processed: {
                    bg: 'bg-green-100',
                    text: 'text-green-700',
                    icon: CheckCircle,
                    label: 'Processed'
                  },
                  queued: {
                    bg: 'bg-blue-100',
                    text: 'text-blue-700',
                    icon: Clock,
                    label: 'Queued'
                  },
                  processing: {
                    bg: 'bg-yellow-100',
                    text: 'text-yellow-700',
                    icon: Loader,
                    label: 'Processing...'
                  },
                  pending: {
                    bg: 'bg-yellow-100',
                    text: 'text-yellow-700',
                    icon: Clock,
                    label: 'Processing...'
                  },
                  failed: {
                    bg: 'bg-red-100',
                    text: 'text-red-700',
                    icon: XCircle,
                    label: 'Failed'
                  }
                }
                
                const status = statusConfig[file.status] || statusConfig['pending'] // Fallback to pending
                const StatusIcon = status?.icon || Clock
                
                return (
                  <motion.div
                    key={file.id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    style={{
                      background: 'white',
                      borderRadius: '8px',
                      padding: '12px',
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                      borderLeft: `3px solid ${typeConfig.color}`,
                      transition: 'all 0.3s',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)'
                      e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                      {/* File Icon */}
                      <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: typeConfig.bgColor }}>
                        <Icon style={{ width: '16px', height: '16px', color: typeConfig.color }} />
                      </div>
                      
                      {/* File Info */}
                      <div style={{ flex: '1' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <div>
                            <h3 style={{ fontSize: '12px', fontWeight: '700', color: '#111827', margin: '0 0 4px 0' }}>{file.name}</h3>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '10px', color: '#6b7280' }}>
                              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <HardDrive style={{ width: '12px', height: '12px' }} />
                                {formatFileSize(file.size)}
                              </span>
                              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Calendar style={{ width: '12px', height: '12px' }} />
                                {formatDate(file.uploadDate)}
                              </span>
                            </div>
                          </div>
                          
                          {/* Status Badge */}
                          <div style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: '4px', 
                            padding: '2px 6px', 
                            borderRadius: '12px',
                            background: status.bg.replace('bg-', '#').replace('-100', '20'),
                            color: status.text.replace('text-', '#').replace('-700', '')
                          }}>
                            <StatusIcon style={{ width: '12px', height: '12px' }} />
                            <span style={{ fontSize: '10px', fontWeight: '600' }}>
                              {status.label}
                            </span>
                          </div>
                        </div>
                        
                        {/* Metrics */}
                        {file.status === 'processed' && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' }}>
                            <BarChart3 style={{ width: '12px', height: '12px', color: '#9333ea' }} />
                            <span style={{ fontSize: '10px', fontWeight: '600', color: '#9333ea' }}>
                              {file.metricsCount} metrics extracted
                            </span>
                          </div>
                        )}
                        
                        {/* Actions */}
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button
                            onClick={() => handleView(file)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '4px 8px',
                              background: '#3b82f6',
                              color: 'white',
                              borderRadius: '4px',
                              fontSize: '10px',
                              fontWeight: '600',
                              border: 'none',
                              cursor: 'pointer',
                              transition: 'background 0.3s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#2563eb'}
                            onMouseLeave={(e) => e.currentTarget.style.background = '#3b82f6'}
                          >
                            <Eye style={{ width: '12px', height: '12px' }} />
                            View
                          </button>
                          <button
                            onClick={() => handleDelete(file.id)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '4px 8px',
                              background: '#ef4444',
                              color: 'white',
                              borderRadius: '4px',
                              fontSize: '10px',
                              fontWeight: '600',
                              border: 'none',
                              cursor: 'pointer',
                              transition: 'background 0.3s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#dc2626'}
                            onMouseLeave={(e) => e.currentTarget.style.background = '#ef4444'}
                          >
                            <Trash2 style={{ width: '12px', height: '12px' }} />
                            Delete
                          </button>
                          {file.status === 'processed' && (
                            <button
                              onClick={() => handleDownload(file)}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                padding: '4px 8px',
                                background: '#6b7280',
                                color: 'white',
                                borderRadius: '4px',
                                fontSize: '10px',
                                fontWeight: '600',
                                border: 'none',
                                cursor: 'pointer',
                                transition: 'background 0.3s'
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.background = '#4b5563'}
                              onMouseLeave={(e) => e.currentTarget.style.background = '#6b7280'}
                            >
                              <Download style={{ width: '12px', height: '12px' }} />
                              Download
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Toast Notifications */}
        <AnimatePresence>
          {toasts.map(toast => (
            <Toast
              key={toast.id}
              message={toast.message}
              type={toast.type}
              onClose={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}



