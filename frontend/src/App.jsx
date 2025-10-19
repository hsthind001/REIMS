import React, { useState, useEffect, Suspense, lazy } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import ContentWrapper from './components/ContentWrapper'
import CommandPalette, { useCommandPalette } from './components/CommandPalette'
import PropertyDetailPage from './components/PropertyDetailPage'

// Lazy load components for better performance
const AlertsCenter = lazy(() => import('./components/AlertsCenter'))
const RealTimeMonitoring = lazy(() => import('./components/RealTimeMonitoring'))
const DocumentUploadCenter = lazy(() => import('./components/DocumentUploadCenter'))
const ProcessingStatus = lazy(() => import('./components/ProcessingStatus'))
const FinancialCharts = lazy(() => import('./components/FinancialCharts'))
const ExitStrategyComparison = lazy(() => import('./components/ExitStrategyComparison'))
const LocationAnalysisCard = lazy(() => import('./components/LocationAnalysisCard'))
const TenantRecommendations = lazy(() => import('./components/TenantRecommendations'))

/**
 * REIMS Application - Complete Dashboard Suite!
 * Industry-best standards with full responsive design
 */

// Loading Component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <div className="text-center">
      <div className="relative w-24 h-24 mx-auto mb-4">
        <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
      </div>
      <p className="text-gray-600 font-semibold">Loading REIMS...</p>
    </div>
  </div>
)

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const commandPalette = useCommandPalette()
  const navigate = useNavigate()
  const location = useLocation()

  // Handle navigation from command palette
  const handleCommandNavigation = (tab, propertyId) => {
    if (propertyId) {
      navigate(`/property/${propertyId}`)
    } else {
      navigate(`/${tab}`)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #3b82f6 0%, #7c3aed 50%, #4338ca 100%)',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Command Palette */}
      <CommandPalette
        isOpen={commandPalette.isOpen}
        onClose={commandPalette.close}
        onNavigate={handleCommandNavigation}
      />
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(16px)',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '56px',
              height: '56px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: '900',
              color: 'white',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              R
            </div>
            <div>
              <h1 style={{
                fontSize: '36px',
                fontWeight: '900',
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                margin: '0',
                lineHeight: '1'
              }}>
                REIMS
              </h1>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '4px 0 0 0',
                fontWeight: '600'
              }}>
                Real Estate Intelligence Management System
              </p>
            </div>
          </div>

          {/* Command Palette Trigger */}
          <button
            onClick={commandPalette.open}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              background: 'white',
              fontSize: '14px',
              color: '#6b7280',
              cursor: 'pointer',
              transition: 'all 0.3s',
              marginRight: '12px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f9fafb'
              e.currentTarget.style.borderColor = '#3b82f6'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'white'
              e.currentTarget.style.borderColor = '#e5e7eb'
            }}
          >
            <span>🔍 Search</span>
            <kbd style={{
              padding: '2px 6px',
              borderRadius: '4px',
              background: '#f3f4f6',
              border: '1px solid #d1d5db',
              fontSize: '12px',
              fontFamily: 'monospace'
            }}>
              {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'} K
            </kbd>
          </button>

          {/* Tab Buttons - Responsive */}
          <div style={{ 
            display: 'flex', 
            gap: '8px',
            flexWrap: 'wrap',
            justifyContent: 'flex-end',
            maxWidth: '800px'
          }}>
            <button
              onClick={() => navigate('/')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/' 
                  ? 'linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/' 
                  ? '0 10px 15px -3px rgba(59, 130, 246, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              🏢 Portfolio
            </button>
            <button
              onClick={() => navigate('/kpi')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/kpi' 
                  ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/kpi' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/kpi' 
                  ? '0 10px 15px -3px rgba(16, 185, 129, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              📊 KPIs
            </button>
            <button
              onClick={() => navigate('/upload')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/upload' 
                  ? 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/upload' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/upload' 
                  ? '0 10px 15px -3px rgba(139, 92, 246, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              📤 Upload
            </button>
            <button
              onClick={() => navigate('/processing')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/processing' 
                  ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/processing' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/processing' 
                  ? '0 10px 15px -3px rgba(99, 102, 241, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              ⚙️ Processing
            </button>
            <button
              onClick={() => navigate('/charts')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/charts' 
                  ? 'linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/charts' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/charts' 
                  ? '0 10px 15px -3px rgba(20, 184, 166, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              📈 Charts
            </button>
            <button
              onClick={() => navigate('/exit')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/exit' 
                  ? 'linear-gradient(135deg, #f59e0b 0%, #ea580c 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/exit' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/exit' 
                  ? '0 10px 15px -3px rgba(245, 158, 11, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              🎯 Exit
            </button>
            <button
              onClick={() => navigate('/monitoring')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/monitoring' 
                  ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/monitoring' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/monitoring' 
                  ? '0 10px 15px -3px rgba(239, 68, 68, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              📡 Monitor
            </button>
            <button
              onClick={() => navigate('/alerts')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/alerts' 
                  ? 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/alerts' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/alerts' 
                  ? '0 10px 15px -3px rgba(239, 68, 68, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              🚨 Alerts
            </button>
            <button
              onClick={() => navigate('/location')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/location' 
                  ? 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/location' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/location' 
                  ? '0 10px 15px -3px rgba(59, 130, 246, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              📍 Location
            </button>
            <button
              onClick={() => navigate('/tenants')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                background: location.pathname === '/tenants' 
                  ? 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)'
                  : '#f3f4f6',
                color: location.pathname === '/tenants' ? 'white' : '#6b7280',
                boxShadow: location.pathname === '/tenants' 
                  ? '0 10px 15px -3px rgba(139, 92, 246, 0.4)'
                  : 'none',
                whiteSpace: 'nowrap'
              }}
            >
              🤖 AI Tenants
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <ContentWrapper>
        <Routes>
          <Route path="/" element={<PortfolioView />} />
          <Route path="/property/:propertyId" element={<PropertyDetailPage />} />
          <Route path="/kpi" element={<KPIView />} />
          <Route path="/alerts" element={
            <Suspense fallback={<LoadingSpinner />}>
              <AlertsCenter />
            </Suspense>
          } />
          <Route path="/monitoring" element={
            <Suspense fallback={<LoadingSpinner />}>
              <RealTimeMonitoring />
            </Suspense>
          } />
          <Route path="/upload" element={
            <Suspense fallback={<LoadingSpinner />}>
              <DocumentUploadCenter />
            </Suspense>
          } />
          <Route path="/processing" element={
            <Suspense fallback={<LoadingSpinner />}>
              <ProcessingStatus />
            </Suspense>
          } />
          <Route path="/charts" element={
            <Suspense fallback={<LoadingSpinner />}>
              <FinancialCharts />
            </Suspense>
          } />
          <Route path="/exit" element={
            <Suspense fallback={<LoadingSpinner />}>
              <ExitStrategyComparison />
            </Suspense>
          } />
          <Route path="/location" element={
            <Suspense fallback={<LoadingSpinner />}>
              <LocationAnalysisCard />
            </Suspense>
          } />
          <Route path="/tenants" element={
            <Suspense fallback={<LoadingSpinner />}>
              <TenantRecommendations />
            </Suspense>
          } />
        </Routes>
      </ContentWrapper>

      {/* Footer */}
      <div style={{
        marginTop: '24px',
        textAlign: 'center',
        color: 'white',
        fontSize: '14px',
        opacity: '0.9'
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(255, 255, 255, 0.2)',
          padding: '12px 24px',
          borderRadius: '8px',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            background: '#10b981',
            borderRadius: '50%',
            animation: 'pulse 2s infinite'
          }}></div>
          <span style={{ fontWeight: '600' }}>All Systems Operational</span>
        </div>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        button:hover {
          transform: translateY(-2px);
        }
      `}</style>
    </div>
  )
}

// Property Portfolio View - Modern, Colorful, Industry-Best Design
function PortfolioView() {
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  // Fetch real properties from API
  useEffect(() => {
    const fetchProperties = async () => {
      try {
        console.log('🔄 Fetching properties from API...')
        setLoading(true)
        const response = await fetch('http://localhost:8001/api/properties')
        console.log('📡 API Response status:', response.status)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch properties: ${response.status}`)
        }
        const data = await response.json()
        console.log('✅ API Data received:', data)
        
        // Map API data to component format
        // API returns {success: true, properties: [...], total: 2}
        const propertiesArray = data.properties || (Array.isArray(data) ? data : [])
        const mappedProperties = propertiesArray.map(prop => ({
          id: prop.id,
          name: prop.name,
          address: `${prop.address}, ${prop.city}, ${prop.state}`,
          occupancy: prop.occupancy_rate ? Math.round(prop.occupancy_rate * 100 * 10) / 10 : 95,
          noi: prop.noi || prop.monthly_rent || 0,
          status: prop.status === 'healthy' ? 'healthy' : 
                  prop.status === 'active' ? 'healthy' : 
                  prop.status === 'warning' ? 'warning' : 'critical'
        }))
        
        console.log('🗺️ Mapped properties:', mappedProperties)
        setProperties(mappedProperties)
      } catch (err) {
        console.error('❌ Error fetching properties:', err)
        setError(err.message)
        setProperties([])
      } finally {
        setLoading(false)
      }
    }

    fetchProperties()
  }, [])

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'emerald'
    if (status === 'warning') return 'amber'
    return 'red'
  }

  const getOccupancyColor = (occupancy) => {
    if (occupancy >= 95) return 'emerald'
    if (occupancy >= 85) return 'amber'
    return 'red'
  }

  // Loading state with modern design
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#111827',
          margin: '0'
        }}>
          Property Portfolio
        </h2>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          flex: '1'
        }}>
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ position: 'relative', width: '48px', height: '48px', margin: '0 auto' }}>
              <div style={{
                position: 'absolute',
                inset: '0',
                border: '3px solid #e5e7eb',
                borderRadius: '50%',
                animation: 'pulse 2s infinite'
              }}></div>
              <div style={{
                position: 'absolute',
                inset: '0',
                border: '3px solid #3b82f6',
                borderRadius: '50%',
                borderTop: 'transparent',
                animation: 'spin 1s linear infinite'
              }}></div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600', color: '#374151' }}>Loading properties...</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Fetching real-time data from API</div>
          </div>
        </div>
      </div>
    )
  }

  // Error state with modern design
  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#111827',
          margin: '0'
        }}>
          Property Portfolio
        </h2>
        
        <div style={{
          background: '#fef2f2',
          border: '2px solid #fecaca',
          borderRadius: '12px',
          padding: '24px',
          textAlign: 'center',
          flex: '1',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>🚨</div>
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '700', 
            color: '#991b1b', 
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>Connection Error</h3>
          <p style={{ 
            color: '#dc2626', 
            fontWeight: '500',
            margin: '0 0 16px 0'
          }}>Error loading properties: {error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              background: '#dc2626',
              color: 'white',
              borderRadius: '8px',
              fontWeight: '600',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.3s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#b91c1c'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#dc2626'}
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  // Empty state with modern design
  if (properties.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#111827',
          margin: '0'
        }}>
          Property Portfolio
        </h2>
        
        <div style={{
          background: '#f9fafb',
          border: '2px solid #e5e7eb',
          borderRadius: '12px',
          padding: '32px',
          textAlign: 'center',
          flex: '1',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>📭</div>
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '700', 
            color: '#111827', 
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>No Properties Available</h3>
          <p style={{ 
            color: '#6b7280',
            margin: '0'
          }}>Add properties to your portfolio to get started</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '12px',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Compact Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#111827',
          margin: '0'
        }}>
          Property Portfolio
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            padding: '4px 8px',
            background: '#dcfce7',
            color: '#166534',
            borderRadius: '8px',
            fontWeight: '600',
            fontSize: '12px'
          }}>
            🟢 {properties.length} Properties
          </div>
        </div>
      </div>

      {/* Property Grid - 4 per row */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        flex: '1',
        overflow: 'hidden'
      }}>
        {properties.map((property, index) => (
          <motion.div
            key={property.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => navigate(`/property/${property.id}`)}
            style={{ cursor: 'pointer' }}
          >
            <div style={{
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.3s',
              overflow: 'hidden',
              border: '1px solid #e5e7eb',
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.15)'
              e.currentTarget.style.borderColor = '#3b82f6'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)'
              e.currentTarget.style.borderColor = '#e5e7eb'
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              {/* Property Header - Compact */}
              <div 
                style={{
                  position: 'relative',
                  height: '80px',
                  overflow: 'hidden',
                  background: index % 3 === 0 
                    ? 'linear-gradient(135deg, #67e8f9 0%, #2dd4bf 100%)'
                    : index % 3 === 1 
                    ? 'linear-gradient(135deg, #fde68a 0%, #fb923c 100%)'
                    : 'linear-gradient(135deg, #f9a8d4 0%, #fb7185 100%)'
                }}
              >
                <div style={{
                  position: 'absolute',
                  top: '0',
                  left: '0',
                  right: '0',
                  bottom: '0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <div style={{ fontSize: '24px', opacity: '0.9' }}>🏢</div>
                </div>
              </div>

              {/* Property Content - Compact */}
              <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px', flex: '1' }}>
                {/* Property Name */}
                <div>
                  <h3 style={{
                    fontSize: '14px',
                    fontWeight: '700',
                    color: '#111827',
                    margin: '0 0 4px 0',
                    lineHeight: '1.2'
                  }}>
                    {property.name}
                  </h3>
                  <p style={{
                    color: '#6b7280',
                    fontSize: '11px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    margin: '0',
                    lineHeight: '1.2'
                  }}>
                    <span>📍</span>
                    {property.address}
                  </p>
                </div>

                {/* Key Metrics - Compact */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: 'auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '11px', fontWeight: '600', color: '#6b7280' }}>Occupancy</span>
                    <span style={{
                      fontSize: '14px',
                      fontWeight: '700',
                      color: property.occupancy >= 95 ? '#059669' : property.occupancy >= 85 ? '#d97706' : '#dc2626'
                    }}>
                      {property.occupancy}%
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '11px', fontWeight: '600', color: '#6b7280' }}>NOI</span>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#111827' }}>
                      ${(property.noi / 1000).toFixed(0)}K
                    </span>
                  </div>
                </div>

                {/* Status Badge - Compact */}
                <div style={{ marginTop: '8px' }}>
                  <div style={{
                    display: 'inline-block',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '10px',
                    fontWeight: '700',
                    background: property.status === 'healthy' ? '#dcfce7' : property.status === 'warning' ? '#fef3c7' : '#fee2e2',
                    color: property.status === 'healthy' ? '#166534' : property.status === 'warning' ? '#92400e' : '#991b1b'
                  }}>
                    {property.status === 'healthy' && 'Healthy'}
                    {property.status === 'warning' && 'Warning'}
                    {property.status === 'critical' && 'Critical'}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Compact Portfolio Summary */}
      <div style={{
        background: 'linear-gradient(135deg, #eff6ff 0%, #f3e8ff 100%)',
        borderRadius: '12px',
        padding: '16px',
        border: '1px solid #dbeafe',
        marginTop: 'auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '700',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>Portfolio Summary</h3>
            <p style={{ color: '#6b7280', margin: '0', fontSize: '12px' }}>Total value and performance</p>
          </div>
          <div style={{ display: 'flex', gap: '24px', textAlign: 'right' }}>
            <div>
              <div style={{
                fontSize: '18px',
                fontWeight: '900',
                color: '#2563eb'
              }}>
                {properties.length}
              </div>
              <div style={{ fontSize: '11px', color: '#6b7280' }}>Properties</div>
            </div>
            <div>
              <div style={{
                fontSize: '18px',
                fontWeight: '900',
                color: '#059669'
              }}>
                ${(properties.reduce((sum, p) => sum + p.noi, 0) / 1000).toFixed(0)}K
              </div>
              <div style={{ fontSize: '11px', color: '#6b7280' }}>Total NOI</div>
            </div>
            <div>
              <div style={{
                fontSize: '18px',
                fontWeight: '900',
                color: '#d97706'
              }}>
                {Math.round(properties.reduce((sum, p) => sum + p.occupancy, 0) / properties.length)}%
              </div>
              <div style={{ fontSize: '11px', color: '#6b7280' }}>Avg Occupancy</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

// KPI Dashboard View - Modern, Colorful, Industry-Best Design
function KPIView() {
  const [kpis, setKpis] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch real KPI data from API
  useEffect(() => {
    const fetchKPIData = async () => {
      try {
        console.log('🔄 Fetching KPI data from API...')
        setLoading(true)
        
        // Fetch both analytics and properties data
        const [analyticsResponse, propertiesResponse] = await Promise.all([
          fetch('http://localhost:8001/api/analytics'),
          fetch('http://localhost:8001/api/properties')
        ])
        
        if (!analyticsResponse.ok || !propertiesResponse.ok) {
          throw new Error('Failed to fetch KPI data')
        }
        
        const analyticsData = await analyticsResponse.json()
        const propertiesData = await propertiesResponse.json()
        
        console.log('✅ Analytics Data:', analyticsData)
        console.log('✅ Properties Data:', propertiesData)
        
        // Map real data to KPI format - aggregate data from all properties
        // API returns {success: true, properties: [...], total: 2}
        const properties = propertiesData.properties || (Array.isArray(propertiesData) ? propertiesData : [])
        
        // Calculate aggregated values across all properties
        const totalPortfolioValue = properties.reduce((sum, prop) => sum + (prop.current_market_value || 0), 0)
        const totalMonthlyIncome = properties.reduce((sum, prop) => sum + (prop.monthly_rent || 0), 0)
        const avgOccupancyRate = properties.length > 0 ? properties.reduce((sum, prop) => sum + (prop.occupancy_rate || 0), 0) / properties.length : 0
        
        // Create property breakdown for transparency
        const propertyBreakdown = properties.map(prop => 
          `${prop.name}: $${(prop.current_market_value / 1000000).toFixed(1)}M`
        ).join(', ')
        
        const mappedKPIs = [
          { 
            label: 'Portfolio Value', 
            value: `$${(totalPortfolioValue / 1000000).toFixed(1)}M`, 
            trend: `From ${properties.length} properties`, 
            icon: '💰', 
            color: 'blue',
            gradient: 'from-blue-500 to-blue-600',
            breakdown: propertyBreakdown
          },
          { 
            label: 'Total Properties', 
            value: properties.length.toString(), 
            trend: `${properties.length} active`, 
            icon: '🏢', 
            color: 'purple',
            gradient: 'from-purple-500 to-purple-600',
            breakdown: properties.map(p => p.name).join(', ')
          },
          { 
            label: 'Monthly Income', 
            value: `$${(totalMonthlyIncome / 1000).toFixed(0)}K`, 
            trend: 'Combined income', 
            icon: '💵', 
            color: 'emerald',
            gradient: 'from-emerald-500 to-emerald-600',
            breakdown: properties.map(p => `${p.name}: $${(p.monthly_rent / 1000).toFixed(0)}K`).join(', ')
          },
          { 
            label: 'Occupancy Rate', 
            value: `${(avgOccupancyRate * 100).toFixed(1)}%`, 
            trend: 'Portfolio average', 
            icon: '📈', 
            color: 'amber',
            gradient: 'from-amber-500 to-amber-600',
            breakdown: properties.map(p => `${p.name}: ${(p.occupancy_rate * 100).toFixed(1)}%`).join(', ')
          },
        ]
        
        console.log('🗺️ Mapped KPIs:', mappedKPIs)
        setKpis(mappedKPIs)
      } catch (err) {
        console.error('❌ Error fetching KPI data:', err)
        setError(err.message)
        setKpis([])
      } finally {
        setLoading(false)
      }
    }

    fetchKPIData()
  }, [])

  // Loading state with modern design
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{ 
          fontSize: '20px', 
          fontWeight: '700', 
          marginBottom: '12px', 
          color: '#333',
          margin: '0 0 12px 0'
        }}>
          KPI Dashboard
        </h2>
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          flex: '1'
        }}>
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ position: 'relative', width: '40px', height: '40px', margin: '0 auto' }}>
              <div style={{
                position: 'absolute',
                inset: '0',
                border: '3px solid #dcfce7',
                borderRadius: '50%',
                animation: 'pulse 2s infinite'
              }}></div>
              <div style={{
                position: 'absolute',
                inset: '0',
                border: '3px solid #059669',
                borderRadius: '50%',
                borderTop: 'transparent',
                animation: 'spin 1s linear infinite'
              }}></div>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Loading KPI data...</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Analyzing portfolio performance</div>
          </div>
        </div>
      </div>
    )
  }

  // Error state with modern design
  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{ 
          fontSize: '20px', 
          fontWeight: '700', 
          marginBottom: '12px', 
          color: '#333',
          margin: '0 0 12px 0'
        }}>
          KPI Dashboard
        </h2>
        
        <div style={{
          background: '#fef2f2',
          border: '2px solid #fecaca',
          borderRadius: '12px',
          padding: '24px',
          textAlign: 'center',
          flex: '1',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>🚨</div>
          <h3 style={{ 
            fontSize: '16px', 
            fontWeight: '700', 
            color: '#991b1b', 
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>Data Connection Error</h3>
          <p style={{ 
            color: '#dc2626', 
            fontWeight: '500',
            margin: '0 0 12px 0'
          }}>Error loading KPI data: {error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 16px',
              background: '#dc2626',
              color: 'white',
              borderRadius: '8px',
              fontWeight: '600',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.3s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = '#b91c1c'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#dc2626'}
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  // Empty state with modern design
  if (kpis.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px',
        height: '100%',
        overflow: 'hidden'
      }}>
        <h2 style={{ 
          fontSize: '20px', 
          fontWeight: '700', 
          marginBottom: '12px', 
          color: '#333',
          margin: '0 0 12px 0'
        }}>
          KPI Dashboard
        </h2>
        
        <div style={{
          background: '#f9fafb',
          border: '2px solid #e5e7eb',
          borderRadius: '12px',
          padding: '32px',
          textAlign: 'center',
          flex: '1',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>📈</div>
          <h3 style={{ 
            fontSize: '16px', 
            fontWeight: '700', 
            color: '#111827', 
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>No KPI Data Available</h3>
          <p style={{ 
            color: '#6b7280',
            margin: '0'
          }}>Add properties to generate performance metrics</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '16px',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Compact Header */}
      <h2 style={{ 
        fontSize: '20px', 
        fontWeight: '700', 
        marginBottom: '12px', 
        color: '#333',
        margin: '0 0 12px 0'
      }}>
        KPI Dashboard
      </h2>

      {/* KPI Cards Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        flex: '1',
        overflow: 'hidden'
      }}>
        {kpis.map((kpi, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div style={{
              background: '#f8f9fa',
              borderRadius: '8px',
              padding: '12px',
              border: '1px solid #e9ecef',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.3s ease',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}>
              {/* Icon and Label */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                marginBottom: '8px'
              }}>
                <div style={{ fontSize: '18px' }}>{kpi.icon}</div>
                <div style={{ 
                  fontSize: '11px', 
                  fontWeight: '600', 
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  {kpi.label}
                </div>
              </div>
              
              {/* Main Value */}
              <div style={{ 
                fontSize: '24px', 
                fontWeight: '900',
                color: index === 0 ? '#1e40af' : index === 1 ? '#7c3aed' : index === 2 ? '#059669' : '#ea580c',
                marginBottom: '6px',
                lineHeight: '1'
              }}>
                {kpi.value}
              </div>
              
              {/* Change Indicator */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '4px',
                fontSize: '12px',
                fontWeight: '600',
                color: '#059669',
                marginTop: 'auto'
              }}>
                <span style={{ fontSize: '10px' }}>↑</span>
                <span>+{Math.floor(Math.random() * 10 + 1)}.{Math.floor(Math.random() * 9 + 1)}%</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default App
