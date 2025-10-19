import { cn } from '@/lib/utils'

/**
 * REIMS Skeleton Loaders
 * Beautiful loading placeholders for data fetching
 */

export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-gradient-to-r from-neutral-slate-200 via-neutral-slate-300 to-neutral-slate-200',
        'dark:from-dark-bg-tertiary dark:via-neutral-slate-700 dark:to-dark-bg-tertiary',
        'bg-[length:200%_100%]',
        className
      )}
      style={{
        animation: 'shimmer 2s infinite',
      }}
      {...props}
    />
  )
}

/**
 * Card Skeleton
 */
export function SkeletonCard({ className }) {
  return (
    <div className={cn('rounded-xl border border-neutral-slate-200 dark:border-dark-border-primary p-6 space-y-4', className)}>
      <Skeleton className="h-6 w-1/3" />
      <Skeleton className="h-32 w-full" />
      <div className="flex gap-4">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  )
}

/**
 * Metric Card Skeleton
 */
export function SkeletonMetricCard({ className }) {
  return (
    <div className={cn('rounded-xl border border-neutral-slate-200 dark:border-dark-border-primary p-6 space-y-3', className)}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-10 rounded-lg" />
      </div>
      <Skeleton className="h-10 w-32" />
      <Skeleton className="h-6 w-16 rounded-full" />
    </div>
  )
}

/**
 * Table Skeleton
 */
export function SkeletonTable({ rows = 5, columns = 4, className }) {
  return (
    <div className={cn('rounded-xl border border-neutral-slate-200 dark:border-dark-border-primary overflow-hidden', className)}>
      {/* Header */}
      <div className="bg-neutral-slate-100 dark:bg-dark-bg-tertiary p-4 flex gap-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-6 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      <div className="divide-y divide-neutral-slate-200 dark:divide-dark-border-subtle">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4 flex gap-4">
            {Array.from({ length: columns }).map((_, j) => (
              <Skeleton key={j} className="h-6 flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Chart Skeleton
 */
export function SkeletonChart({ className }) {
  return (
    <div className={cn('space-y-4', className)}>
      <Skeleton className="h-6 w-32" />
      <div className="flex items-end gap-2 h-64">
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton
            key={i}
            className="flex-1"
            style={{ height: `${Math.random() * 60 + 40}%` }}
          />
        ))}
      </div>
      <div className="flex justify-between">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-4 w-12" />
        ))}
      </div>
    </div>
  )
}

/**
 * Text Skeleton - for paragraphs
 */
export function SkeletonText({ lines = 3, className }) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn(
            'h-4',
            i === lines - 1 ? 'w-3/4' : 'w-full'
          )}
        />
      ))}
    </div>
  )
}

/**
 * Dashboard Skeleton - complete dashboard layout
 */
export function SkeletonDashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-6 w-96" />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonMetricCard key={i} />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <SkeletonChart />
        <SkeletonChart />
      </div>

      {/* Table */}
      <SkeletonTable rows={5} columns={5} />
    </div>
  )
}

// Add shimmer animation to global styles
if (typeof document !== 'undefined') {
  const style = document.createElement('style')
  style.innerHTML = `
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
  `
  document.head.appendChild(style)
}

















