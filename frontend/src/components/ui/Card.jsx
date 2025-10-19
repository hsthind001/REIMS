import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

/**
 * REIMS Card Component
 * Beautiful card with shadow, hover effects, and gradient options
 */

export function Card({ 
  children, 
  className,
  variant = 'default',
  gradient = false,
  hoverable = true,
  ...props 
}) {
  const variants = {
    default: 'bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary',
    blue: 'bg-gradient-to-br from-brand-blue-50 to-brand-teal-50 border border-brand-blue-200',
    purple: 'bg-gradient-to-br from-accent-purple-50 to-accent-indigo-50 border border-accent-purple-200',
    success: 'bg-gradient-to-br from-status-success-50 to-growth-emerald-50 border border-status-success-200',
    warning: 'bg-gradient-to-br from-status-warning-50 to-growth-lime-50 border border-status-warning-200',
    glass: 'bg-white/80 dark:bg-dark-bg-secondary/80 backdrop-blur-xl border border-white/20',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={hoverable ? { y: -4, transition: { duration: 0.2 } } : {}}
      className={cn(
        'rounded-xl shadow-lg',
        hoverable && 'hover:shadow-2xl transition-all duration-300 cursor-pointer',
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export function CardHeader({ children, className, ...props }) {
  return (
    <div className={cn('p-6 border-b border-neutral-slate-100 dark:border-dark-border-subtle', className)} {...props}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className, ...props }) {
  return (
    <h3 className={cn('text-2xl font-bold text-neutral-slate-900 dark:text-dark-text-primary', className)} {...props}>
      {children}
    </h3>
  )
}

export function CardDescription({ children, className, ...props }) {
  return (
    <p className={cn('text-sm text-neutral-slate-600 dark:text-dark-text-secondary mt-1', className)} {...props}>
      {children}
    </p>
  )
}

export function CardContent({ children, className, ...props }) {
  return (
    <div className={cn('p-6', className)} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({ children, className, ...props }) {
  return (
    <div className={cn('p-6 border-t border-neutral-slate-100 dark:border-dark-border-subtle', className)} {...props}>
      {children}
    </div>
  )
}

/**
 * Gradient Card - Premium look for special features
 */
export function GradientCard({ children, className, gradient = 'brand', ...props }) {
  const gradients = {
    brand: 'bg-gradient-to-br from-brand-blue-500 to-brand-teal-500',
    ai: 'bg-gradient-to-br from-accent-purple-500 to-accent-indigo-600',
    success: 'bg-gradient-to-br from-growth-emerald-500 to-growth-lime-500',
    premium: 'bg-gradient-to-br from-accent-indigo-600 via-accent-purple-600 to-accent-purple-700',
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={cn(
        'rounded-xl shadow-2xl text-white overflow-hidden',
        'hover:shadow-3xl transition-all duration-300',
        gradients[gradient],
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}

















