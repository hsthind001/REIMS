import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home,
  Building2,
  Bell,
  FileText,
  Menu,
  X,
  ChevronLeft,
  Search,
  MoreVertical
} from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * REIMS Mobile Layout
 * 
 * Features:
 * - Single column layout for KPI cards
 * - Collapsible navigation menu
 * - Full-screen property detail view
 * - Swipeable chart navigation
 * - Bottom tab navigation
 * - Touchable button sizes (44x44px minimum)
 * - Mobile-optimized data tables
 * - Maintains color scheme and branding
 */

export default function MobileLayout({ 
  activeTab, 
  onTabChange, 
  onOpenCommandPalette,
  children 
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Close mobile menu when tab changes
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [activeTab])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen && isMobile) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isMobileMenuOpen, isMobile])

  const tabs = [
    { id: 'portfolio', label: 'Dashboard', icon: Home },
    { id: 'kpi', label: 'Properties', icon: Building2 },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'upload', label: 'Documents', icon: FileText },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-blue-600 to-accent-purple-600">
      {/* Mobile Header */}
      <MobileHeader
        isMobileMenuOpen={isMobileMenuOpen}
        onToggleMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        onOpenSearch={onOpenCommandPalette}
      />

      {/* Collapsible Navigation Menu (Mobile) */}
      <AnimatePresence>
        {isMobileMenuOpen && isMobile && (
          <CollapsibleMenu
            activeTab={activeTab}
            onTabChange={onTabChange}
            onClose={() => setIsMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <main 
        className={cn(
          'pb-20 md:pb-6',
          isMobile && 'px-4 pt-4'
        )}
      >
        {children}
      </main>

      {/* Bottom Tab Navigation (Mobile Only) */}
      {isMobile && (
        <BottomTabNavigation
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={onTabChange}
        />
      )}
    </div>
  )
}

/**
 * Mobile Header Component
 */
function MobileHeader({ isMobileMenuOpen, onToggleMenu, onOpenSearch }) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-lg border-b border-neutral-slate-200 dark:border-dark-border-primary shadow-sm">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Logo & Menu Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMenu}
            className="md:hidden p-2 -ml-2 rounded-lg hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-all touch-manipulation"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-neutral-slate-700 dark:text-dark-text-primary" />
            ) : (
              <Menu className="w-6 h-6 text-neutral-slate-700 dark:text-dark-text-primary" />
            )}
          </button>
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-brand-blue-500 to-accent-purple-500 flex items-center justify-center">
              <span className="text-white font-black text-lg md:text-xl">R</span>
            </div>
            <div>
              <h1 className="text-lg md:text-xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent">
                REIMS
              </h1>
            </div>
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={onOpenSearch}
          className="p-2 rounded-lg hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-all touch-manipulation"
          style={{ minWidth: '44px', minHeight: '44px' }}
        >
          <Search className="w-5 h-5 text-neutral-slate-600 dark:text-dark-text-secondary" />
        </button>
      </div>
    </header>
  )
}

/**
 * Collapsible Navigation Menu
 */
function CollapsibleMenu({ activeTab, onTabChange, onClose }) {
  const menuItems = [
    { id: 'portfolio', label: 'Portfolio', icon: Home, color: 'from-brand-blue-500 to-brand-blue-600' },
    { id: 'kpi', label: 'KPI Dashboard', icon: Building2, color: 'from-accent-indigo-500 to-accent-purple-500' },
    { id: 'location', label: 'Location Analysis', icon: '📍', color: 'from-brand-blue-500 to-accent-purple-500' },
    { id: 'tenants', label: 'AI Tenants', icon: '🤖', color: 'from-accent-purple-500 to-accent-violet-500' },
    { id: 'upload', label: 'Upload', icon: FileText, color: 'from-accent-purple-500 to-accent-violet-600' },
    { id: 'processing', label: 'Processing', icon: '⚙️', color: 'from-accent-indigo-500 to-accent-purple-500' },
    { id: 'charts', label: 'Charts', icon: '📈', color: 'from-brand-teal-500 to-accent-cyan-500' },
    { id: 'exit', label: 'Exit Strategy', icon: '🎯', color: 'from-status-warning-500 to-accent-orange-500' },
    { id: 'monitoring', label: 'Monitoring', icon: '📡', color: 'from-growth-emerald-500 to-growth-lime-500' },
    { id: 'alerts', label: 'Alerts', icon: Bell, color: 'from-status-error-500 to-status-warning-500' },
  ]

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
      />

      {/* Menu Drawer */}
      <motion.div
        initial={{ x: '-100%' }}
        animate={{ x: 0 }}
        exit={{ x: '-100%' }}
        transition={{ type: 'tween', duration: 0.3 }}
        className="fixed left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-white dark:bg-dark-bg-secondary shadow-2xl z-50 overflow-y-auto"
      >
        {/* Menu Header */}
        <div className="p-6 border-b border-neutral-slate-200 dark:border-dark-border-primary">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-blue-500 to-accent-purple-500 flex items-center justify-center">
              <span className="text-white font-black text-2xl">R</span>
            </div>
            <div>
              <h2 className="text-xl font-black text-neutral-slate-900 dark:text-dark-text-primary">
                REIMS
              </h2>
              <p className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                Real Estate Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="p-4">
          <div className="space-y-2">
            {menuItems.map((item) => {
              const Icon = typeof item.icon === 'string' ? null : item.icon
              const isActive = activeTab === item.id

              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all touch-manipulation',
                    'hover:bg-neutral-slate-50 dark:hover:bg-dark-bg-tertiary',
                    isActive && 'bg-gradient-to-r text-white shadow-lg',
                    !isActive && 'text-neutral-slate-700 dark:text-dark-text-primary'
                  )}
                  style={{
                    minHeight: '44px',
                    ...(isActive && {
                      backgroundImage: `linear-gradient(to right, ${item.color.replace('from-', '').replace('to-', ', ')})`,
                    })
                  }}
                >
                  {Icon ? (
                    <Icon className="w-5 h-5 shrink-0" />
                  ) : (
                    <span className="text-xl shrink-0">{item.icon}</span>
                  )}
                  <span className="font-semibold text-sm">{item.label}</span>
                </button>
              )
            })}
          </div>
        </nav>
      </motion.div>
    </>
  )
}

/**
 * Bottom Tab Navigation
 */
function BottomTabNavigation({ tabs, activeTab, onTabChange }) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-lg border-t border-neutral-slate-200 dark:border-dark-border-primary shadow-lg z-30">
      <div className="flex items-center justify-around px-2 py-2 safe-area-inset-bottom">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                'flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-lg transition-all touch-manipulation',
                'active:scale-95',
                isActive && 'bg-gradient-to-br from-brand-blue-50 to-accent-purple-50 dark:from-brand-blue-900/20 dark:to-accent-purple-900/20'
              )}
              style={{ minWidth: '44px', minHeight: '44px' }}
            >
              <Icon 
                className={cn(
                  'w-5 h-5',
                  isActive 
                    ? 'text-brand-blue-600 dark:text-brand-blue-400' 
                    : 'text-neutral-slate-600 dark:text-dark-text-secondary'
                )}
              />
              <span
                className={cn(
                  'text-xs font-semibold',
                  isActive
                    ? 'text-brand-blue-600 dark:text-brand-blue-400'
                    : 'text-neutral-slate-600 dark:text-dark-text-secondary'
                )}
              >
                {tab.label}
              </span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}

/**
 * Mobile-Optimized Card Container
 * Single column layout, full-width cards
 */
export function MobileCardContainer({ children, className }) {
  return (
    <div className={cn(
      'grid grid-cols-1 gap-4',
      'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
      className
    )}>
      {children}
    </div>
  )
}

/**
 * Mobile-Optimized Data Table
 * Horizontal scroll with sticky header
 */
export function MobileDataTable({ columns, data, className }) {
  return (
    <div className={cn(
      'overflow-x-auto -mx-4 md:mx-0',
      'scrollbar-thin scrollbar-thumb-neutral-slate-300 scrollbar-track-neutral-slate-100',
      className
    )}>
      <table className="min-w-full divide-y divide-neutral-slate-200 dark:divide-dark-border-primary">
        <thead className="bg-neutral-slate-50 dark:bg-dark-bg-tertiary sticky top-0">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                className="px-4 py-3 text-left text-xs font-semibold text-neutral-slate-600 dark:text-dark-text-secondary uppercase tracking-wider whitespace-nowrap"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-dark-bg-secondary divide-y divide-neutral-slate-200 dark:divide-dark-border-primary">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-neutral-slate-50 dark:hover:bg-dark-bg-tertiary">
              {columns.map((column, colIndex) => (
                <td
                  key={colIndex}
                  className="px-4 py-3 text-sm text-neutral-slate-900 dark:text-dark-text-primary whitespace-nowrap"
                >
                  {column.accessor ? row[column.accessor] : column.cell?.(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * Touchable Button Component
 * Minimum 44x44px touch target
 */
export function TouchableButton({ 
  children, 
  variant = 'primary', 
  size = 'default',
  className,
  ...props 
}) {
  const variants = {
    primary: 'bg-gradient-to-r from-brand-blue-500 to-accent-purple-500 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-white dark:bg-dark-bg-tertiary text-neutral-slate-900 dark:text-dark-text-primary border border-neutral-slate-200 dark:border-dark-border-primary',
    ghost: 'bg-transparent hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary text-neutral-slate-700 dark:text-dark-text-primary',
  }

  const sizes = {
    small: 'px-4 py-2 text-sm min-h-[44px]',
    default: 'px-6 py-3 text-base min-h-[44px]',
    large: 'px-8 py-4 text-lg min-h-[52px]',
  }

  return (
    <button
      className={cn(
        'rounded-xl font-semibold transition-all active:scale-95 touch-manipulation',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

/**
 * Full-Screen Property Detail View
 */
export function FullScreenPropertyView({ property, onClose, children }) {
  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'tween', duration: 0.3 }}
      className="fixed inset-0 bg-white dark:bg-dark-bg-secondary z-50 overflow-y-auto"
    >
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-lg border-b border-neutral-slate-200 dark:border-dark-border-primary">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            onClick={onClose}
            className="p-2 -ml-2 rounded-lg hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-all touch-manipulation"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            <ChevronLeft className="w-6 h-6 text-neutral-slate-700 dark:text-dark-text-primary" />
          </button>
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-black text-neutral-slate-900 dark:text-dark-text-primary truncate">
              {property?.name || 'Property Details'}
            </h2>
            <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary truncate">
              {property?.address}
            </p>
          </div>
          <button
            className="p-2 rounded-lg hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary active:scale-95 transition-all touch-manipulation"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            <MoreVertical className="w-5 h-5 text-neutral-slate-600 dark:text-dark-text-secondary" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {children}
      </div>
    </motion.div>
  )
}

/**
 * Swipeable Chart Container
 * For mobile chart navigation
 */
export function SwipeableChartContainer({ charts, className }) {
  const [currentIndex, setCurrentIndex] = useState(0)

  return (
    <div className={cn('relative', className)}>
      {/* Chart Display */}
      <div className="overflow-hidden rounded-xl bg-white dark:bg-dark-bg-secondary shadow-lg">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.3 }}
            className="p-4"
          >
            {charts[currentIndex]}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Dots Indicator */}
      <div className="flex items-center justify-center gap-2 mt-4">
        {charts.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentIndex(index)}
            className={cn(
              'w-2 h-2 rounded-full transition-all touch-manipulation',
              index === currentIndex
                ? 'w-6 bg-brand-blue-600'
                : 'bg-neutral-slate-300 dark:bg-neutral-slate-600'
            )}
            style={{ minWidth: '44px', minHeight: '44px' }}
          />
        ))}
      </div>

      {/* Navigation Buttons (Optional) */}
      {charts.length > 1 && (
        <>
          <button
            onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/90 dark:bg-dark-bg-tertiary/90 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={() => setCurrentIndex((prev) => Math.min(charts.length - 1, prev + 1))}
            disabled={currentIndex === charts.length - 1}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/90 dark:bg-dark-bg-tertiary/90 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            <ChevronLeft className="w-5 h-5 rotate-180" />
          </button>
        </>
      )}
    </div>
  )
}
















