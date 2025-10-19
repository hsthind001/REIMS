import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Building2, 
  TrendingUp, 
  DollarSign, 
  Users,
  ShoppingBag,
  Coffee,
  Utensils,
  Dumbbell,
  Briefcase,
  Sparkles,
  CheckCircle2,
  UserPlus,
  PieChart as PieChartIcon,
  Square
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { cn } from '@/lib/utils'

/**
 * REIMS AI Tenant Recommendations Component
 * 
 * Features:
 * - Available square footage display
 * - Current tenant mix pie chart
 * - 3-5 AI-powered business recommendations
 * - Synergy scores with progress bars
 * - Add to prospects functionality
 */

export default function TenantRecommendations({ propertyId = 1, className }) {
  const [addedProspects, setAddedProspects] = useState([])

  // Property data
  const propertyData = {
    name: 'Empire State Plaza',
    totalSqFt: 1000000, // Large commercial property
    occupiedSqFt: 950000, // 95% occupancy
    vacantSqFt: 50000,
    vacancyRate: 5.0, // 5% vacancy rate
  }

  // Current tenant mix data
  const tenantMixData = [
    { category: 'Retail', sqft: 15000, percentage: 38.96, color: '#3b82f6' }, // blue
    { category: 'Dining', sqft: 12000, percentage: 31.17, color: '#10b981' }, // green
    { category: 'Services', sqft: 8500, percentage: 22.08, color: '#8b5cf6' }, // purple
    { category: 'Office', sqft: 3000, percentage: 7.79, color: '#f59e0b' }, // orange
  ]

  // AI-powered recommendations
  const recommendations = [
    {
      id: 1,
      businessType: 'Premium Fitness Studio',
      icon: Dumbbell,
      synergyScore: 92,
      rentRange: '$45-$55/sqft',
      sqftNeeded: '3,500-5,000',
      whySucceed: [
        'High-income demographic within 1-mile radius',
        'No competing gyms in immediate area',
        'Synergy with health-focused restaurants',
        'Morning & evening traffic patterns ideal'
      ],
      demographics: {
        targetAge: '25-45',
        income: '$75K+',
        interests: 'Health & Wellness'
      },
      gradient: 'from-growth-emerald-500 to-brand-teal-600',
      glowColor: 'rgba(16, 185, 129, 0.3)'
    },
    {
      id: 2,
      businessType: 'Artisan Coffee & Co-Working',
      icon: Coffee,
      synergyScore: 88,
      rentRange: '$38-$48/sqft',
      sqftNeeded: '2,500-3,500',
      whySucceed: [
        'Complements existing office tenants',
        'Remote workers in area need spaces',
        'Morning traffic from surrounding offices',
        'Instagram-worthy location drives foot traffic'
      ],
      demographics: {
        targetAge: '22-40',
        income: '$50K+',
        interests: 'Tech & Creativity'
      },
      gradient: 'from-accent-amber-500 to-accent-orange-600',
      glowColor: 'rgba(245, 158, 11, 0.3)'
    },
    {
      id: 3,
      businessType: 'Upscale Fast-Casual Restaurant',
      icon: Utensils,
      synergyScore: 85,
      rentRange: '$42-$52/sqft',
      sqftNeeded: '2,000-3,000',
      whySucceed: [
        'Gap in lunch options for office workers',
        'Evening dining destination for residents',
        'Patio space available for outdoor seating',
        'High visibility from main street'
      ],
      demographics: {
        targetAge: '25-55',
        income: '$60K+',
        interests: 'Dining & Social'
      },
      gradient: 'from-status-error-500 to-accent-rose-600',
      glowColor: 'rgba(239, 68, 68, 0.3)'
    },
    {
      id: 4,
      businessType: 'Boutique Retail Concept',
      icon: ShoppingBag,
      synergyScore: 82,
      rentRange: '$40-$50/sqft',
      sqftNeeded: '1,500-2,500',
      whySucceed: [
        'Affluent residential area nearby',
        'Low competition for unique goods',
        'Cross-promotion with dining tenants',
        'Strong weekend foot traffic'
      ],
      demographics: {
        targetAge: '28-50',
        income: '$70K+',
        interests: 'Fashion & Lifestyle'
      },
      gradient: 'from-accent-purple-500 to-accent-violet-600',
      glowColor: 'rgba(139, 92, 246, 0.3)'
    },
    {
      id: 5,
      businessType: 'Professional Services Hub',
      icon: Briefcase,
      synergyScore: 78,
      rentRange: '$35-$45/sqft',
      sqftNeeded: '2,000-3,000',
      whySucceed: [
        'Established business district location',
        'Parking availability for clients',
        'Professional atmosphere of property',
        'Networking opportunities with other tenants'
      ],
      demographics: {
        targetAge: '30-60',
        income: '$80K+',
        interests: 'Business Services'
      },
      gradient: 'from-brand-blue-500 to-accent-indigo-600',
      glowColor: 'rgba(37, 99, 235, 0.3)'
    }
  ]

  const handleAddProspect = (recommendationId) => {
    if (!addedProspects.includes(recommendationId)) {
      setAddedProspects([...addedProspects, recommendationId])
      // In real app, this would call an API to add to CRM
      console.log(`Added prospect: ${recommendationId}`)
    }
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 rounded-xl bg-gradient-to-br from-accent-purple-500 to-brand-blue-500">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-black text-neutral-slate-900 dark:text-dark-text-primary">
            AI Tenant Recommendations
          </h2>
          <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
            Intelligent tenant matching for {propertyData.name}
          </p>
        </div>
      </div>

      {/* Property Overview & Tenant Mix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Available Space Card */}
        <AvailableSpaceCard data={propertyData} />

        {/* Current Tenant Mix Card */}
        <TenantMixCard data={tenantMixData} />
      </div>

      {/* Recommendations Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-accent-purple-600" />
          <h3 className="text-xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Recommended Business Types
          </h3>
          <span className="px-2 py-1 rounded-full bg-accent-purple-100 dark:bg-accent-purple-900/30 text-accent-purple-700 dark:text-accent-purple-400 text-xs font-bold">
            AI Powered
          </span>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {recommendations.map((recommendation, index) => (
            <RecommendationCard
              key={recommendation.id}
              recommendation={recommendation}
              index={index}
              isAdded={addedProspects.includes(recommendation.id)}
              onAddProspect={handleAddProspect}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

/**
 * Available Space Card
 */
function AvailableSpaceCard({ data }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-2xl bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary shadow-lg p-6"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand-blue-500/5 to-accent-purple-500/5" />

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-gradient-to-br from-brand-blue-500 to-accent-purple-500">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-lg font-black text-neutral-slate-900 dark:text-dark-text-primary">
            Available Space
          </h3>
        </div>

        {/* Metrics */}
        <div className="space-y-4">
          {/* Total Space */}
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
              Total Square Footage
            </span>
            <span className="text-2xl font-black text-neutral-slate-900 dark:text-dark-text-primary">
              {data.totalSqFt.toLocaleString()}
            </span>
          </div>

          {/* Occupied */}
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
              Occupied
            </span>
            <span className="text-xl font-bold text-growth-emerald-600 dark:text-growth-emerald-400">
              {data.occupiedSqFt.toLocaleString()} sqft
            </span>
          </div>

          {/* Vacant */}
          <div className="flex items-baseline justify-between p-3 rounded-xl bg-status-warning-50 dark:bg-status-warning-900/20 border border-status-warning-200 dark:border-status-warning-800">
            <span className="text-sm font-semibold text-status-warning-700 dark:text-status-warning-400">
              💡 Available for Lease
            </span>
            <span className="text-2xl font-black text-status-warning-700 dark:text-status-warning-400">
              {data.vacantSqFt.toLocaleString()} sqft
            </span>
          </div>

          {/* Vacancy Rate */}
          <div className="pt-3 border-t border-neutral-slate-200 dark:border-dark-border-primary">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                Vacancy Rate
              </span>
              <span className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary">
                {data.vacancyRate}%
              </span>
            </div>
            <div className="w-full h-2 bg-neutral-slate-200 dark:bg-neutral-slate-700 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${data.vacancyRate}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-status-warning-500 to-status-warning-600"
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Tenant Mix Pie Chart Card
 */
function TenantMixCard({ data }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="relative overflow-hidden rounded-2xl bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary shadow-lg p-6"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-growth-emerald-500/5 to-brand-teal-500/5" />

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-gradient-to-br from-growth-emerald-500 to-brand-teal-500">
            <PieChartIcon className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-lg font-black text-neutral-slate-900 dark:text-dark-text-primary">
            Current Tenant Mix
          </h3>
        </div>

        {/* Pie Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="sqft"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={80}
                innerRadius={50}
                paddingAngle={2}
                animationBegin={0}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-white dark:bg-dark-bg-tertiary border border-neutral-slate-200 dark:border-dark-border-primary rounded-lg p-3 shadow-lg">
                        <p className="font-bold text-neutral-slate-900 dark:text-dark-text-primary">
                          {payload[0].name}
                        </p>
                        <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                          {payload[0].value.toLocaleString()} sqft ({payload[0].payload.percentage.toFixed(1)}%)
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-2 mt-4">
          {data.map((item) => (
            <div key={item.category} className="flex items-center gap-2">
              <Square className="w-4 h-4" style={{ fill: item.color, stroke: item.color }} />
              <div className="flex-1">
                <div className="text-xs font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                  {item.category}
                </div>
                <div className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary">
                  {item.percentage.toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Recommendation Card
 */
function RecommendationCard({ recommendation, index, isAdded, onAddProspect }) {
  const [isHovered, setIsHovered] = useState(false)
  const Icon = recommendation.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -4 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="relative overflow-hidden rounded-2xl bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary shadow-lg hover:shadow-2xl transition-all duration-300 group"
    >
      {/* Background gradient */}
      <div className={cn(
        'absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500',
        `bg-gradient-to-br ${recommendation.gradient}`
      )} />

      {/* Animated glow */}
      <motion.div
        className="absolute -top-24 -right-24 w-48 h-48 rounded-full blur-3xl"
        style={{ backgroundColor: recommendation.glowColor }}
        animate={{
          scale: isHovered ? [1, 1.3, 1] : 1,
          opacity: isHovered ? [0.2, 0.4, 0.2] : 0.1,
        }}
        transition={{ duration: 3, repeat: Infinity }}
      />

      {/* Content */}
      <div className="relative z-10 p-6">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <motion.div
            className={cn(
              'p-4 rounded-xl bg-gradient-to-br shrink-0',
              recommendation.gradient
            )}
            animate={{
              rotate: isHovered ? [0, 5, -5, 0] : 0,
            }}
            transition={{ duration: 0.5 }}
          >
            <Icon className="w-8 h-8 text-white" />
          </motion.div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <h4 className="text-xl font-black text-neutral-slate-900 dark:text-dark-text-primary mb-1">
                  {recommendation.businessType}
                </h4>
                <div className="flex flex-wrap items-center gap-2 text-sm">
                  <span className="flex items-center gap-1 text-neutral-slate-600 dark:text-dark-text-secondary">
                    <Square className="w-3 h-3" />
                    {recommendation.sqftNeeded} sqft
                  </span>
                  <span className="text-neutral-slate-400">•</span>
                  <span className="flex items-center gap-1 text-growth-emerald-600 dark:text-growth-emerald-400 font-semibold">
                    <DollarSign className="w-3 h-3" />
                    {recommendation.rentRange}
                  </span>
                </div>
              </div>

              {/* Synergy Score Badge */}
              <div className="text-center shrink-0">
                <div className="text-3xl font-black text-accent-purple-600 dark:text-accent-purple-400">
                  {recommendation.synergyScore}
                </div>
                <div className="text-xs text-neutral-slate-600 dark:text-dark-text-secondary uppercase tracking-wider">
                  Synergy
                </div>
              </div>
            </div>

            {/* Synergy Progress Bar */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-neutral-slate-600 dark:text-dark-text-secondary uppercase tracking-wider">
                  Tenant Synergy Score
                </span>
                <span className="text-xs font-bold text-accent-purple-600 dark:text-accent-purple-400">
                  {recommendation.synergyScore}/100
                </span>
              </div>
              <div className="w-full h-3 bg-neutral-slate-200 dark:bg-neutral-slate-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${recommendation.synergyScore}%` }}
                  transition={{ duration: 1, delay: index * 0.1 + 0.3, ease: 'easeOut' }}
                  className={cn(
                    'h-full bg-gradient-to-r relative',
                    recommendation.gradient
                  )}
                >
                  <motion.div
                    className="absolute inset-0 bg-white/30"
                    animate={{
                      x: ['-100%', '100%'],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                  />
                </motion.div>
              </div>
            </div>

            {/* Why They'll Succeed */}
            <div className="mb-4">
              <h5 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-growth-emerald-600" />
                Why They'll Succeed Here
              </h5>
              <ul className="space-y-1.5">
                {recommendation.whySucceed.map((reason, idx) => (
                  <motion.li
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 + idx * 0.05 }}
                    className="flex items-start gap-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary"
                  >
                    <CheckCircle2 className="w-4 h-4 text-growth-emerald-600 dark:text-growth-emerald-400 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </motion.li>
                ))}
              </ul>
            </div>

            {/* Target Demographics */}
            <div className="mb-4 p-3 rounded-xl bg-neutral-slate-50 dark:bg-dark-bg-tertiary">
              <h5 className="text-xs font-bold text-neutral-slate-600 dark:text-dark-text-secondary mb-2 uppercase tracking-wider flex items-center gap-1">
                <Users className="w-3 h-3" />
                Target Demographics
              </h5>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 rounded-full bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary text-xs font-semibold text-neutral-slate-700 dark:text-dark-text-primary">
                  {recommendation.demographics.targetAge}
                </span>
                <span className="px-2 py-1 rounded-full bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary text-xs font-semibold text-neutral-slate-700 dark:text-dark-text-primary">
                  {recommendation.demographics.income}
                </span>
                <span className="px-2 py-1 rounded-full bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary text-xs font-semibold text-neutral-slate-700 dark:text-dark-text-primary">
                  {recommendation.demographics.interests}
                </span>
              </div>
            </div>

            {/* Add to Prospects Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onAddProspect(recommendation.id)}
              disabled={isAdded}
              className={cn(
                'w-full py-3 px-4 rounded-xl font-bold text-sm shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2',
                isAdded
                  ? 'bg-growth-emerald-100 dark:bg-growth-emerald-900/30 text-growth-emerald-700 dark:text-growth-emerald-400 cursor-not-allowed'
                  : `bg-gradient-to-r text-white ${recommendation.gradient}`
              )}
            >
              {isAdded ? (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  <span>Added to Prospects</span>
                </>
              ) : (
                <>
                  <UserPlus className="w-5 h-5" />
                  <span>Add to Prospects</span>
                </>
              )}
            </motion.button>
          </div>
        </div>
      </div>

      {/* Border glow on hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: isHovered ? `0 0 40px ${recommendation.glowColor}` : 'none',
        }}
        animate={{
          opacity: isHovered ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  )
}













