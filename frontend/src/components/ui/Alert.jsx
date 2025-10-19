import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Info, 
  X,
  AlertCircle 
} from 'lucide-react'

/**
 * REIMS Alert Component
 * Beautiful alerts with icons, animations, and dismissible option
 */

export function Alert({
  variant = 'info',
  title,
  children,
  dismissible = false,
  onDismiss,
  icon: CustomIcon,
  className,
  ...props
}) {
  const variants = {
    success: {
      container: 'bg-status-success-50 border-status-success-500 dark:bg-status-success-900/20',
      icon: 'text-status-success-600 dark:text-status-success-400',
      iconBg: 'bg-status-success-100 dark:bg-status-success-900/40',
      title: 'text-status-success-900 dark:text-status-success-300',
      description: 'text-status-success-800 dark:text-status-success-400',
      defaultIcon: CheckCircle2,
    },
    warning: {
      container: 'bg-status-warning-50 border-status-warning-500 dark:bg-status-warning-900/20',
      icon: 'text-status-warning-600 dark:text-status-warning-400',
      iconBg: 'bg-status-warning-100 dark:bg-status-warning-900/40',
      title: 'text-status-warning-900 dark:text-status-warning-300',
      description: 'text-status-warning-800 dark:text-status-warning-400',
      defaultIcon: AlertTriangle,
    },
    error: {
      container: 'bg-status-error-50 border-status-error-500 dark:bg-status-error-900/20',
      icon: 'text-status-error-600 dark:text-status-error-400',
      iconBg: 'bg-status-error-100 dark:bg-status-error-900/40',
      title: 'text-status-error-900 dark:text-status-error-300',
      description: 'text-status-error-800 dark:text-status-error-400',
      defaultIcon: XCircle,
    },
    info: {
      container: 'bg-status-info-50 border-status-info-500 dark:bg-status-info-900/20',
      icon: 'text-status-info-600 dark:text-status-info-400',
      iconBg: 'bg-status-info-100 dark:bg-status-info-900/40',
      title: 'text-status-info-900 dark:text-status-info-300',
      description: 'text-status-info-800 dark:text-status-info-400',
      defaultIcon: Info,
    },
    critical: {
      container: 'bg-gradient-to-r from-status-error-500 to-status-error-600 text-white border-0',
      icon: 'text-white',
      iconBg: 'bg-white/20',
      title: 'text-white',
      description: 'text-white/90',
      defaultIcon: AlertCircle,
    },
  }

  const config = variants[variant]
  const Icon = CustomIcon || config.defaultIcon

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'rounded-xl border-l-4 p-4 shadow-lg',
        config.container,
        className
      )}
      {...props}
    >
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className={cn(
          'flex-shrink-0 p-2 rounded-lg',
          config.iconBg
        )}>
          <Icon className={cn('w-5 h-5', config.icon)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className={cn('text-sm font-bold mb-1', config.title)}>
              {title}
            </h4>
          )}
          <div className={cn('text-sm', config.description)}>
            {children}
          </div>
        </div>

        {/* Dismiss button */}
        {dismissible && (
          <button
            onClick={onDismiss}
            className={cn(
              'flex-shrink-0 p-1 rounded-lg hover:bg-black/10 transition-colors',
              config.icon
            )}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  )
}

/**
 * Alert Container for managing multiple alerts
 */
export function AlertContainer({ alerts, onDismiss, className }) {
  return (
    <div className={cn('fixed top-4 right-4 z-50 space-y-3 max-w-md', className)}>
      <AnimatePresence>
        {alerts.map((alert) => (
          <Alert
            key={alert.id}
            variant={alert.variant}
            title={alert.title}
            dismissible={alert.dismissible}
            onDismiss={() => onDismiss(alert.id)}
          >
            {alert.message}
          </Alert>
        ))}
      </AnimatePresence>
    </div>
  )
}

/**
 * Inline Alert - For forms and content sections
 */
export function InlineAlert({ variant = 'info', children, className }) {
  const config = {
    success: 'bg-status-success-100 text-status-success-800 border-status-success-300',
    warning: 'bg-status-warning-100 text-status-warning-800 border-status-warning-300',
    error: 'bg-status-error-100 text-status-error-800 border-status-error-300',
    info: 'bg-status-info-100 text-status-info-800 border-status-info-300',
  }

  return (
    <div className={cn(
      'text-sm px-4 py-2 rounded-lg border',
      config[variant],
      className
    )}>
      {children}
    </div>
  )
}

















