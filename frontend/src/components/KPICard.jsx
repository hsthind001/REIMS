import React, { useEffect, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';

/**
 * Reusable KPI Card Component
 * 
 * Displays key performance indicators with:
 * - Large metric value with animation
 * - Trend indicator (up/down with color)
 * - Color-coded gradient backgrounds
 * - Hover effects with shadow elevation
 * - Responsive layout
 * - Number formatting (currency, percentage, count)
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Card title
 * @param {number|string} props.value - Metric value
 * @param {string} [props.unit] - Unit suffix (e.g., "$", "%")
 * @param {number|null} [props.trend] - Percentage change (positive or negative)
 * @param {boolean} [props.trendUp] - Whether trend is positive (overrides auto-detection)
 * @param {React.Component} [props.icon] - Icon component to display
 * @param {'blue'|'green'|'purple'|'orange'|'red'|'indigo'} [props.color='blue'] - Card color theme
 * @param {string} [props.subtitle] - Optional subtitle text
 * @param {boolean} [props.loading] - Show loading state
 * @param {Function} [props.onClick] - Click handler (makes card clickable)
 * @param {string} [props.className] - Additional CSS classes
 */
export default function KPICard({
  title,
  value,
  unit = '',
  trend = null,
  trendUp = null,
  icon: Icon = null,
  color = 'blue',
  subtitle = null,
  loading = false,
  onClick = null,
  className = '',
}) {
  const [mounted, setMounted] = useState(false);

  // Determine if trend is positive (auto-detect if not specified)
  const isTrendPositive = trendUp !== null ? trendUp : trend >= 0;

  // Parse numeric value for animation
  const numericValue = typeof value === 'string' 
    ? parseFloat(value.replace(/[^0-9.-]/g, '')) 
    : value;

  const isValidNumber = !isNaN(numericValue);

  // Animated number using framer-motion
  const spring = useSpring(0, {
    stiffness: 80,
    damping: 30,
    duration: 1500,
  });

  const displayValue = useTransform(spring, (current) => {
    if (!isValidNumber) return value;
    return formatNumber(current, unit);
  });

  useEffect(() => {
    setMounted(true);
    if (isValidNumber) {
      spring.set(numericValue);
    }
  }, [numericValue, spring, isValidNumber]);

  // Color configurations
  const colorConfig = {
    blue: {
      gradient: 'from-blue-500 to-blue-600',
      light: 'from-blue-50 to-blue-100',
      text: 'text-blue-600',
      iconBg: 'bg-blue-100',
      border: 'border-blue-200',
      hover: 'hover:from-blue-600 hover:to-blue-700',
    },
    green: {
      gradient: 'from-green-500 to-emerald-600',
      light: 'from-green-50 to-emerald-100',
      text: 'text-green-600',
      iconBg: 'bg-green-100',
      border: 'border-green-200',
      hover: 'hover:from-green-600 hover:to-emerald-700',
    },
    purple: {
      gradient: 'from-purple-500 to-purple-600',
      light: 'from-purple-50 to-purple-100',
      text: 'text-purple-600',
      iconBg: 'bg-purple-100',
      border: 'border-purple-200',
      hover: 'hover:from-purple-600 hover:to-purple-700',
    },
    orange: {
      gradient: 'from-orange-500 to-orange-600',
      light: 'from-orange-50 to-orange-100',
      text: 'text-orange-600',
      iconBg: 'bg-orange-100',
      border: 'border-orange-200',
      hover: 'hover:from-orange-600 hover:to-orange-700',
    },
    red: {
      gradient: 'from-red-500 to-red-600',
      light: 'from-red-50 to-red-100',
      text: 'text-red-600',
      iconBg: 'bg-red-100',
      border: 'border-red-200',
      hover: 'hover:from-red-600 hover:to-red-700',
    },
    indigo: {
      gradient: 'from-indigo-500 to-indigo-600',
      light: 'from-indigo-50 to-indigo-100',
      text: 'text-indigo-600',
      iconBg: 'bg-indigo-100',
      border: 'border-indigo-200',
      hover: 'hover:from-indigo-600 hover:to-indigo-700',
    },
  };

  const config = colorConfig[color] || colorConfig.blue;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ 
        scale: onClick ? 1.02 : 1.01,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      }}
      className={`
        relative overflow-hidden rounded-xl
        bg-gradient-to-br ${config.light}
        border ${config.border}
        p-6
        transition-all duration-300
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {/* Background Pattern */}
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 opacity-5">
        <div className={`w-full h-full rounded-full bg-gradient-to-br ${config.gradient}`}></div>
      </div>

      {/* Icon */}
      {Icon && (
        <div className={`absolute top-4 right-4 p-2 rounded-lg ${config.iconBg}`}>
          <Icon className={`w-5 h-5 ${config.text}`} />
        </div>
      )}

      {/* Content */}
      <div className="relative">
        {/* Title */}
        <h3 className="text-sm font-medium text-gray-600 mb-2 truncate pr-12">
          {title}
        </h3>

        {/* Value */}
        {loading ? (
          <div className="space-y-2">
            <div className="h-9 bg-gray-200 rounded animate-pulse w-3/4"></div>
            {trend !== null && (
              <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
            )}
          </div>
        ) : (
          <>
            <div className="flex items-baseline gap-1 mb-2">
              <motion.span 
                className={`text-3xl font-bold ${config.text}`}
                style={{ display: 'inline-block' }}
              >
                {mounted && isValidNumber ? (
                  <motion.span>{displayValue}</motion.span>
                ) : (
                  formatNumber(value, unit)
                )}
              </motion.span>
            </div>

            {/* Trend Indicator */}
            {trend !== null && (
              <div className="flex items-center gap-1">
                <div
                  className={`
                    flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
                    ${isTrendPositive 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                    }
                  `}
                >
                  {/* Arrow Icon */}
                  {isTrendPositive ? (
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  <span>
                    {Math.abs(trend).toFixed(1)}%
                  </span>
                </div>
                {subtitle && (
                  <span className="text-xs text-gray-500">{subtitle}</span>
                )}
              </div>
            )}

            {/* Subtitle without trend */}
            {!trend && subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </>
        )}
      </div>

      {/* Click indicator */}
      {onClick && (
        <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      )}
    </motion.div>
  );
}

/**
 * Format numbers based on magnitude and unit
 */
function formatNumber(value, unit) {
  const num = typeof value === 'string' 
    ? parseFloat(value.replace(/[^0-9.-]/g, '')) 
    : value;

  if (isNaN(num)) return value;

  // Handle percentage
  if (unit === '%') {
    return `${num.toFixed(1)}%`;
  }

  // Handle currency
  if (unit === '$' || unit === 'USD') {
    if (Math.abs(num) >= 1000000) {
      return `$${(num / 1000000).toFixed(1)}M`;
    } else if (Math.abs(num) >= 1000) {
      return `$${(num / 1000).toFixed(1)}K`;
    } else {
      return `$${num.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    }
  }

  // Handle large counts
  if (Math.abs(num) >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  } else if (Math.abs(num) >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }

  // Default formatting
  return num.toLocaleString('en-US', { maximumFractionDigits: 1 });
}

/**
 * Grid layout component for KPI cards
 */
export function KPICardGrid({ children, columns = 4, className = '' }) {
  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6',
  };

  return (
    <div className={`grid ${columnClasses[columns] || columnClasses[4]} gap-4 md:gap-6 ${className}`}>
      {children}
    </div>
  );
}

/**
 * Skeleton loader for KPI card
 */
export function KPICardSkeleton({ color = 'blue' }) {
  return (
    <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 p-6">
      <div className="space-y-3 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        <div className="h-9 bg-gray-200 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
  );
}

