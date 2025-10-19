import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Home,
  FileText,
  BarChart3
} from 'lucide-react'
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter,
  GradientCard 
} from './ui/Card'
import { MetricCard, CompactMetricCard } from './ui/MetricCard'
import { Alert, InlineAlert } from './ui/Alert'
import { DataTable } from './ui/DataTable'
import { 
  Skeleton, 
  SkeletonCard, 
  SkeletonMetricCard, 
  SkeletonTable,
  SkeletonDashboard 
} from './ui/Skeleton'
import { useToast } from './ui/Toast'

/**
 * Component Showcase
 * Interactive demo of all REIMS UI components
 */

export default function ComponentShowcase() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  // Sample data for table
  const sampleData = [
    { id: 1, property: 'Sunset Apartments', location: 'Los Angeles', value: '$2.4M', occupancy: '94%', status: 'Active' },
    { id: 2, property: 'Ocean View Tower', location: 'San Diego', value: '$5.2M', occupancy: '87%', status: 'Active' },
    { id: 3, property: 'Mountain Lodge', location: 'Denver', value: '$1.8M', occupancy: '92%', status: 'Pending' },
    { id: 4, property: 'City Center Plaza', location: 'Chicago', value: '$3.9M', occupancy: '96%', status: 'Active' },
    { id: 5, property: 'Riverside Complex', location: 'Portland', value: '$2.1M', occupancy: '89%', status: 'Active' },
  ]

  const columns = [
    { key: 'property', header: 'Property', sortable: true },
    { key: 'location', header: 'Location', sortable: true },
    { 
      key: 'value', 
      header: 'Value', 
      sortable: true,
      render: (value) => <span className="font-bold text-brand-blue-600">{value}</span>
    },
    { key: 'occupancy', header: 'Occupancy', sortable: true },
    { 
      key: 'status', 
      header: 'Status',
      render: (value) => (
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
          value === 'Active' 
            ? 'bg-status-success-100 text-status-success-700' 
            : 'bg-status-warning-100 text-status-warning-700'
        }`}>
          {value}
        </span>
      )
    },
  ]

  const simulateLoading = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 3000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-slate-50 to-brand-blue-50 dark:from-dark-bg-primary dark:to-dark-bg-secondary p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <h1 className="text-5xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent">
            REIMS Component Library
          </h1>
          <p className="text-xl text-neutral-slate-600 dark:text-dark-text-secondary">
            Beautiful, colorful, and highly functional UI components
          </p>
        </motion.div>

        {/* Cards Section */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Card Components
          </h2>
          
          <div className="grid grid-cols-3 gap-6">
            <Card variant="default">
              <CardHeader>
                <CardTitle>Default Card</CardTitle>
                <CardDescription>Clean and professional</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-neutral-slate-600 dark:text-dark-text-secondary">
                  Perfect for standard content and information display.
                </p>
              </CardContent>
              <CardFooter>
                <button className="w-full bg-brand-blue-500 hover:bg-brand-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                  Learn More
                </button>
              </CardFooter>
            </Card>

            <Card variant="blue">
              <CardHeader>
                <CardTitle>Blue Gradient</CardTitle>
                <CardDescription>Brand colors</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-neutral-slate-600">
                  Subtle gradient using brand blue and teal colors.
                </p>
              </CardContent>
            </Card>

            <Card variant="purple">
              <CardHeader>
                <CardTitle>Purple Gradient</CardTitle>
                <CardDescription>For AI features</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-neutral-slate-600">
                  Highlights AI-powered and premium features.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <GradientCard gradient="brand">
              <CardHeader>
                <CardTitle className="text-white">Brand Gradient</CardTitle>
                <CardDescription className="text-white/80">Blue to teal</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-white/90">
                  Bold gradient cards for important features and call-to-actions.
                </p>
              </CardContent>
            </GradientCard>

            <GradientCard gradient="ai">
              <CardHeader>
                <CardTitle className="text-white">AI Gradient</CardTitle>
                <CardDescription className="text-white/80">Purple to indigo</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-white/90">
                  Perfect for showcasing AI and machine learning features.
                </p>
              </CardContent>
            </GradientCard>
          </div>
        </section>

        {/* Metric Cards Section */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Metric/KPI Cards
          </h2>
          
          <div className="grid grid-cols-4 gap-6">
            <MetricCard
              title="Total Properties"
              value="184"
              change="+12.5%"
              trend="up"
              icon={Home}
              variant="default"
            />

            <MetricCard
              title="Monthly Revenue"
              value="$1.2M"
              change="+8.3%"
              trend="up"
              icon={DollarSign}
              variant="success"
            />

            <MetricCard
              title="Occupancy Rate"
              value="94.6%"
              change="-2.1%"
              trend="down"
              icon={Users}
              variant="warning"
            />

            <MetricCard
              title="Documents"
              value="1,234"
              change="0%"
              trend="neutral"
              icon={FileText}
              variant="purple"
            />
          </div>

          {/* Compact Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <CompactMetricCard
              title="Active Properties"
              value="174"
              icon={Home}
              color="blue"
            />
            <CompactMetricCard
              title="Total Revenue"
              value="$5.2M"
              icon={DollarSign}
              color="success"
            />
            <CompactMetricCard
              title="AI Insights"
              value="42"
              icon={BarChart3}
              color="purple"
            />
            <CompactMetricCard
              title="Occupancy"
              value="94.6%"
              icon={TrendingUp}
              color="teal"
            />
          </div>
        </section>

        {/* Alerts Section */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Alert Components
          </h2>
          
          <div className="space-y-4">
            <Alert
              variant="success"
              title="Success!"
              dismissible
            >
              Your document has been uploaded and processed successfully.
            </Alert>

            <Alert
              variant="warning"
              title="Attention Required"
              dismissible
            >
              Please review the pending property approval requests.
            </Alert>

            <Alert
              variant="error"
              title="Error Occurred"
              dismissible
            >
              Failed to connect to the database. Please try again later.
            </Alert>

            <Alert
              variant="info"
              title="Information"
              dismissible
            >
              New AI features are now available in your dashboard.
            </Alert>

            <Alert
              variant="critical"
              title="Critical Alert"
              dismissible
            >
              System maintenance scheduled for tonight at 2:00 AM UTC.
            </Alert>
          </div>

          {/* Inline Alerts */}
          <div className="grid grid-cols-2 gap-4">
            <InlineAlert variant="success">Document saved successfully</InlineAlert>
            <InlineAlert variant="warning">Changes are not saved</InlineAlert>
            <InlineAlert variant="error">Invalid input format</InlineAlert>
            <InlineAlert variant="info">Pro tip: Use keyboard shortcuts</InlineAlert>
          </div>
        </section>

        {/* Data Table Section */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Data Table
          </h2>
          
          <DataTable
            data={sampleData}
            columns={columns}
            sortable
            searchable
            filterable
            exportable
            onRowClick={(row) => toast.info(`Clicked: ${row.property}`)}
          />
        </section>

        {/* Skeleton Loaders Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
              Skeleton Loaders
            </h2>
            <button
              onClick={simulateLoading}
              className="px-6 py-2 bg-brand-blue-500 hover:bg-brand-blue-600 text-white rounded-lg font-semibold transition-colors"
            >
              Simulate Loading
            </button>
          </div>
          
          {loading ? (
            <>
              <div className="grid grid-cols-4 gap-6">
                <SkeletonMetricCard />
                <SkeletonMetricCard />
                <SkeletonMetricCard />
                <SkeletonMetricCard />
              </div>
              <SkeletonTable rows={5} columns={5} />
            </>
          ) : (
            <div className="grid grid-cols-3 gap-6">
              <SkeletonCard />
              <SkeletonMetricCard />
              <div className="space-y-4">
                <Skeleton className="h-6 w-full" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-6 w-3/4" />
              </div>
            </div>
          )}
        </section>

        {/* Toast Notifications Section */}
        <section className="space-y-6">
          <h2 className="text-3xl font-bold text-neutral-slate-900 dark:text-dark-text-primary">
            Toast Notifications
          </h2>
          
          <div className="grid grid-cols-4 gap-4">
            <button
              onClick={() => toast.success('Document uploaded successfully!')}
              className="px-6 py-3 bg-gradient-to-r from-growth-emerald-500 to-growth-emerald-600 hover:from-growth-emerald-600 hover:to-growth-emerald-700 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              Show Success
            </button>
            
            <button
              onClick={() => toast.error('Failed to upload document', {
                title: 'Upload Error',
                action: { label: 'Retry', onClick: () => console.log('Retry') }
              })}
              className="px-6 py-3 bg-gradient-to-r from-status-error-500 to-status-error-600 hover:from-status-error-600 hover:to-status-error-700 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              Show Error
            </button>
            
            <button
              onClick={() => toast.warning('Please review pending items')}
              className="px-6 py-3 bg-gradient-to-r from-status-warning-500 to-status-warning-600 hover:from-status-warning-600 hover:to-status-warning-700 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              Show Warning
            </button>
            
            <button
              onClick={() => toast.info('New features available!')}
              className="px-6 py-3 bg-gradient-to-r from-brand-blue-500 to-brand-blue-600 hover:from-brand-blue-600 hover:to-brand-blue-700 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              Show Info
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}

















