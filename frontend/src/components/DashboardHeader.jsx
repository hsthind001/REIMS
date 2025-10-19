import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  ChevronDown,
  Command,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useToast } from './ui/Toast'

/**
 * REIMS Modern Dashboard Header
 * 
 * Features:
 * - Animated gradient logo
 * - Real-time clock
 * - System status indicator
 * - User profile dropdown
 * - Command palette search (Cmd+K / Ctrl+K)
 * - Notifications with badge
 * - Glassmorphism effect
 */

export default function DashboardHeader({ 
  user = { name: 'John Doe', email: 'john@reims.io', avatar: null },
  notifications = [],
  systemStatus = 'healthy', // 'healthy', 'warning', 'critical'
  onLogout,
  className 
}) {
  const { toast } = useToast()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showCommandPalette, setShowCommandPalette] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const searchInputRef = useRef(null)

  // Real-time clock update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Command palette keyboard shortcut (Cmd+K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setShowCommandPalette(true)
      }
      if (e.key === 'Escape') {
        setShowCommandPalette(false)
        setShowUserMenu(false)
        setShowNotifications(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Focus search input when command palette opens
  useEffect(() => {
    if (showCommandPalette && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [showCommandPalette])

  // System status configuration
  const statusConfig = {
    healthy: {
      icon: CheckCircle2,
      color: 'text-growth-emerald-500',
      bg: 'bg-growth-emerald-500',
      label: 'All Systems Operational',
      pulse: true
    },
    warning: {
      icon: AlertTriangle,
      color: 'text-status-warning-500',
      bg: 'bg-status-warning-500',
      label: 'Some Issues Detected',
      pulse: true
    },
    critical: {
      icon: XCircle,
      color: 'text-status-error-500',
      bg: 'bg-status-error-500',
      label: 'Critical Issues',
      pulse: true
    }
  }

  const status = statusConfig[systemStatus]
  const StatusIcon = status.icon
  const unreadNotifications = notifications.filter(n => !n.read).length

  // Format time
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: true 
    })
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <>
      {/* Header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className={cn(
          'sticky top-0 z-50 backdrop-blur-xl bg-white/80 dark:bg-dark-bg-primary/80',
          'border-b border-neutral-slate-200/50 dark:border-dark-border-primary/50',
          'shadow-lg shadow-brand-blue-500/5',
          className
        )}
      >
        <div className="max-w-[1920px] mx-auto px-6 py-3">
          <div className="flex items-center justify-between gap-6">
            {/* Left Section: Logo + Status */}
            <div className="flex items-center gap-6">
              {/* Animated Logo */}
              <motion.div 
                className="flex items-center gap-3 cursor-pointer group"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="relative">
                  {/* Logo background glow */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-br from-brand-blue-500 to-accent-purple-500 rounded-xl blur-xl opacity-50"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.5, 0.8, 0.5]
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: 'easeInOut'
                    }}
                  />
                  
                  {/* Logo */}
                  <div className="relative w-12 h-12 bg-gradient-to-br from-brand-blue-500 to-accent-purple-500 rounded-xl flex items-center justify-center shadow-xl">
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                      className="text-white font-black text-2xl"
                    >
                      R
                    </motion.div>
                  </div>
                </div>

                {/* Brand name */}
                <div>
                  <h1 className="text-xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent">
                    REIMS
                  </h1>
                  <p className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                    Real Estate Intelligence
                  </p>
                </div>
              </motion.div>

              {/* System Status Indicator */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-neutral-slate-100/50 dark:bg-dark-bg-secondary/50 backdrop-blur-sm cursor-pointer"
              >
                <div className="relative">
                  <StatusIcon className={cn('w-5 h-5', status.color)} />
                  {status.pulse && (
                    <motion.div
                      className={cn('absolute inset-0 rounded-full', status.bg, 'opacity-20')}
                      animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0, 0.2] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </div>
                <span className="text-sm font-semibold text-neutral-slate-700 dark:text-dark-text-primary">
                  {status.label}
                </span>
              </motion.div>
            </div>

            {/* Center Section: Search Bar */}
            <div className="flex-1 max-w-2xl">
              <div className="relative">
                <button
                  onClick={() => setShowCommandPalette(true)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-2.5 rounded-xl',
                    'bg-neutral-slate-100/80 dark:bg-dark-bg-secondary/80 backdrop-blur-sm',
                    'border border-neutral-slate-200 dark:border-dark-border-primary',
                    'hover:border-brand-blue-400 dark:hover:border-brand-blue-600',
                    'hover:shadow-lg hover:shadow-brand-blue-500/10',
                    'transition-all duration-200 group'
                  )}
                >
                  <Search className="w-5 h-5 text-neutral-slate-400 group-hover:text-brand-blue-500 transition-colors" />
                  <span className="flex-1 text-left text-sm text-neutral-slate-500 dark:text-dark-text-secondary">
                    Search properties, documents, analytics...
                  </span>
                  <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-neutral-slate-200 dark:bg-dark-bg-tertiary">
                    <Command className="w-3 h-3 text-neutral-slate-600 dark:text-dark-text-secondary" />
                    <span className="text-xs font-semibold text-neutral-slate-600 dark:text-dark-text-secondary">
                      K
                    </span>
                  </div>
                </button>
              </div>
            </div>

            {/* Right Section: Clock + Notifications + User */}
            <div className="flex items-center gap-4">
              {/* Real-time Clock */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="hidden lg:block text-right"
              >
                <motion.div 
                  key={currentTime.toLocaleTimeString()}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary font-mono"
                >
                  {formatTime(currentTime)}
                </motion.div>
                <div className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                  {formatDate(currentTime)}
                </div>
              </motion.div>

              {/* Notifications */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative"
              >
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className={cn(
                    'relative p-3 rounded-xl',
                    'bg-neutral-slate-100 dark:bg-dark-bg-secondary',
                    'hover:bg-neutral-slate-200 dark:hover:bg-dark-bg-tertiary',
                    'transition-colors duration-200'
                  )}
                >
                  <Bell className="w-5 h-5 text-neutral-slate-700 dark:text-dark-text-primary" />
                  {unreadNotifications > 0 && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1.5 flex items-center justify-center rounded-full bg-gradient-to-r from-status-error-500 to-status-error-600 text-white text-xs font-bold shadow-lg"
                    >
                      {unreadNotifications > 9 ? '9+' : unreadNotifications}
                    </motion.div>
                  )}
                </button>

                {/* Notifications Dropdown */}
                <AnimatePresence>
                  {showNotifications && (
                    <NotificationsDropdown
                      notifications={notifications}
                      onClose={() => setShowNotifications(false)}
                    />
                  )}
                </AnimatePresence>
              </motion.div>

              {/* User Profile */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative"
              >
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-xl',
                    'bg-gradient-to-r from-brand-blue-500 to-accent-purple-500',
                    'hover:from-brand-blue-600 hover:to-accent-purple-600',
                    'transition-all duration-200 shadow-lg'
                  )}
                >
                  <div className="w-8 h-8 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="w-full h-full rounded-lg object-cover" />
                    ) : (
                      <User className="w-5 h-5 text-white" />
                    )}
                  </div>
                  <div className="hidden xl:block text-left">
                    <div className="text-sm font-bold text-white">{user.name}</div>
                    <div className="text-xs text-white/80">{user.email}</div>
                  </div>
                  <ChevronDown className="w-4 h-4 text-white" />
                </button>

                {/* User Dropdown */}
                <AnimatePresence>
                  {showUserMenu && (
                    <UserDropdown
                      user={user}
                      onClose={() => setShowUserMenu(false)}
                      onLogout={onLogout}
                    />
                  )}
                </AnimatePresence>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Command Palette Modal */}
      <AnimatePresence>
        {showCommandPalette && (
          <CommandPalette
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            searchInputRef={searchInputRef}
            onClose={() => setShowCommandPalette(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}

/**
 * Notifications Dropdown Component
 */
function NotificationsDropdown({ notifications, onClose }) {
  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-40"
      />

      {/* Dropdown */}
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ duration: 0.15 }}
        className={cn(
          'absolute right-0 top-full mt-2 w-96 z-50',
          'bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-xl',
          'border border-neutral-slate-200 dark:border-dark-border-primary',
          'rounded-xl shadow-2xl overflow-hidden'
        )}
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-neutral-slate-200 dark:border-dark-border-primary">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary">
              Notifications
            </h3>
            <button className="text-xs text-brand-blue-600 hover:text-brand-blue-700 font-semibold">
              Mark all as read
            </button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <Bell className="w-12 h-12 mx-auto mb-3 text-neutral-slate-300 dark:text-neutral-slate-600" />
              <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                No notifications yet
              </p>
            </div>
          ) : (
            notifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  'px-4 py-3 border-b border-neutral-slate-100 dark:border-dark-border-subtle',
                  'hover:bg-neutral-slate-50 dark:hover:bg-dark-bg-tertiary',
                  'transition-colors cursor-pointer',
                  !notification.read && 'bg-brand-blue-50/50 dark:bg-brand-blue-900/10'
                )}
              >
                <div className="flex items-start gap-3">
                  {!notification.read && (
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-brand-blue-500" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                      {notification.title}
                    </p>
                    <p className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary mt-0.5">
                      {notification.message}
                    </p>
                    <p className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary mt-1">
                      {notification.time}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="px-4 py-2 border-t border-neutral-slate-200 dark:border-dark-border-primary bg-neutral-slate-50 dark:bg-dark-bg-tertiary">
            <button className="text-xs text-brand-blue-600 hover:text-brand-blue-700 font-semibold">
              View all notifications →
            </button>
          </div>
        )}
      </motion.div>
    </>
  )
}

/**
 * User Dropdown Component
 */
function UserDropdown({ user, onClose, onLogout }) {
  const menuItems = [
    { icon: User, label: 'Profile', action: () => console.log('Profile') },
    { icon: Settings, label: 'Settings', action: () => console.log('Settings') },
    { icon: Activity, label: 'Activity Log', action: () => console.log('Activity') },
    { icon: LogOut, label: 'Logout', action: onLogout, danger: true },
  ]

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-40"
      />

      {/* Dropdown */}
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ duration: 0.15 }}
        className={cn(
          'absolute right-0 top-full mt-2 w-64 z-50',
          'bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-xl',
          'border border-neutral-slate-200 dark:border-dark-border-primary',
          'rounded-xl shadow-2xl overflow-hidden'
        )}
      >
        {/* User Info */}
        <div className="px-4 py-3 border-b border-neutral-slate-200 dark:border-dark-border-primary">
          <p className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            {user.name}
          </p>
          <p className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
            {user.email}
          </p>
        </div>

        {/* Menu Items */}
        <div className="py-2">
          {menuItems.map((item, index) => (
            <motion.button
              key={item.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => {
                item.action()
                onClose()
              }}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-2.5',
                'hover:bg-neutral-slate-50 dark:hover:bg-dark-bg-tertiary',
                'transition-colors text-left',
                item.danger 
                  ? 'text-status-error-600 hover:bg-status-error-50 dark:hover:bg-status-error-900/20' 
                  : 'text-neutral-slate-700 dark:text-dark-text-primary'
              )}
            >
              <item.icon className="w-4 h-4" />
              <span className="text-sm font-medium">{item.label}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </>
  )
}

/**
 * Command Palette Component
 */
function CommandPalette({ searchQuery, setSearchQuery, searchInputRef, onClose }) {
  const commands = [
    { id: 1, title: 'View Dashboard', category: 'Navigation', shortcut: 'Ctrl+D' },
    { id: 2, title: 'Upload Document', category: 'Actions', shortcut: 'Ctrl+U' },
    { id: 3, title: 'Search Properties', category: 'Search', shortcut: 'Ctrl+P' },
    { id: 4, title: 'Analytics Report', category: 'Reports', shortcut: 'Ctrl+R' },
    { id: 5, title: 'AI Insights', category: 'AI', shortcut: 'Ctrl+I' },
  ]

  const filteredCommands = commands.filter(cmd =>
    cmd.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cmd.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100]"
      />

      {/* Command Palette */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.2 }}
        className="fixed top-24 left-1/2 -translate-x-1/2 w-full max-w-2xl z-[101]"
      >
        <div className={cn(
          'bg-white/95 dark:bg-dark-bg-secondary/95 backdrop-blur-xl',
          'border border-neutral-slate-200 dark:border-dark-border-primary',
          'rounded-2xl shadow-2xl overflow-hidden'
        )}>
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-4 border-b border-neutral-slate-200 dark:border-dark-border-primary">
            <Search className="w-5 h-5 text-neutral-slate-400" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent outline-none text-neutral-slate-900 dark:text-dark-text-primary placeholder-neutral-slate-400"
            />
            <button
              onClick={onClose}
              className="px-2 py-1 rounded-md text-xs font-semibold text-neutral-slate-600 dark:text-dark-text-secondary bg-neutral-slate-100 dark:bg-dark-bg-tertiary"
            >
              ESC
            </button>
          </div>

          {/* Results */}
          <div className="max-h-96 overflow-y-auto py-2">
            {filteredCommands.length === 0 ? (
              <div className="px-4 py-8 text-center text-neutral-slate-600 dark:text-dark-text-secondary">
                No results found
              </div>
            ) : (
              filteredCommands.map((cmd, index) => (
                <motion.div
                  key={cmd.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    'flex items-center justify-between px-4 py-3',
                    'hover:bg-brand-blue-50 dark:hover:bg-brand-blue-900/20',
                    'cursor-pointer transition-colors'
                  )}
                >
                  <div>
                    <p className="text-sm font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                      {cmd.title}
                    </p>
                    <p className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                      {cmd.category}
                    </p>
                  </div>
                  <span className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary font-mono">
                    {cmd.shortcut}
                  </span>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </motion.div>
    </>
  )
}

















