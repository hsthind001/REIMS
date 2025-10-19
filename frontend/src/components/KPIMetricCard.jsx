import { useState, useEffect, useRef } from 'react'
import { motion, useInView, useMotionValue, useSpring } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { cn } from '@/lib/utils'

/**
 * REIMS KPI Metric Card
 * 
 * Features:
 * - Large animated numbers with color coding
 * - Trend indicators (up/down with percentage)
 * - Sparkline chart (30-day history)
 * - Hover tooltip with details
 * - Background gradients specific to metric type
 * - Count-up animation on load
 */

export default function KPIMetricCard({
  title,
  value,
  formattedValue,
  trend = 'up',
  trendValue = '+0%',
  sparklineData = [],
  icon: Icon,
  type = 'default', // 'portfolio', 'properties', 'income', 'occupancy', 'default'
  subtitle,
  details = {},
  className,
  ...props
}) {
  const [isHovered, setIsHovered] = useState(false)
  const cardRef = useRef(null)
  const isInView = useInView(cardRef, { once: true })

  // Configuration for different metric types
  const typeConfig = {
    portfolio: {
      gradient: 'from-brand-blue-500 via-accent-indigo-500 to-accent-purple-500',
      accentColor: 'rgb(37, 99, 235)', // brand-blue-500
      sparklineColor: '#2563EB',
      glowColor: 'rgba(37, 99, 235, 0.4)',
    },
    properties: {
      gradient: 'from-brand-teal-500 via-accent-cyan-500 to-brand-blue-400',
      accentColor: 'rgb(44, 154, 139)', // brand-teal-500
      sparklineColor: '#2C9A8B',
      glowColor: 'rgba(44, 154, 139, 0.4)',
    },
    income: {
      gradient: 'from-growth-emerald-500 via-growth-lime-500 to-growth-emerald-400',
      accentColor: 'rgb(16, 185, 129)', // growth-emerald-500
      sparklineColor: '#10B981',
      glowColor: 'rgba(16, 185, 129, 0.4)',
    },
    occupancy: {
      gradient: 'from-accent-purple-500 via-accent-indigo-500 to-brand-blue-500',
      accentColor: 'rgb(128, 90, 213)', // accent-purple-500
      sparklineColor: '#805AD5',
      glowColor: 'rgba(128, 90, 213, 0.4)',
    },
    default: {
      gradient: 'from-neutral-slate-400 via-neutral-slate-500 to-neutral-slate-600',
      accentColor: 'rgb(100, 116, 139)', // neutral-slate-500
      sparklineColor: '#64748B',
      glowColor: 'rgba(100, 116, 139, 0.4)',
    },
  }

  const config = typeConfig[type] || typeConfig.default

  // Trend configuration
  const trendConfig = {
    up: {
      icon: TrendingUp,
      color: 'text-growth-emerald-600 dark:text-growth-emerald-400',
      bg: 'bg-growth-emerald-100 dark:bg-growth-emerald-900/30',
      iconColor: 'text-growth-emerald-600',
    },
    down: {
      icon: TrendingDown,
      color: 'text-status-error-600 dark:text-status-error-400',
      bg: 'bg-status-error-100 dark:bg-status-error-900/30',
      iconColor: 'text-status-error-600',
    },
    neutral: {
      icon: Minus,
      color: 'text-neutral-slate-600 dark:text-neutral-slate-400',
      bg: 'bg-neutral-slate-100 dark:bg-neutral-slate-900/30',
      iconColor: 'text-neutral-slate-600',
    },
  }

  const trendData = trendConfig[trend]
  const TrendIcon = trendData.icon

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -8, transition: { duration: 0.3 } }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={cn(
        'relative overflow-hidden rounded-2xl',
        'bg-white dark:bg-dark-bg-secondary',
        'border border-neutral-slate-200 dark:border-dark-border-primary',
        'shadow-lg hover:shadow-2xl',
        'transition-all duration-300',
        'cursor-pointer group',
        className
      )}
      {...props}
    >
      {/* Background Gradient */}
      <div className={cn(
        'absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500',
        `bg-gradient-to-br ${config.gradient}`
      )} />

      {/* Animated Glow Effect */}
      <motion.div
        className="absolute -top-24 -right-24 w-48 h-48 rounded-full blur-3xl"
        style={{ backgroundColor: config.glowColor }}
        animate={{
          scale: isHovered ? [1, 1.2, 1] : 1,
          opacity: isHovered ? [0.3, 0.5, 0.3] : 0.2,
        }}
        transition={{ duration: 2, repeat: Infinity }}
      />

      {/* Content */}
      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className="text-sm font-semibold uppercase tracking-wider text-neutral-slate-600 dark:text-dark-text-secondary mb-1">
              {title}
            </p>
            {subtitle && (
              <p className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary">
                {subtitle}
              </p>
            )}
          </div>
          
          {Icon && (
            <motion.div
              className="p-3 rounded-xl"
              style={{ backgroundColor: `${config.accentColor}15` }}
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.6 }}
            >
              <Icon className="w-6 h-6" style={{ color: config.accentColor }} />
            </motion.div>
          )}
        </div>

        {/* Main Value with Count-up Animation */}
        <div className="mb-4">
          <AnimatedNumber
            value={value}
            formattedValue={formattedValue}
            isInView={isInView}
            color={config.accentColor}
          />
        </div>

        {/* Trend Indicator */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className={cn(
              'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold',
              trendData.bg,
              trendData.color
            )}>
              <TrendIcon className="w-3.5 h-3.5" />
              <span>{trendValue}</span>
            </span>
            <span className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
              vs last month
            </span>
          </div>
        </div>

        {/* Sparkline Chart */}
        {sparklineData.length > 0 && (
          <div className="h-16 -mx-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData}>
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={config.sparklineColor}
                  strokeWidth={2}
                  dot={false}
                  animationDuration={1500}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Hover Tooltip */}
      <AnimatePresence>
        {isHovered && Object.keys(details).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'absolute inset-x-0 bottom-0 p-4',
              'bg-white/95 dark:bg-dark-bg-tertiary/95 backdrop-blur-xl',
              'border-t border-neutral-slate-200 dark:border-dark-border-primary'
            )}
          >
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-neutral-slate-900 dark:text-dark-text-primary uppercase tracking-wider">
                Details
              </h4>
              {Object.entries(details).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between text-xs">
                  <span className="text-neutral-slate-600 dark:text-dark-text-secondary">
                    {key}
                  </span>
                  <span className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    {val}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Border Glow on Hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: isHovered ? `0 0 30px ${config.glowColor}` : 'none',
        }}
        animate={{
          opacity: isHovered ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  )
}

/**
 * Animated Number Component
 * Counts up from 0 to target value
 */
function AnimatedNumber({ value, formattedValue, isInView, color }) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    if (!isInView) return

    // Extract numeric value from formatted string
    const numericValue = typeof value === 'number' 
      ? value 
      : parseFloat(value.toString().replace(/[^0-9.]/g, ''))

    if (isNaN(numericValue)) {
      setDisplayValue(value)
      return
    }

    // Animate counting up
    const duration = 2000 // 2 seconds
    const steps = 60
    const increment = numericValue / steps
    let current = 0
    let step = 0

    const timer = setInterval(() => {
      step++
      current += increment
      
      if (step >= steps) {
        setDisplayValue(numericValue)
        clearInterval(timer)
      } else {
        setDisplayValue(current)
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value, isInView])

  // Format the display value
  const formatDisplayValue = () => {
    if (typeof displayValue !== 'number') return displayValue

    const numValue = Math.round(displayValue * 100) / 100

    // Check if original format has special characters
    if (formattedValue) {
      if (formattedValue.includes('$')) {
        // Format as currency
        if (numValue >= 1000000) {
          return `$${(numValue / 1000000).toFixed(1)}M`
        } else if (numValue >= 1000) {
          return `$${(numValue / 1000).toFixed(1)}K`
        }
        return `$${numValue.toFixed(0)}`
      } else if (formattedValue.includes('%')) {
        // Format as percentage
        return `${numValue.toFixed(1)}%`
      }
    }

    // Default: format with commas
    return numValue.toLocaleString('en-US', { maximumFractionDigits: 0 })
  }

  return (
    <motion.div
      initial={{ scale: 0.5, opacity: 0 }}
      animate={isInView ? { scale: 1, opacity: 1 } : {}}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="text-4xl font-black"
      style={{ color }}
    >
      {formatDisplayValue()}
    </motion.div>
  )
}

/**
 * Generate sample sparkline data for 30 days
 */
export function generateSparklineData(baseValue, variance = 0.1, days = 30) {
  const data = []
  let current = baseValue * (1 - variance)
  
  for (let i = 0; i < days; i++) {
    // Random walk with slight upward trend
    const change = (Math.random() - 0.45) * (baseValue * variance * 0.1)
    current = Math.max(baseValue * (1 - variance), Math.min(baseValue * (1 + variance), current + change))
    
    data.push({
      day: i + 1,
      value: current,
    })
  }
  
  return data
}

















