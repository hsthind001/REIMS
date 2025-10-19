import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Home, 
  DollarSign, 
  Users,
  Building2,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import KPIMetricCard, { generateSparklineData } from './KPIMetricCard'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { Alert } from './ui/Alert'

/**
 * REIMS KPI Dashboard
 * Displays key performance indicators with animated metrics
 */

export default function KPIDashboard() {
  // KPI Data
  const kpis = [
    {
      id: 'portfolio',
      title: 'Portfolio Value',
      value: 47800000,
      formattedValue: '$47.8M',
      trend: 'up',
      trendValue: '+12.5%',
      sparklineData: generateSparklineData(47800000, 0.08, 30),
      icon: Building2,
      type: 'portfolio',
      subtitle: 'Total Assets',
      details: {
        'Properties': '184',
        'Avg Value': '$260K',
        'YoY Growth': '+15.2%',
        'Market Cap': '$52M',
      }
    },
    {
      id: 'properties',
      title: 'Total Properties',
      value: 184,
      formattedValue: '184',
      trend: 'up',
      trendValue: '+8 units',
      sparklineData: generateSparklineData(184, 0.05, 30),
      icon: Home,
      type: 'properties',
      subtitle: 'Active Units',
      details: {
        'Residential': '142',
        'Commercial': '42',
        'Acquired This Year': '12',
        'Under Construction': '3',
      }
    },
    {
      id: 'income',
      title: 'Monthly Income',
      value: 1200000,
      formattedValue: '$1.2M',
      trend: 'up',
      trendValue: '+8.3%',
      sparklineData: generateSparklineData(1200000, 0.06, 30),
      icon: DollarSign,
      type: 'income',
      subtitle: 'Rental Revenue',
      details: {
        'Gross Revenue': '$1.4M',
        'Net Revenue': '$1.2M',
        'Expenses': '$200K',
        'Profit Margin': '85.7%',
      }
    },
    {
      id: 'occupancy',
      title: 'Occupancy Rate',
      value: 94.6,
      formattedValue: '94.6%',
      trend: 'down',
      trendValue: '-2.1%',
      sparklineData: generateSparklineData(94.6, 0.03, 30),
      icon: Users,
      type: 'occupancy',
      subtitle: 'Current Occupancy',
      details: {
        'Occupied': '174 units',
        'Vacant': '10 units',
        'Target': '96%',
        'Historical Avg': '93.2%',
      }
    }
  ]

  // Performance Summary
  const performanceMetrics = [
    { label: 'Revenue Growth', value: '+15.2%', trend: 'up', color: 'text-growth-emerald-600' },
    { label: 'ROI', value: '12.8%', trend: 'up', color: 'text-growth-emerald-600' },
    { label: 'Expenses', value: '$200K', trend: 'down', color: 'text-growth-emerald-600' },
    { label: 'Profit Margin', value: '85.7%', trend: 'up', color: 'text-growth-emerald-600' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-slate-50 via-white to-brand-blue-50 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary p-8">
      <div className="max-w-[1920px] mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-5xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent mb-2">
                KPI Dashboard
              </h1>
              <p className="text-xl text-neutral-slate-600 dark:text-dark-text-secondary">
                Real-time portfolio performance metrics
              </p>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-gradient-to-r from-brand-blue-500 to-accent-purple-500 hover:from-brand-blue-600 hover:to-accent-purple-600 text-white rounded-xl font-semibold shadow-lg flex items-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              View Full Report
            </motion.button>
          </div>
        </motion.div>

        {/* Alert Banner */}
        <Alert variant="info" title="Live Data">
          All metrics are updated in real-time and reflect the latest portfolio performance. 
          Hover over cards for detailed breakdowns.
        </Alert>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpis.map((kpi, index) => (
            <motion.div
              key={kpi.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <KPIMetricCard {...kpi} />
            </motion.div>
          ))}
        </div>

        {/* Performance Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              {performanceMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="text-center p-4 rounded-xl bg-neutral-slate-50 dark:bg-dark-bg-tertiary"
                >
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary mb-2">
                    {metric.label}
                  </p>
                  <div className="flex items-center justify-center gap-2">
                    <p className={`text-2xl font-bold ${metric.color}`}>
                      {metric.value}
                    </p>
                    {metric.trend === 'up' ? (
                      <ArrowUpRight className="w-5 h-5 text-growth-emerald-600" />
                    ) : (
                      <ArrowDownRight className="w-5 h-5 text-status-error-600" />
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Features Info */}
        <Card variant="glass">
          <CardContent className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div>
                <h3 className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2">
                  🎨 Color Coded
                </h3>
                <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  Each metric has unique gradient backgrounds and accent colors
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2">
                  📈 Sparklines
                </h3>
                <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  30-day trend visualization using Recharts
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2">
                  ✨ Animated
                </h3>
                <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  Count-up animations on load with smooth transitions
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-2">
                  💡 Interactive
                </h3>
                <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  Hover for detailed tooltips and glow effects
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Usage Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Features & Interactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-brand-blue-500 mt-2" />
                <div>
                  <h4 className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    Animated Numbers
                  </h4>
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                    Numbers count up from 0 when the card enters the viewport
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-brand-teal-500 mt-2" />
                <div>
                  <h4 className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    Trend Indicators
                  </h4>
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                    Up/down arrows with percentage change vs last month
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-growth-emerald-500 mt-2" />
                <div>
                  <h4 className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    Sparkline Charts
                  </h4>
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                    30-day historical trend with smooth line animation
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-accent-purple-500 mt-2" />
                <div>
                  <h4 className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    Hover Effects
                  </h4>
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                    Hover to see detailed breakdown tooltip and glowing border
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-status-warning-500 mt-2" />
                <div>
                  <h4 className="font-semibold text-neutral-slate-900 dark:text-dark-text-primary">
                    Background Gradients
                  </h4>
                  <p className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                    Each metric type has unique gradient: blue (portfolio), teal (properties), green (income), purple (occupancy)
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

















