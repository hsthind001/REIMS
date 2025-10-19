import { motion, AnimatePresence } from 'framer-motion'
import { createContext, useContext, useState, useCallback } from 'react'
import { cn } from '@/lib/utils'
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react'

/**
 * REIMS Toast Notification System
 * Beautiful toast notifications with animations and auto-dismiss
 */

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((toast) => {
    const id = Date.now()
    const newToast = { id, ...toast }
    
    setToasts((prev) => [...prev, newToast])

    if (toast.duration !== Infinity) {
      setTimeout(() => {
        removeToast(id)
      }, toast.duration || 5000)
    }

    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const toast = useCallback((options) => {
    if (typeof options === 'string') {
      return addToast({ variant: 'info', message: options })
    }
    return addToast(options)
  }, [addToast])

  // Convenience methods
  toast.success = useCallback((message, options = {}) => {
    return addToast({ variant: 'success', message, ...options })
  }, [addToast])

  toast.error = useCallback((message, options = {}) => {
    return addToast({ variant: 'error', message, ...options })
  }, [addToast])

  toast.warning = useCallback((message, options = {}) => {
    return addToast({ variant: 'warning', message, ...options })
  }, [addToast])

  toast.info = useCallback((message, options = {}) => {
    return addToast({ variant: 'info', message, ...options })
  }, [addToast])

  return (
    <ToastContext.Provider value={{ toast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

function ToastContainer({ toasts, removeToast }) {
  return (
    <div className="fixed top-4 right-4 z-[100] space-y-3 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

function Toast({ 
  variant = 'info', 
  title, 
  message, 
  onClose,
  action,
}) {
  const variants = {
    success: {
      container: 'bg-gradient-to-r from-growth-emerald-500 to-growth-emerald-600 text-white',
      icon: CheckCircle2,
      progressBar: 'bg-white/30',
    },
    error: {
      container: 'bg-gradient-to-r from-status-error-500 to-status-error-600 text-white',
      icon: XCircle,
      progressBar: 'bg-white/30',
    },
    warning: {
      container: 'bg-gradient-to-r from-status-warning-500 to-status-warning-600 text-white',
      icon: AlertTriangle,
      progressBar: 'bg-white/30',
    },
    info: {
      container: 'bg-gradient-to-r from-brand-blue-500 to-brand-blue-600 text-white',
      icon: Info,
      progressBar: 'bg-white/30',
    },
  }

  const config = variants[variant]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.2 } }}
      className={cn(
        'rounded-xl shadow-2xl overflow-hidden backdrop-blur-xl',
        config.container
      )}
    >
      <div className="p-4 flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 p-2 bg-white/20 rounded-lg">
          <Icon className="w-5 h-5" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="text-sm font-bold mb-1">
              {title}
            </h4>
          )}
          <p className="text-sm opacity-90">
            {message}
          </p>
          {action && (
            <button
              onClick={action.onClick}
              className="mt-2 text-sm font-semibold underline hover:no-underline"
            >
              {action.label}
            </button>
          )}
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="flex-shrink-0 p-1 hover:bg-white/20 rounded-lg transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Progress bar */}
      <motion.div
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: 5, ease: 'linear' }}
        className={cn('h-1', config.progressBar)}
      />
    </motion.div>
  )
}

/**
 * Example usage:
 * 
 * import { useToast } from '@/components/ui/Toast'
 * 
 * function MyComponent() {
 *   const { toast } = useToast()
 *   
 *   const handleSuccess = () => {
 *     toast.success('Document uploaded successfully!')
 *   }
 *   
 *   const handleError = () => {
 *     toast.error('Failed to upload document', {
 *       title: 'Upload Error',
 *       action: {
 *         label: 'Retry',
 *         onClick: () => console.log('Retry')
 *       }
 *     })
 *   }
 *   
 *   return (
 *     <button onClick={handleSuccess}>Show Toast</button>
 *   )
 * }
 */

















