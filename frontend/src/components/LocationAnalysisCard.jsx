import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Users, 
  Briefcase, 
  Building2, 
  FileText,
  TrendingUp,
  TrendingDown,
  ExternalLink,
  MapPin,
  DollarSign,
  Calendar,
  ArrowRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * REIMS Location Analysis Card
 * 
 * Market intelligence display with:
 * - Demographics (population, median income, age distribution)
 * - Employment (unemployment rate, major employers)
 * - New Developments (recent projects in area)
 * - Political/Zoning changes (recent updates)
 * 
 * Features:
 * - Animated colorful icons
 * - Gradient backgrounds
 * - Key metrics with trend indicators
 * - Last update timestamps
 * - "Learn more" links to detailed views
 */

export default function LocationAnalysisCard({ location = 'Empire State Plaza District', className }) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 rounded-xl bg-gradient-to-br from-brand-blue-500 to-accent-purple-500">
          <MapPin className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-black text-neutral-slate-900 dark:text-dark-text-primary">
            Location Analysis
          </h2>
          <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
            Market intelligence for {location}
          </p>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <DemographicsCard />
        <EmploymentCard />
        <NewDevelopmentsCard />
        <PoliticalZoningCard />
      </div>
    </div>
  )
}

/**
 * Demographics Card
 */
function DemographicsCard() {
  const [isHovered, setIsHovered] = useState(false)
  
  const data = {
    population: 125487,
    populationTrend: 'up',
    populationChange: '+3.2%',
    medianIncome: 78500,
    incomeTrend: 'up',
    incomeChange: '+5.8%',
    medianAge: 34.2,
    ageTrend: 'neutral',
    ageChange: '+0.3',
    lastUpdated: '2 days ago'
  }

  return (
    <IntelligenceCard
      icon={Users}
      title="Demographics"
      gradient="from-brand-blue-500 via-accent-indigo-500 to-accent-purple-500"
      glowColor="rgba(99, 102, 241, 0.3)"
      lastUpdated={data.lastUpdated}
      isHovered={isHovered}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <div className="space-y-4">
        {/* Population */}
        <MetricRow
          label="Population"
          value={data.population.toLocaleString()}
          trend={data.populationTrend}
          change={data.populationChange}
          icon="👥"
        />

        {/* Median Income */}
        <MetricRow
          label="Median Income"
          value={`$${(data.medianIncome / 1000).toFixed(0)}K`}
          trend={data.incomeTrend}
          change={data.incomeChange}
          icon="💰"
        />

        {/* Median Age */}
        <MetricRow
          label="Median Age"
          value={`${data.medianAge} years`}
          trend={data.ageTrend}
          change={data.ageChange}
          icon="🎂"
        />

        {/* Age Distribution Quick Stats */}
        <div className="pt-2 border-t border-neutral-slate-200 dark:border-dark-border-primary">
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className="font-bold text-brand-blue-600 dark:text-brand-blue-400">28%</div>
              <div className="text-neutral-slate-600 dark:text-dark-text-secondary">18-29</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-brand-blue-600 dark:text-brand-blue-400">42%</div>
              <div className="text-neutral-slate-600 dark:text-dark-text-secondary">30-49</div>
            </div>
            <div className="text-center">
              <div className="font-bold text-brand-blue-600 dark:text-brand-blue-400">30%</div>
              <div className="text-neutral-slate-600 dark:text-dark-text-secondary">50+</div>
            </div>
          </div>
        </div>
      </div>
    </IntelligenceCard>
  )
}

/**
 * Employment Card
 */
function EmploymentCard() {
  const [isHovered, setIsHovered] = useState(false)
  
  const data = {
    unemploymentRate: 3.8,
    unemploymentTrend: 'down',
    unemploymentChange: '-0.4%',
    laborForce: 68542,
    lastUpdated: '1 week ago'
  }

  const majorEmployers = [
    { name: 'Tech Corp', employees: '2,500+', sector: '💻 Technology' },
    { name: 'General Hospital', employees: '1,800+', sector: '🏥 Healthcare' },
    { name: 'State University', employees: '1,200+', sector: '🎓 Education' },
  ]

  return (
    <IntelligenceCard
      icon={Briefcase}
      title="Employment"
      gradient="from-growth-emerald-500 via-growth-lime-500 to-brand-teal-500"
      glowColor="rgba(16, 185, 129, 0.3)"
      lastUpdated={data.lastUpdated}
      isHovered={isHovered}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <div className="space-y-4">
        {/* Unemployment Rate */}
        <MetricRow
          label="Unemployment Rate"
          value={`${data.unemploymentRate}%`}
          trend={data.unemploymentTrend}
          change={data.unemploymentChange}
          icon="📊"
        />

        {/* Labor Force */}
        <MetricRow
          label="Labor Force"
          value={data.laborForce.toLocaleString()}
          trend="neutral"
          change="—"
          icon="👔"
        />

        {/* Major Employers */}
        <div className="pt-2 border-t border-neutral-slate-200 dark:border-dark-border-primary">
          <h4 className="text-xs font-bold text-neutral-slate-600 dark:text-dark-text-secondary mb-2 uppercase tracking-wider">
            Major Employers
          </h4>
          <div className="space-y-2">
            {majorEmployers.map((employer, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between text-xs"
              >
                <div className="flex-1">
                  <div className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    {employer.name}
                  </div>
                  <div className="text-neutral-slate-500 dark:text-dark-text-secondary">
                    {employer.sector}
                  </div>
                </div>
                <div className="font-bold text-growth-emerald-600 dark:text-growth-emerald-400">
                  {employer.employees}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </IntelligenceCard>
  )
}

/**
 * New Developments Card
 */
function NewDevelopmentsCard() {
  const [isHovered, setIsHovered] = useState(false)
  
  const data = {
    totalProjects: 12,
    projectsTrend: 'up',
    projectsChange: '+4',
    totalInvestment: 285000000,
    lastUpdated: '3 days ago'
  }

  const recentProjects = [
    { name: 'Skyline Tower', type: 'Mixed-Use', status: 'Under Construction', value: '$95M' },
    { name: 'Harbor Walk', type: 'Residential', status: 'Planning', value: '$68M' },
    { name: 'Innovation Hub', type: 'Office', status: 'Approved', value: '$52M' },
  ]

  return (
    <IntelligenceCard
      icon={Building2}
      title="New Developments"
      gradient="from-accent-purple-500 via-accent-violet-500 to-accent-indigo-500"
      glowColor="rgba(139, 92, 246, 0.3)"
      lastUpdated={data.lastUpdated}
      isHovered={isHovered}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <div className="space-y-4">
        {/* Total Projects */}
        <MetricRow
          label="Active Projects"
          value={data.totalProjects.toString()}
          trend={data.projectsTrend}
          change={data.projectsChange}
          icon="🏗️"
        />

        {/* Total Investment */}
        <MetricRow
          label="Total Investment"
          value={`$${(data.totalInvestment / 1000000).toFixed(0)}M`}
          trend="up"
          change="+12.3%"
          icon="💼"
        />

        {/* Recent Projects */}
        <div className="pt-2 border-t border-neutral-slate-200 dark:border-dark-border-primary">
          <h4 className="text-xs font-bold text-neutral-slate-600 dark:text-dark-text-secondary mb-2 uppercase tracking-wider">
            Recent Projects
          </h4>
          <div className="space-y-2">
            {recentProjects.map((project, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-2 rounded-lg bg-neutral-slate-50 dark:bg-dark-bg-tertiary"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-xs text-neutral-slate-900 dark:text-dark-text-primary">
                      {project.name}
                    </div>
                    <div className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary">
                      {project.type} • {project.status}
                    </div>
                  </div>
                  <div className="font-bold text-xs text-accent-purple-600 dark:text-accent-purple-400">
                    {project.value}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </IntelligenceCard>
  )
}

/**
 * Political/Zoning Card
 */
function PoliticalZoningCard() {
  const [isHovered, setIsHovered] = useState(false)
  
  const data = {
    recentChanges: 5,
    changesTrend: 'up',
    changesChange: '+2',
    lastUpdated: '5 days ago'
  }

  const recentUpdates = [
    { 
      title: 'Mixed-Use Zoning Expansion', 
      date: 'Oct 8, 2025', 
      impact: 'High',
      description: 'Allows residential + commercial development'
    },
    { 
      title: 'Height Restriction Update', 
      date: 'Oct 5, 2025', 
      impact: 'Medium',
      description: 'Increased from 150ft to 200ft in downtown'
    },
    { 
      title: 'Tax Incentive Program', 
      date: 'Oct 1, 2025', 
      impact: 'High',
      description: 'New 10-year tax abatement for green buildings'
    },
  ]

  return (
    <IntelligenceCard
      icon={FileText}
      title="Political & Zoning"
      gradient="from-status-warning-500 via-accent-orange-500 to-accent-amber-500"
      glowColor="rgba(245, 158, 11, 0.3)"
      lastUpdated={data.lastUpdated}
      isHovered={isHovered}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <div className="space-y-4">
        {/* Recent Changes */}
        <MetricRow
          label="Recent Changes"
          value={`${data.recentChanges} updates`}
          trend={data.changesTrend}
          change={data.changesChange}
          icon="📋"
        />

        {/* Recent Updates */}
        <div className="pt-2 border-t border-neutral-slate-200 dark:border-dark-border-primary">
          <h4 className="text-xs font-bold text-neutral-slate-600 dark:text-dark-text-secondary mb-2 uppercase tracking-wider">
            Latest Updates
          </h4>
          <div className="space-y-2">
            {recentUpdates.map((update, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-2 rounded-lg bg-neutral-slate-50 dark:bg-dark-bg-tertiary"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="font-semibold text-xs text-neutral-slate-900 dark:text-dark-text-primary mb-0.5">
                      {update.title}
                    </div>
                    <div className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary mb-1">
                      {update.description}
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <Calendar className="w-3 h-3 text-neutral-slate-400" />
                      <span className="text-neutral-slate-600 dark:text-dark-text-secondary">
                        {update.date}
                      </span>
                    </div>
                  </div>
                  <span className={cn(
                    'px-2 py-0.5 rounded text-xs font-bold whitespace-nowrap',
                    update.impact === 'High' 
                      ? 'bg-status-error-100 text-status-error-700 dark:bg-status-error-900/30 dark:text-status-error-400'
                      : 'bg-status-warning-100 text-status-warning-700 dark:bg-status-warning-900/30 dark:text-status-warning-400'
                  )}>
                    {update.impact}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </IntelligenceCard>
  )
}

/**
 * Base Intelligence Card Component
 */
function IntelligenceCard({ 
  icon: Icon, 
  title, 
  gradient, 
  glowColor, 
  lastUpdated, 
  children, 
  isHovered,
  onHoverStart,
  onHoverEnd
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -6, transition: { duration: 0.3 } }}
      onHoverStart={onHoverStart}
      onHoverEnd={onHoverEnd}
      className="relative overflow-hidden rounded-2xl bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary shadow-lg hover:shadow-2xl transition-all duration-300 group cursor-pointer"
    >
      {/* Background Gradient */}
      <div className={cn(
        'absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500',
        `bg-gradient-to-br ${gradient}`
      )} />

      {/* Animated Glow Effect */}
      <motion.div
        className="absolute -top-24 -right-24 w-48 h-48 rounded-full blur-3xl"
        style={{ backgroundColor: glowColor }}
        animate={{
          scale: isHovered ? [1, 1.3, 1] : 1,
          opacity: isHovered ? [0.2, 0.4, 0.2] : 0.1,
        }}
        transition={{ duration: 3, repeat: Infinity }}
      />

      {/* Content */}
      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <motion.div
              className={cn(
                'p-3 rounded-xl bg-gradient-to-br',
                gradient
              )}
              animate={{
                rotate: isHovered ? [0, 5, -5, 0] : 0,
              }}
              transition={{ duration: 0.5 }}
            >
              <Icon className="w-5 h-5 text-white" />
            </motion.div>
            <div>
              <h3 className="text-lg font-black text-neutral-slate-900 dark:text-dark-text-primary">
                {title}
              </h3>
              <p className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Updated {lastUpdated}
              </p>
            </div>
          </div>
        </div>

        {/* Card Content */}
        {children}

        {/* Learn More Link */}
        <motion.button
          whileHover={{ x: 5 }}
          className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r text-white font-semibold text-sm shadow-md hover:shadow-lg transition-all duration-300"
          style={{ backgroundImage: `linear-gradient(to right, ${gradient.split(' ').slice(1).join(' ')})` }}
        >
          <span>Learn more</span>
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </div>

      {/* Border Glow on Hover */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: isHovered ? `0 0 40px ${glowColor}` : 'none',
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
 * Metric Row Component
 */
function MetricRow({ label, value, trend, change, icon }) {
  const trendConfig = {
    up: {
      icon: TrendingUp,
      color: 'text-growth-emerald-600 dark:text-growth-emerald-400',
      bg: 'bg-growth-emerald-100 dark:bg-growth-emerald-900/30',
    },
    down: {
      icon: TrendingDown,
      color: 'text-status-error-600 dark:text-status-error-400',
      bg: 'bg-status-error-100 dark:bg-status-error-900/30',
    },
    neutral: {
      icon: null,
      color: 'text-neutral-slate-600 dark:text-neutral-slate-400',
      bg: 'bg-neutral-slate-100 dark:bg-neutral-slate-800/30',
    },
  }

  const config = trendConfig[trend]
  const TrendIcon = config.icon

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-lg">{icon}</span>
        <div>
          <div className="text-sm font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
            {label}
          </div>
          <div className="text-xs text-neutral-slate-500 dark:text-dark-text-secondary">
            {value}
          </div>
        </div>
      </div>
      <div className={cn(
        'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold',
        config.bg,
        config.color
      )}>
        {TrendIcon && <TrendIcon className="w-3 h-3" />}
        <span>{change}</span>
      </div>
    </div>
  )
}













