import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  SlidersHorizontal,
  Eye,
  Edit,
  BarChart3,
  MapPin,
  TrendingUp,
  TrendingDown,
  Home,
  DollarSign,
  Users,
  Calendar,
  ArrowUpDown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useToast } from './ui/Toast'

/**
 * REIMS Property Portfolio Grid
 * 
 * Features:
 * - Property cards with image/gradient overlays
 * - Key metrics (occupancy, NOI, DSCR)
 * - Status badges (healthy/warning/critical)
 * - Quick action buttons
 * - Filtering by status
 * - Search by name/address
 * - Sorting options
 * - Hover effects revealing additional metrics
 */

export default function PropertyPortfolioGrid({ properties = [], onViewProperty, onEditProperty, onAnalyzeProperty }) {
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('name')
  const [sortOrder, setSortOrder] = useState('asc')
  const [showFilters, setShowFilters] = useState(false)

  // Filter and sort properties
  const filteredAndSortedProperties = useMemo(() => {
    let filtered = properties

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(property =>
        property.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        property.address.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(property => property.status === statusFilter)
    }

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      let aValue = a[sortBy]
      let bValue = b[sortBy]

      // Handle numeric values
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
      }

      // Handle string values
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return 0
    })

    return filtered
  }, [properties, searchQuery, statusFilter, sortBy, sortOrder])

  // Status counts
  const statusCounts = useMemo(() => {
    return {
      all: properties.length,
      healthy: properties.filter(p => p.status === 'healthy').length,
      warning: properties.filter(p => p.status === 'warning').length,
      critical: properties.filter(p => p.status === 'critical').length,
    }
  }, [properties])

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('asc')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="space-y-4">
        {/* Search and Filter Bar */}
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search properties by name or address..."
              className={cn(
                'w-full pl-12 pr-4 py-3 rounded-xl',
                'bg-white dark:bg-dark-bg-secondary',
                'border border-neutral-slate-200 dark:border-dark-border-primary',
                'focus:ring-2 focus:ring-brand-blue-500 focus:border-transparent',
                'transition-all duration-200'
              )}
            />
          </div>

          {/* Filter Toggle */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'px-6 py-3 rounded-xl font-semibold flex items-center gap-2',
              'transition-colors duration-200',
              showFilters
                ? 'bg-brand-blue-500 text-white'
                : 'bg-neutral-slate-100 dark:bg-dark-bg-tertiary text-neutral-slate-700 dark:text-dark-text-primary hover:bg-neutral-slate-200 dark:hover:bg-neutral-slate-600'
            )}
          >
            <SlidersHorizontal className="w-5 h-5" />
            <span>Filters</span>
          </motion.button>
        </div>

        {/* Filter Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="p-6 rounded-xl bg-neutral-slate-50 dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Status Filter */}
                  <div>
                    <h3 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                      Status
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { value: 'all', label: 'All', count: statusCounts.all },
                        { value: 'healthy', label: 'Healthy', count: statusCounts.healthy },
                        { value: 'warning', label: 'Warning', count: statusCounts.warning },
                        { value: 'critical', label: 'Critical', count: statusCounts.critical },
                      ].map((status) => (
                        <button
                          key={status.value}
                          onClick={() => setStatusFilter(status.value)}
                          className={cn(
                            'px-4 py-2 rounded-lg font-semibold text-sm transition-all',
                            statusFilter === status.value
                              ? 'bg-brand-blue-500 text-white shadow-lg'
                              : 'bg-white dark:bg-dark-bg-tertiary text-neutral-slate-700 dark:text-dark-text-primary hover:bg-neutral-slate-100 dark:hover:bg-neutral-slate-600'
                          )}
                        >
                          {status.label} ({status.count})
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Sort Options */}
                  <div>
                    <h3 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                      Sort By
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { value: 'name', label: 'Name' },
                        { value: 'occupancy', label: 'Occupancy' },
                        { value: 'noi', label: 'NOI' },
                        { value: 'dscr', label: 'DSCR' },
                      ].map((sort) => (
                        <button
                          key={sort.value}
                          onClick={() => toggleSort(sort.value)}
                          className={cn(
                            'px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2',
                            sortBy === sort.value
                              ? 'bg-brand-blue-500 text-white shadow-lg'
                              : 'bg-white dark:bg-dark-bg-tertiary text-neutral-slate-700 dark:text-dark-text-primary hover:bg-neutral-slate-100 dark:hover:bg-neutral-slate-600'
                          )}
                        >
                          {sort.label}
                          {sortBy === sort.value && (
                            <ArrowUpDown className="w-4 h-4" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Count */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
            Showing <span className="font-bold">{filteredAndSortedProperties.length}</span> of{' '}
            <span className="font-bold">{properties.length}</span> properties
          </p>
        </div>
      </div>

      {/* Property Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <AnimatePresence mode="popLayout">
          {filteredAndSortedProperties.map((property, index) => (
            <PropertyCard
              key={property.id}
              property={property}
              index={index}
              onView={() => onViewProperty?.(property)}
              onEdit={() => onEditProperty?.(property)}
              onAnalyze={() => onAnalyzeProperty?.(property)}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredAndSortedProperties.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <Home className="w-16 h-16 mx-auto mb-4 text-neutral-slate-300 dark:text-neutral-slate-600" />
          <h3 className="text-xl font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2">
            No properties found
          </h3>
          <p className="text-neutral-slate-600 dark:text-dark-text-secondary">
            Try adjusting your search or filters
          </p>
        </motion.div>
      )}
    </div>
  )
}

/**
 * Property Card Component
 */
function PropertyCard({ property, index, onView, onEdit, onAnalyze }) {
  const [isHovered, setIsHovered] = useState(false)
  const { toast } = useToast()

  // Status configuration
  const statusConfig = {
    healthy: {
      color: 'bg-growth-emerald-500',
      text: 'text-growth-emerald-700',
      bg: 'bg-growth-emerald-100',
      label: 'Healthy',
      icon: TrendingUp,
    },
    warning: {
      color: 'bg-status-warning-500',
      text: 'text-status-warning-700',
      bg: 'bg-status-warning-100',
      label: 'Warning',
      icon: TrendingUp,
    },
    critical: {
      color: 'bg-status-error-500',
      text: 'text-status-error-700',
      bg: 'bg-status-error-100',
      label: 'Critical',
      icon: TrendingDown,
    },
  }

  const statusData = statusConfig[property.status] || statusConfig.healthy
  const StatusIcon = statusData.icon

  // Metric color coding
  const getMetricColor = (value, type) => {
    if (type === 'occupancy') {
      if (value >= 95) return 'text-growth-emerald-600'
      if (value >= 85) return 'text-status-warning-600'
      return 'text-status-error-600'
    }
    if (type === 'dscr') {
      if (value >= 1.5) return 'text-growth-emerald-600'
      if (value >= 1.2) return 'text-status-warning-600'
      return 'text-status-error-600'
    }
    if (type === 'noi') {
      if (value >= 50000) return 'text-growth-emerald-600'
      if (value >= 25000) return 'text-status-warning-600'
      return 'text-status-error-600'
    }
    return 'text-neutral-slate-700'
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -8 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={cn(
        'group relative rounded-2xl overflow-hidden',
        'bg-white dark:bg-dark-bg-secondary',
        'border border-neutral-slate-200 dark:border-dark-border-primary',
        'shadow-lg hover:shadow-2xl',
        'transition-all duration-300 cursor-pointer'
      )}
    >
      {/* Property Image with Gradient Overlay */}
      <div className="relative h-48 overflow-hidden">
        {property.image ? (
          <img
            src={property.image}
            alt={property.name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          />
        ) : (
          <div className={cn(
            'w-full h-full',
            'bg-gradient-to-br from-brand-blue-400 via-accent-purple-400 to-brand-teal-400',
            'flex items-center justify-center'
          )}>
            <Home className="w-16 h-16 text-white/30" />
          </div>
        )}
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />

        {/* Status Badge */}
        <div className="absolute top-4 right-4">
          <div className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-full',
            'backdrop-blur-xl',
            statusData.bg,
            'border border-white/20'
          )}>
            <StatusIcon className={cn('w-4 h-4', statusData.text)} />
            <span className={cn('text-xs font-bold', statusData.text)}>
              {statusData.label}
            </span>
          </div>
        </div>

        {/* Property Type */}
        <div className="absolute top-4 left-4">
          <div className="px-3 py-1.5 rounded-full backdrop-blur-xl bg-white/20 border border-white/20">
            <span className="text-xs font-bold text-white">
              {property.type}
            </span>
          </div>
        </div>
      </div>

      {/* Property Info */}
      <div className="p-5 space-y-4">
        {/* Name and Address */}
        <div>
          <h3 className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-1 line-clamp-1">
            {property.name}
          </h3>
          <div className="flex items-start gap-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
            <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span className="line-clamp-2">{property.address}</span>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-3">
          {/* Occupancy */}
          <div>
            <div className="flex items-center gap-1 mb-1">
              <Users className="w-3.5 h-3.5 text-neutral-slate-400" />
              <span className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                Occupancy
              </span>
            </div>
            <p className={cn('text-lg font-bold', getMetricColor(property.occupancy, 'occupancy'))}>
              {property.occupancy}%
            </p>
          </div>

          {/* NOI */}
          <div>
            <div className="flex items-center gap-1 mb-1">
              <DollarSign className="w-3.5 h-3.5 text-neutral-slate-400" />
              <span className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                NOI
              </span>
            </div>
            <p className={cn('text-lg font-bold', getMetricColor(property.noi, 'noi'))}>
              ${(property.noi / 1000).toFixed(0)}K
            </p>
          </div>

          {/* DSCR */}
          <div>
            <div className="flex items-center gap-1 mb-1">
              <BarChart3 className="w-3.5 h-3.5 text-neutral-slate-400" />
              <span className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                DSCR
              </span>
            </div>
            <p className={cn('text-lg font-bold', getMetricColor(property.dscr, 'dscr'))}>
              {property.dscr.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Additional Metrics (Revealed on Hover) */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden space-y-2 pt-3 border-t border-neutral-slate-200 dark:border-dark-border-subtle"
            >
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-neutral-slate-600 dark:text-dark-text-secondary">Units:</span>
                  <span className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary ml-2">
                    {property.units}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-slate-600 dark:text-dark-text-secondary">Value:</span>
                  <span className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary ml-2">
                    ${(property.value / 1000000).toFixed(1)}M
                  </span>
                </div>
                <div>
                  <span className="text-neutral-slate-600 dark:text-dark-text-secondary">Built:</span>
                  <span className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary ml-2">
                    {property.yearBuilt}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-slate-600 dark:text-dark-text-secondary">Cap Rate:</span>
                  <span className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary ml-2">
                    {property.capRate}%
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation()
              onView()
              toast.info(`Viewing ${property.name}`)
            }}
            className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-brand-blue-500 hover:bg-brand-blue-600 text-white text-sm font-semibold transition-colors"
          >
            <Eye className="w-4 h-4" />
            <span>View</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation()
              onEdit()
              toast.info(`Editing ${property.name}`)
            }}
            className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-neutral-slate-100 dark:bg-dark-bg-tertiary hover:bg-neutral-slate-200 dark:hover:bg-neutral-slate-600 text-neutral-slate-700 dark:text-dark-text-primary text-sm font-semibold transition-colors"
          >
            <Edit className="w-4 h-4" />
            <span>Edit</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation()
              onAnalyze()
              toast.info(`Analyzing ${property.name}`)
            }}
            className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-accent-purple-500 hover:bg-accent-purple-600 text-white text-sm font-semibold transition-colors"
          >
            <BarChart3 className="w-4 h-4" />
            <span>Analyze</span>
          </motion.button>
        </div>
      </div>

      {/* Hover Glow Effect */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: isHovered ? '0 0 40px rgba(37, 99, 235, 0.3)' : 'none',
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
 * Generate sample property data
 */
export function generateSampleProperties(count = 12) {
  const names = [
    'Sunset Apartments', 'Ocean View Tower', 'Mountain Lodge', 'City Center Plaza',
    'Riverside Complex', 'Harbor Point', 'Garden Estates', 'Metro Square',
    'Lakeside Residence', 'Downtown Lofts', 'Parkview Condos', 'Hillside Villas'
  ]

  const addresses = [
    '123 Main St, Los Angeles, CA', '456 Ocean Ave, San Diego, CA',
    '789 Mountain Rd, Denver, CO', '321 Center Dr, Chicago, IL',
    '654 River Ln, Portland, OR', '987 Harbor Blvd, Seattle, WA',
    '147 Garden Way, Austin, TX', '258 Metro St, Boston, MA',
    '369 Lake Dr, Miami, FL', '741 Downtown Ave, NYC, NY',
    '852 Park Blvd, Phoenix, AZ', '963 Hill Rd, San Francisco, CA'
  ]

  const types = ['Residential', 'Commercial', 'Mixed-Use']
  const statuses = ['healthy', 'warning', 'critical']

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: names[i] || `Property ${i + 1}`,
    address: addresses[i] || `${i + 1} Example St, City, ST`,
    type: types[Math.floor(Math.random() * types.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    occupancy: Math.floor(Math.random() * 30) + 70, // 70-100%
    noi: Math.floor(Math.random() * 80000) + 20000, // $20K-$100K
    dscr: (Math.random() * 1.5 + 0.8).toFixed(2), // 0.8-2.3
    units: Math.floor(Math.random() * 150) + 10, // 10-160 units
    value: Math.floor(Math.random() * 8000000) + 2000000, // $2M-$10M
    yearBuilt: Math.floor(Math.random() * 40) + 1984, // 1984-2024
    capRate: (Math.random() * 4 + 4).toFixed(1), // 4%-8%
    image: null, // Placeholder, will show gradient
  }))
}

















