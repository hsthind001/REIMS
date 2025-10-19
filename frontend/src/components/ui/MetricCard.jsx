import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

/**
 * REIMS Metric/KPI Card Component
 * Display metrics with trend indicators and beautiful animations
 */

export function MetricCard({
  title,
  value,
  change,
  trend = 'neutral', // 'up', 'down', 'neutral'
  icon: Icon,
  variant = 'default',
  subtitle,
  loading = false,
  className,
  ...props
}) {
  const variants = {
    default: 'bg-white dark:bg-dark-bg-secondary border-neutral-slate-200 dark:border-dark-border-primary',
    blue: 'bg-gradient-to-br from-brand-blue-500 to-brand-blue-600 text-white border-0',
    teal: 'bg-gradient-to-br from-brand-teal-500 to-brand-teal-600 text-white border-0',
    purple: 'bg-gradient-to-br from-accent-purple-500 to-accent-purple-600 text-white border-0',
    success: 'bg-gradient-to-br from-growth-emerald-500 to-growth-emerald-600 text-white border-0',
    warning: 'bg-gradient-to-br from-status-warning-500 to-status-warning-600 text-white border-0',
  }

  const trendConfig = {
    up: {
      icon: TrendingUp,
      color: variant.includes('gradient') || variant !== 'default' 
        ? 'text-white' 
        : 'text-growth-emerald-600',
      bg: variant.includes('gradient') || variant !== 'default'
        ? 'bg-white/20'
        : 'bg-growth-emerald-100',
    },
    down: {
      icon: TrendingDown,
      color: variant.includes('gradient') || variant !== 'default'
        ? 'text-white'
        : 'text-status-error-600',
      bg: variant.includes('gradient') || variant !== 'default'
        ? 'bg-white/20'
        : 'bg-status-error-100',
    },
    neutral: {
      icon: Minus,
      color: variant.includes('gradient') || variant !== 'default'
        ? 'text-white'
        : 'text-neutral-slate-600',
      bg: variant.includes('gradient') || variant !== 'default'
        ? 'bg-white/20'
        : 'bg-neutral-slate-100',
    },
  }

  const TrendIcon = trendConfig[trend].icon

  if (loading) {
    return (
      <div className={cn('rounded-xl border p-6 animate-pulse', variants.default, className)}>
        <div className="h-4 bg-neutral-slate-200 rounded w-1/2 mb-4"></div>
        <div className="h-8 bg-neutral-slate-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-neutral-slate-200 rounded w-1/3"></div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'rounded-xl border shadow-lg hover:shadow-2xl transition-all duration-300 p-6 relative overflow-hidden group',
        variants[variant],
        className
      )}
      {...props}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-3xl transform translate-x-16 -translate-y-16 group-hover:scale-150 transition-transform duration-500"></div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className={cn(
              'text-sm font-semibold uppercase tracking-wider mb-2',
              variant === 'default' ? 'text-neutral-slate-600 dark:text-dark-text-secondary' : 'text-white/90'
            )}>
              {title}
            </p>
          </div>
          {Icon && (
            <div className={cn(
              'p-3 rounded-xl transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3',
              variant === 'default' 
                ? 'bg-brand-blue-100 text-brand-blue-600' 
                : 'bg-white/20 text-white'
            )}>
              <Icon className="w-6 h-6" />
            </div>
          )}
        </div>

        {/* Value */}
        <div className="mb-3">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className={cn(
              'text-4xl font-black mb-1',
              variant === 'default' ? 'text-neutral-slate-900 dark:text-dark-text-primary' : 'text-white'
            )}
          >
            {value}
          </motion.div>
          {subtitle && (
            <p className={cn(
              'text-sm',
              variant === 'default' ? 'text-neutral-slate-600 dark:text-dark-text-secondary' : 'text-white/80'
            )}>
              {subtitle}
            </p>
          )}
        </div>

        {/* Trend */}
        {change && (
          <div className="flex items-center space-x-2">
            <span className={cn(
              'inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-sm font-bold',
              trendConfig[trend].bg,
              trendConfig[trend].color
            )}>
              <TrendIcon className="w-4 h-4" />
              <span>{change}</span>
            </span>
          </div>
        )}
      </div>

      {/* Animated border on hover */}
      <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-white/20 transition-colors duration-300"></div>
    </motion.div>
  )
}

/**
 * Compact Metric Card - For dashboard grids
 */
export function CompactMetricCard({ title, value, icon: Icon, color = 'blue', className }) {
  const colors = {
    blue: 'from-brand-blue-500 to-brand-blue-600',
    teal: 'from-brand-teal-500 to-brand-teal-600',
    purple: 'from-accent-purple-500 to-accent-purple-600',
    success: 'from-growth-emerald-500 to-growth-emerald-600',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={cn(
        'rounded-lg p-4 bg-gradient-to-br text-white shadow-lg hover:shadow-xl transition-shadow',
        colors[color],
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm opacity-90 mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        {Icon && <Icon className="w-8 h-8 opacity-80" />}
      </div>
    </motion.div>
  )
}

















