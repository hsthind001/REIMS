import { useState } from 'react'
import DashboardHeader from './DashboardHeader'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { Alert } from './ui/Alert'
import { ToastProvider, useToast } from './ui/Toast'

/**
 * Dashboard Header Demo
 * Showcases all header features with interactive controls
 */

function DemoContent() {
  const { toast } = useToast()
  const [systemStatus, setSystemStatus] = useState('healthy')
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'Document Uploaded',
      message: 'Property_Analysis_Q4.pdf has been processed',
      time: '2 minutes ago',
      read: false
    },
    {
      id: 2,
      title: 'AI Insight Available',
      message: 'New market trend detected for downtown properties',
      time: '1 hour ago',
      read: false
    },
    {
      id: 3,
      title: 'Report Generated',
      message: 'Monthly portfolio report is ready',
      time: '3 hours ago',
      read: true
    },
    {
      id: 4,
      title: 'Property Alert',
      message: 'Occupancy rate dropped below 90% at Sunset Apartments',
      time: '5 hours ago',
      read: true
    }
  ])

  const user = {
    name: 'John Doe',
    email: 'john.doe@reims.io',
    avatar: null
  }

  const handleLogout = () => {
    toast.info('Logging out...', {
      title: 'Goodbye!',
      duration: 3000
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-slate-50 to-brand-blue-50 dark:from-dark-bg-primary dark:to-dark-bg-secondary">
      {/* Header */}
      <DashboardHeader
        user={user}
        notifications={notifications}
        systemStatus={systemStatus}
        onLogout={handleLogout}
      />

      {/* Demo Content */}
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Hero */}
        <div className="text-center space-y-4 py-12">
          <h1 className="text-5xl font-black bg-gradient-to-r from-brand-blue-600 to-accent-purple-600 bg-clip-text text-transparent">
            Modern Dashboard Header
          </h1>
          <p className="text-xl text-neutral-slate-600 dark:text-dark-text-secondary max-w-2xl mx-auto">
            A feature-rich header with glassmorphism effect, real-time clock, system status, notifications, and command palette
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-6">
          <Card variant="blue">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">🎨</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                Glassmorphism
              </h3>
              <p className="text-sm text-neutral-slate-600">
                Modern glass effect with backdrop blur
              </p>
            </CardContent>
          </Card>

          <Card variant="purple">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">⏰</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                Real-time Clock
              </h3>
              <p className="text-sm text-neutral-slate-600">
                Live updating time and date display
              </p>
            </CardContent>
          </Card>

          <Card variant="success">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">🟢</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                System Status
              </h3>
              <p className="text-sm text-neutral-slate-600">
                Animated status indicator with pulse
              </p>
            </CardContent>
          </Card>

          <Card variant="default">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">🔍</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                Command Palette
              </h3>
              <p className="text-sm text-neutral-slate-600">
                Press Cmd+K / Ctrl+K to search
              </p>
            </CardContent>
          </Card>

          <Card variant="default">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">🔔</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                Notifications
              </h3>
              <p className="text-sm text-neutral-slate-600">
                {notifications.filter(n => !n.read).length} unread notifications
              </p>
            </CardContent>
          </Card>

          <Card variant="default">
            <CardContent className="p-6">
              <div className="text-4xl mb-3">👤</div>
              <h3 className="text-lg font-bold text-neutral-slate-900 mb-2">
                User Profile
              </h3>
              <p className="text-sm text-neutral-slate-600">
                Dropdown with settings and logout
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Interactive Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Interactive Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* System Status Control */}
            <div>
              <h4 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                Change System Status
              </h4>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setSystemStatus('healthy')
                    toast.success('System status set to healthy')
                  }}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    systemStatus === 'healthy'
                      ? 'bg-growth-emerald-500 text-white shadow-lg'
                      : 'bg-neutral-slate-100 text-neutral-slate-700 hover:bg-neutral-slate-200'
                  }`}
                >
                  🟢 Healthy
                </button>
                <button
                  onClick={() => {
                    setSystemStatus('warning')
                    toast.warning('System status set to warning')
                  }}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    systemStatus === 'warning'
                      ? 'bg-status-warning-500 text-white shadow-lg'
                      : 'bg-neutral-slate-100 text-neutral-slate-700 hover:bg-neutral-slate-200'
                  }`}
                >
                  🟡 Warning
                </button>
                <button
                  onClick={() => {
                    setSystemStatus('critical')
                    toast.error('System status set to critical')
                  }}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    systemStatus === 'critical'
                      ? 'bg-status-error-500 text-white shadow-lg'
                      : 'bg-neutral-slate-100 text-neutral-slate-700 hover:bg-neutral-slate-200'
                  }`}
                >
                  🔴 Critical
                </button>
              </div>
            </div>

            {/* Notifications Control */}
            <div>
              <h4 className="text-sm font-bold text-neutral-slate-900 dark:text-dark-text-primary mb-3">
                Notification Actions
              </h4>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    const newNotification = {
                      id: Date.now(),
                      title: 'Test Notification',
                      message: 'This is a test notification',
                      time: 'Just now',
                      read: false
                    }
                    setNotifications([newNotification, ...notifications])
                    toast.info('New notification added')
                  }}
                  className="px-4 py-2 rounded-lg bg-brand-blue-500 hover:bg-brand-blue-600 text-white font-semibold transition-colors"
                >
                  Add Notification
                </button>
                <button
                  onClick={() => {
                    setNotifications(notifications.map(n => ({ ...n, read: true })))
                    toast.success('All notifications marked as read')
                  }}
                  className="px-4 py-2 rounded-lg bg-neutral-slate-100 hover:bg-neutral-slate-200 text-neutral-slate-700 font-semibold transition-colors"
                >
                  Mark All Read
                </button>
                <button
                  onClick={() => {
                    setNotifications([])
                    toast.info('All notifications cleared')
                  }}
                  className="px-4 py-2 rounded-lg bg-neutral-slate-100 hover:bg-neutral-slate-200 text-neutral-slate-700 font-semibold transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Keyboard Shortcuts */}
        <Card>
          <CardHeader>
            <CardTitle>Keyboard Shortcuts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-slate-50 dark:bg-dark-bg-tertiary">
                <span className="text-sm font-medium text-neutral-slate-700 dark:text-dark-text-primary">
                  Open Command Palette
                </span>
                <kbd className="px-2 py-1 rounded bg-neutral-slate-200 dark:bg-dark-bg-primary text-xs font-mono">
                  Cmd+K / Ctrl+K
                </kbd>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-slate-50 dark:bg-dark-bg-tertiary">
                <span className="text-sm font-medium text-neutral-slate-700 dark:text-dark-text-primary">
                  Close Modal
                </span>
                <kbd className="px-2 py-1 rounded bg-neutral-slate-200 dark:bg-dark-bg-primary text-xs font-mono">
                  ESC
                </kbd>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Alert variant="info" title="Try It Out!">
          <ul className="space-y-2 text-sm">
            <li>• Press <strong>Cmd+K</strong> (Mac) or <strong>Ctrl+K</strong> (Windows) to open the command palette</li>
            <li>• Click the <strong>bell icon</strong> to view {notifications.filter(n => !n.read).length} unread notifications</li>
            <li>• Click your <strong>profile</strong> to access user menu</li>
            <li>• Watch the <strong>real-time clock</strong> update every second</li>
            <li>• Change the <strong>system status</strong> to see animated transitions</li>
          </ul>
        </Alert>
      </div>
    </div>
  )
}

export default function DashboardHeaderDemo() {
  return (
    <ToastProvider>
      <DemoContent />
    </ToastProvider>
  )
}

















