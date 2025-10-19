import { lazy } from 'react'

/**
 * Route-based Code Splitting Configuration
 * Lazy load components for optimal bundle size
 */

// Lazy load route components
export const Dashboard = lazy(() => import('../components/Dashboard'))
export const CleanProfessionalDashboard = lazy(() => import('../CleanProfessionalDashboard'))
export const DocumentUpload = lazy(() => import('../components/DocumentUpload'))
export const ExecutiveDocumentCenter = lazy(() => import('../components/ExecutiveDocumentCenter'))
export const ExecutiveAnalytics = lazy(() => import('../components/ExecutiveAnalytics'))
export const PropertyManagementExecutive = lazy(() => import('../components/PropertyManagementExecutive'))
export const AdvancedAnalytics = lazy(() => import('../components/AdvancedAnalytics'))
export const AIFeatures = lazy(() => import('../components/AIFeatures'))

/**
 * Route configuration with code splitting
 */
export const routes = [
  {
    path: '/',
    component: CleanProfessionalDashboard,
    preload: true, // Preload on app init
  },
  {
    path: '/dashboard',
    component: Dashboard,
    preload: false,
  },
  {
    path: '/upload',
    component: DocumentUpload,
    preload: false,
  },
  {
    path: '/documents',
    component: ExecutiveDocumentCenter,
    preload: false,
  },
  {
    path: '/analytics',
    component: ExecutiveAnalytics,
    preload: false,
  },
  {
    path: '/properties',
    component: PropertyManagementExecutive,
    preload: false,
  },
  {
    path: '/advanced-analytics',
    component: AdvancedAnalytics,
    preload: false,
  },
  {
    path: '/ai-features',
    component: AIFeatures,
    preload: false,
  },
]

/**
 * Preload a route component
 * Call this on hover or route prediction
 */
export const preloadRoute = (routePath) => {
  const route = routes.find(r => r.path === routePath)
  if (route && route.component) {
    // Trigger webpack to load the chunk
    route.component.preload?.()
  }
}

















