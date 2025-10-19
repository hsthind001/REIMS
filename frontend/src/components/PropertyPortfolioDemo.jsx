import { useState } from 'react'
import { motion } from 'framer-motion'
import PropertyPortfolioGrid, { generateSampleProperties } from './PropertyPortfolioGrid'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { Alert } from './ui/Alert'
import { ToastProvider } from './ui/Toast'

/**
 * Property Portfolio Grid Demo
 * Showcases the property portfolio grid with sample data
 */

function DemoContent() {
  const [properties] = useState(() => generateSampleProperties(12))

  const handleViewProperty = (property) => {
    console.log('View property:', property)
  }

  const handleEditProperty = (property) => {
    console.log('Edit property:', property)
  }

  const handleAnalyzeProperty = (property) => {
    console.log('Analyze property:', property)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-slate-50 via-white to-brand-blue-50 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary p-8">
      <div className="max-w-[1920px] mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h1 className="text-5xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent">
            Property Portfolio
          </h1>
          <p className="text-xl text-neutral-slate-600 dark:text-dark-text-secondary">
            Manage and monitor your entire real estate portfolio
          </p>
        </motion.div>

        {/* Info Alert */}
        <Alert variant="info" title="Interactive Features">
          Search properties, filter by status, sort by metrics, and hover over cards to reveal additional details.
          Click action buttons to view, edit, or analyze properties.
        </Alert>

        {/* Portfolio Grid */}
        <PropertyPortfolioGrid
          properties={properties}
          onViewProperty={handleViewProperty}
          onEditProperty={handleEditProperty}
          onAnalyzeProperty={handleAnalyzeProperty}
        />

        {/* Features Info */}
        <Card>
          <CardHeader>
            <CardTitle>Features & Interactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                  Search & Filter
                </h4>
                <ul className="space-y-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  <li>• Search by property name or address</li>
                  <li>• Filter by status (healthy, warning, critical)</li>
                  <li>• Sort by name, occupancy, NOI, or DSCR</li>
                  <li>• Real-time results update</li>
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                  Property Cards
                </h4>
                <ul className="space-y-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  <li>• Gradient overlays on images</li>
                  <li>• Status badges (color-coded)</li>
                  <li>• Key metrics (occupancy, NOI, DSCR)</li>
                  <li>• Hover to reveal additional metrics</li>
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                  Color Coding
                </h4>
                <ul className="space-y-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  <li>• 🟢 Green: Excellent performance</li>
                  <li>• 🟡 Yellow: Needs attention</li>
                  <li>• 🔴 Red: Critical issues</li>
                  <li>• Applies to all key metrics</li>
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                  Quick Actions
                </h4>
                <ul className="space-y-2 text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
                  <li>• 👁️ View: See full property details</li>
                  <li>• ✏️ Edit: Modify property information</li>
                  <li>• 📊 Analyze: AI-powered insights</li>
                  <li>• Toast notifications for feedback</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Metric Guidelines */}
        <Card variant="blue">
          <CardContent className="p-6">
            <h3 className="text-lg font-bold text-neutral-slate-900 mb-4">
              Metric Thresholds
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-semibold text-neutral-slate-700 mb-2">
                  Occupancy Rate
                </h4>
                <ul className="space-y-1 text-sm text-neutral-slate-600">
                  <li>🟢 ≥95%: Excellent</li>
                  <li>🟡 85-94%: Good</li>
                  <li>🔴 &lt;85%: Needs Attention</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-neutral-slate-700 mb-2">
                  Net Operating Income (NOI)
                </h4>
                <ul className="space-y-1 text-sm text-neutral-slate-600">
                  <li>🟢 ≥$50K: Strong</li>
                  <li>🟡 $25K-$50K: Moderate</li>
                  <li>🔴 &lt;$25K: Weak</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-neutral-slate-700 mb-2">
                  Debt Service Coverage Ratio (DSCR)
                </h4>
                <ul className="space-y-1 text-sm text-neutral-slate-600">
                  <li>🟢 ≥1.5: Excellent</li>
                  <li>🟡 1.2-1.49: Adequate</li>
                  <li>🔴 &lt;1.2: At Risk</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function PropertyPortfolioDemo() {
  return (
    <ToastProvider>
      <DemoContent />
    </ToastProvider>
  )
}

















