import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search,
  Building2,
  FileUp,
  BarChart3,
  FileText,
  Download,
  File,
  Clock,
  Home,
  TrendingUp,
  Settings,
  Users,
  DollarSign,
  Calendar,
  Map,
  Zap,
  ChevronRight,
  Command,
  ArrowUp,
  Hash
} from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * REIMS Command Palette
 * 
 * Features:
 * - Cmd+K / Ctrl+K activation
 * - Quick navigation to properties
 * - Upload document shortcuts
 * - Run analysis commands
 * - Generate reports
 * - Export data
 * - Search documents
 * - Recent actions tracking
 * - Keyboard navigation (arrows, enter, esc)
 * - Highlighted results
 * - Command descriptions & keyboard shortcuts
 */

export default function CommandPalette({ isOpen, onClose, onNavigate }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentActions, setRecentActions] = useState([])
  const inputRef = useRef(null)
  const listRef = useRef(null)

  // Real properties for quick navigation
  const properties = [
    { id: 1, name: 'Empire State Plaza', address: '1 Empire State Plaza, Albany, NY' },
  ]

  // All available commands
  const allCommands = [
    // Navigation Commands
    {
      id: 'nav-portfolio',
      category: 'Navigation',
      title: 'Go to Portfolio',
      description: 'View all properties in your portfolio',
      icon: Building2,
      shortcut: 'G P',
      action: () => onNavigate?.('portfolio'),
    },
    {
      id: 'nav-kpi',
      category: 'Navigation',
      title: 'Go to KPI Dashboard',
      description: 'View key performance indicators',
      icon: TrendingUp,
      shortcut: 'G K',
      action: () => onNavigate?.('kpi'),
    },
    {
      id: 'nav-location',
      category: 'Navigation',
      title: 'Go to Location Analysis',
      description: 'View market intelligence',
      icon: Map,
      shortcut: 'G L',
      action: () => onNavigate?.('location'),
    },
    {
      id: 'nav-tenants',
      category: 'Navigation',
      title: 'Go to AI Tenant Recommendations',
      description: 'View tenant matching suggestions',
      icon: Users,
      shortcut: 'G T',
      action: () => onNavigate?.('tenants'),
    },
    {
      id: 'nav-charts',
      category: 'Navigation',
      title: 'Go to Financial Charts',
      description: 'View financial analytics',
      icon: BarChart3,
      shortcut: 'G C',
      action: () => onNavigate?.('charts'),
    },

    // Property Quick Access
    ...properties.map(property => ({
      id: `property-${property.id}`,
      category: 'Properties',
      title: property.name,
      description: property.address,
      icon: Building2,
      action: () => {
        console.log('Navigate to property:', property.id)
        onNavigate?.('portfolio', property.id)
      },
    })),

    // Upload Commands
    {
      id: 'upload-document',
      category: 'Upload',
      title: 'Upload Document',
      description: 'Upload a new document or lease',
      icon: FileUp,
      shortcut: 'U D',
      action: () => onNavigate?.('upload'),
    },
    {
      id: 'upload-financial',
      category: 'Upload',
      title: 'Upload Financial Data',
      description: 'Import financial statements',
      icon: DollarSign,
      shortcut: 'U F',
      action: () => {
        console.log('Upload financial data')
        onNavigate?.('upload')
      },
    },
    {
      id: 'upload-property',
      category: 'Upload',
      title: 'Upload Property Data',
      description: 'Bulk import property information',
      icon: FileUp,
      shortcut: 'U P',
      action: () => {
        console.log('Upload property data')
        onNavigate?.('upload')
      },
    },

    // Analysis Commands
    {
      id: 'analysis-portfolio',
      category: 'Analysis',
      title: 'Run Portfolio Analysis',
      description: 'Analyze entire portfolio performance',
      icon: BarChart3,
      shortcut: 'A P',
      action: () => {
        console.log('Running portfolio analysis...')
        onNavigate?.('charts')
      },
    },
    {
      id: 'analysis-tenant',
      category: 'Analysis',
      title: 'Analyze Tenant Mix',
      description: 'Review current tenant composition',
      icon: Users,
      shortcut: 'A T',
      action: () => {
        console.log('Analyzing tenant mix...')
        onNavigate?.('tenants')
      },
    },
    {
      id: 'analysis-market',
      category: 'Analysis',
      title: 'Run Market Analysis',
      description: 'Analyze market conditions and trends',
      icon: TrendingUp,
      shortcut: 'A M',
      action: () => {
        console.log('Running market analysis...')
        onNavigate?.('location')
      },
    },
    {
      id: 'analysis-financial',
      category: 'Analysis',
      title: 'Financial Performance Analysis',
      description: 'Analyze revenue and expenses',
      icon: DollarSign,
      shortcut: 'A F',
      action: () => {
        console.log('Running financial analysis...')
        onNavigate?.('charts')
      },
    },

    // Report Commands
    {
      id: 'report-monthly',
      category: 'Reports',
      title: 'Generate Monthly Report',
      description: 'Create comprehensive monthly summary',
      icon: FileText,
      shortcut: 'R M',
      action: () => {
        console.log('Generating monthly report...')
        alert('Monthly report generation started!')
      },
    },
    {
      id: 'report-quarterly',
      category: 'Reports',
      title: 'Generate Quarterly Report',
      description: 'Create Q1-Q4 financial report',
      icon: Calendar,
      shortcut: 'R Q',
      action: () => {
        console.log('Generating quarterly report...')
        alert('Quarterly report generation started!')
      },
    },
    {
      id: 'report-tenant',
      category: 'Reports',
      title: 'Generate Tenant Report',
      description: 'Export tenant roster and details',
      icon: Users,
      action: () => {
        console.log('Generating tenant report...')
        alert('Tenant report generation started!')
      },
    },
    {
      id: 'report-occupancy',
      category: 'Reports',
      title: 'Occupancy Report',
      description: 'View occupancy rates and trends',
      icon: Building2,
      action: () => {
        console.log('Generating occupancy report...')
        alert('Occupancy report generation started!')
      },
    },

    // Export Commands
    {
      id: 'export-csv',
      category: 'Export',
      title: 'Export to CSV',
      description: 'Download data in CSV format',
      icon: Download,
      shortcut: 'E C',
      action: () => {
        console.log('Exporting to CSV...')
        alert('CSV export started!')
      },
    },
    {
      id: 'export-excel',
      category: 'Export',
      title: 'Export to Excel',
      description: 'Download data in Excel format',
      icon: Download,
      shortcut: 'E X',
      action: () => {
        console.log('Exporting to Excel...')
        alert('Excel export started!')
      },
    },
    {
      id: 'export-pdf',
      category: 'Export',
      title: 'Export to PDF',
      description: 'Generate PDF document',
      icon: FileText,
      shortcut: 'E P',
      action: () => {
        console.log('Exporting to PDF...')
        alert('PDF export started!')
      },
    },

    // Document Search
    {
      id: 'search-leases',
      category: 'Search',
      title: 'Search Leases',
      description: 'Find lease documents',
      icon: File,
      action: () => {
        console.log('Searching leases...')
        onNavigate?.('upload')
      },
    },
    {
      id: 'search-contracts',
      category: 'Search',
      title: 'Search Contracts',
      description: 'Find contract documents',
      icon: File,
      action: () => {
        console.log('Searching contracts...')
        onNavigate?.('upload')
      },
    },
    {
      id: 'search-financial',
      category: 'Search',
      title: 'Search Financial Docs',
      description: 'Find financial documents',
      icon: DollarSign,
      action: () => {
        console.log('Searching financial docs...')
        onNavigate?.('upload')
      },
    },

    // Quick Actions
    {
      id: 'quick-dashboard',
      category: 'Quick Actions',
      title: 'Open Dashboard',
      description: 'Go to main dashboard',
      icon: Home,
      shortcut: 'G H',
      action: () => onNavigate?.('portfolio'),
    },
    {
      id: 'quick-alerts',
      category: 'Quick Actions',
      title: 'View Alerts',
      description: 'Check system alerts',
      icon: Zap,
      shortcut: 'G A',
      action: () => onNavigate?.('alerts'),
    },
    {
      id: 'quick-settings',
      category: 'Quick Actions',
      title: 'Open Settings',
      description: 'Configure application settings',
      icon: Settings,
      action: () => {
        console.log('Opening settings...')
        alert('Settings panel would open here')
      },
    },
  ]

  // Filter commands based on search query
  const filteredCommands = searchQuery
    ? allCommands.filter(
        (cmd) =>
          cmd.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          cmd.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          cmd.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allCommands

  // Group filtered commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = []
    }
    acc[cmd.category].push(cmd)
    return acc
  }, {})

  // Add recent actions if no search query
  useEffect(() => {
    if (!searchQuery && recentActions.length > 0) {
      groupedCommands['Recent Actions'] = recentActions
    }
  }, [searchQuery, recentActions])

  // Handle command execution
  const executeCommand = useCallback(
    (command) => {
      // Add to recent actions
      setRecentActions((prev) => {
        const filtered = prev.filter((cmd) => cmd.id !== command.id)
        return [command, ...filtered].slice(0, 5) // Keep only 5 recent
      })

      // Execute the command
      command.action?.()

      // Close palette
      onClose?.()
    },
    [onClose]
  )

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex((prev) => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex])
          }
          break
        case 'Escape':
          e.preventDefault()
          onClose?.()
          break
        default:
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selectedIndex, filteredCommands, executeCommand, onClose])

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      setSearchQuery('')
      setSelectedIndex(0)
      inputRef.current?.focus()
    }
  }, [isOpen])

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current && selectedIndex >= 0) {
      const selectedElement = listRef.current.children[selectedIndex]
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth',
        })
      }
    }
  }, [selectedIndex])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9998]"
          />

          {/* Command Palette */}
          <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-[15vh] px-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="w-full max-w-2xl bg-white dark:bg-dark-bg-secondary rounded-2xl shadow-2xl border border-neutral-slate-200 dark:border-dark-border-primary overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Search Input */}
              <div className="flex items-center gap-3 px-4 py-4 border-b border-neutral-slate-200 dark:border-dark-border-primary">
                <Search className="w-5 h-5 text-neutral-slate-400 dark:text-dark-text-secondary shrink-0" />
                <input
                  ref={inputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value)
                    setSelectedIndex(0)
                  }}
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent border-none outline-none text-neutral-slate-900 dark:text-dark-text-primary placeholder:text-neutral-slate-400 dark:placeholder:text-dark-text-secondary text-base"
                />
                <kbd className="hidden sm:flex items-center gap-1 px-2 py-1 rounded bg-neutral-slate-100 dark:bg-dark-bg-tertiary border border-neutral-slate-200 dark:border-dark-border-primary text-xs font-mono text-neutral-slate-600 dark:text-dark-text-secondary">
                  ESC
                </kbd>
              </div>

              {/* Commands List */}
              <div className="max-h-[60vh] overflow-y-auto" ref={listRef}>
                {Object.keys(groupedCommands).length === 0 ? (
                  <div className="py-12 text-center">
                    <p className="text-neutral-slate-500 dark:text-dark-text-secondary">
                      No commands found
                    </p>
                  </div>
                ) : (
                  Object.entries(groupedCommands).map(([category, commands], categoryIndex) => (
                    <div key={category}>
                      {/* Category Header */}
                      <div className="px-4 py-2 bg-neutral-slate-50 dark:bg-dark-bg-tertiary">
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-slate-500 dark:text-dark-text-secondary">
                          {category}
                        </h3>
                      </div>

                      {/* Commands in Category */}
                      {commands.map((command, commandIndex) => {
                        const globalIndex = filteredCommands.findIndex((c) => c.id === command.id)
                        const isSelected = globalIndex === selectedIndex
                        const Icon = command.icon

                        return (
                          <motion.button
                            key={command.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: commandIndex * 0.02 }}
                            onClick={() => executeCommand(command)}
                            className={cn(
                              'w-full flex items-center gap-3 px-4 py-3 transition-colors',
                              'hover:bg-neutral-slate-100 dark:hover:bg-dark-bg-tertiary',
                              isSelected &&
                                'bg-brand-blue-50 dark:bg-brand-blue-900/20 border-l-2 border-brand-blue-500'
                            )}
                          >
                            {/* Icon */}
                            <div
                              className={cn(
                                'p-2 rounded-lg shrink-0',
                                isSelected
                                  ? 'bg-brand-blue-100 dark:bg-brand-blue-900/40 text-brand-blue-600 dark:text-brand-blue-400'
                                  : 'bg-neutral-slate-100 dark:bg-dark-bg-tertiary text-neutral-slate-600 dark:text-dark-text-secondary'
                              )}
                            >
                              <Icon className="w-4 h-4" />
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0 text-left">
                              <div className="font-semibold text-sm text-neutral-slate-900 dark:text-dark-text-primary truncate">
                                {command.title}
                              </div>
                              <div className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary truncate">
                                {command.description}
                              </div>
                            </div>

                            {/* Shortcut */}
                            {command.shortcut && (
                              <div className="hidden sm:flex items-center gap-1 shrink-0">
                                {command.shortcut.split(' ').map((key, idx) => (
                                  <kbd
                                    key={idx}
                                    className="px-2 py-1 rounded bg-neutral-slate-100 dark:bg-dark-bg-tertiary border border-neutral-slate-200 dark:border-dark-border-primary text-xs font-mono text-neutral-slate-600 dark:text-dark-text-secondary"
                                  >
                                    {key}
                                  </kbd>
                                ))}
                              </div>
                            )}

                            {/* Chevron */}
                            <ChevronRight
                              className={cn(
                                'w-4 h-4 shrink-0',
                                isSelected
                                  ? 'text-brand-blue-600 dark:text-brand-blue-400'
                                  : 'text-neutral-slate-400 dark:text-dark-text-secondary opacity-0 group-hover:opacity-100'
                              )}
                            />
                          </motion.button>
                        )
                      })}
                    </div>
                  ))
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between px-4 py-3 bg-neutral-slate-50 dark:bg-dark-bg-tertiary border-t border-neutral-slate-200 dark:border-dark-border-primary text-xs text-neutral-slate-500 dark:text-dark-text-secondary">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <ArrowUp className="w-3 h-3" />
                    <ArrowUp className="w-3 h-3 rotate-180" />
                    Navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary font-mono">
                      ↵
                    </kbd>
                    Select
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary font-mono">
                      ESC
                    </kbd>
                    Close
                  </span>
                </div>
                <span className="hidden sm:block">{filteredCommands.length} commands</span>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}

/**
 * Hook to manage Command Palette state
 */
export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen((prev) => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
  }
}













