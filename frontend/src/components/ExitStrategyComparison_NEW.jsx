import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  RefreshCw,
  DollarSign,
  CheckCircle2,
  XCircle,
  Award,
  Clock,
  Target,
  Percent,
  Home,
  Calculator
} from 'lucide-react'

/**
 * REIMS Exit Strategy Comparison Dashboard
 * 
 * Features:
 * - Real-time data from backend API
 * - Property selector dropdown
 * - 3 scenarios: Hold, Refinance, Sale
 * - Side-by-side card comparison
 * - Recommended strategy highlighted
 * - Pros/Cons with visual indicators
 * - Confidence score with gauge
 * - All styling uses inline styles
 */

// Confidence Score Gauge Component
const ConfidenceGauge = ({ score, size = 'md' }) => {
  const sizeConfig = {
    sm: { container: 80, stroke: 6 },
    md: { container: 128, stroke: 8 },
    lg: { container: 160, stroke: 10 }
  }

  const { container, stroke } = sizeConfig[size]
  const radius = 50 - stroke / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const getColor = () => {
    if (score >= 80) return '#10b981' // Green
    if (score >= 60) return '#f59e0b' // Orange
    return '#ef4444' // Red
  }

  const color = getColor()

  return (
    <div style={{ position: 'relative', width: `${container}px`, height: `${container}px` }}>
      <svg style={{ transform: 'rotate(-90deg)' }} viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth={stroke}
          fill="none"
        />
        {/* Progress circle */}
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      {/* Score text */}
      <div style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <span style={{ fontSize: '30px', fontWeight: '900', color }}>
          {score}%
        </span>
        <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600' }}>Confidence</span>
      </div>
    </div>
  )
}

// Strategy Card Component
const StrategyCard = ({ strategy, onSelect, isSelected }) => {
  const Icon = strategy.icon
  const isRecommended = strategy.recommended

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)' }}
      transition={{ duration: 0.3 }}
      onClick={() => onSelect(strategy.id)}
      style={{
        position: 'relative',
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        cursor: 'pointer',
        transition: 'all 0.3s',
        border: isRecommended 
          ? '4px solid #22c55e'
          : '2px solid #e5e7eb',
        boxShadow: isRecommended 
          ? '0 20px 25px -5px rgba(34, 197, 94, 0.1), 0 10px 10px -5px rgba(34, 197, 94, 0.04)'
          : '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        outline: isSelected ? '4px solid rgba(59, 130, 246, 0.5)' : 'none'
      }}
    >
      {/* Recommended Badge */}
      {isRecommended && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
          style={{
            position: 'absolute',
            top: '-12px',
            right: '-12px',
            background: 'linear-gradient(90deg, #22c55e 0%, #10b981 100%)',
            color: '#ffffff',
            padding: '8px 16px',
            borderRadius: '9999px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Award style={{ width: '16px', height: '16px' }} />
          <span style={{ fontSize: '14px', fontWeight: '700' }}>Recommended</span>
        </motion.div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            padding: '12px',
            borderRadius: '12px',
            backgroundColor: isRecommended 
              ? '#d1fae5' 
              : strategy.id === 'hold' 
                ? '#dbeafe'
                : '#fed7aa'
          }}>
            <Icon style={{
              width: '24px',
              height: '24px',
              color: isRecommended 
                ? '#059669' 
                : strategy.id === 'hold' 
                  ? '#2563eb'
                  : '#ea580c'
            }} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '900', color: '#111827' }}>{strategy.name}</h3>
            <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>{strategy.description}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {strategy.id === 'hold' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>IRR</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#2563eb' }}>
                {strategy.metrics.irr}%
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Projected NOI</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                ${(strategy.metrics.projectedNOI / 1000).toFixed(0)}K/yr
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Terminal Value</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                ${(strategy.metrics.terminalValue / 1000000).toFixed(1)}M
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Hold Period</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                {strategy.metrics.holdPeriod} years
              </span>
            </div>
          </>
        )}

        {strategy.id === 'refinance' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Monthly Savings</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#22c55e' }}>
                ${(strategy.metrics.monthlySavings / 1000).toFixed(0)}K
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>New DSCR</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                {strategy.metrics.newDSCR.toFixed(2)}x
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Cash Out</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                ${(strategy.metrics.cashOut / 1000000).toFixed(1)}M
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>New Rate</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                {strategy.metrics.newRate}%
              </span>
            </div>
          </>
        )}

        {strategy.id === 'sale' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Net Proceeds</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#22c55e' }}>
                ${(strategy.metrics.netProceeds / 1000000).toFixed(2)}M
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Transaction Costs</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#ef4444' }}>
                ${(strategy.metrics.transactionCosts / 1000).toFixed(0)}K
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Annualized Return</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                {strategy.metrics.annualizedReturn}%
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Sale Price</span>
              <span style={{ fontSize: '18px', fontWeight: '900', color: '#111827' }}>
                ${(strategy.metrics.salePrice / 1000000).toFixed(1)}M
              </span>
            </div>
          </>
        )}
      </div>

      {/* Pros */}
      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ fontSize: '14px', fontWeight: '700', color: '#059669', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 style={{ width: '16px', height: '16px' }} />
          Advantages
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {strategy.pros.map((pro, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              style={{ display: 'flex', alignItems: 'start', gap: '8px' }}
            >
              <CheckCircle2 style={{ width: '16px', height: '16px', color: '#22c55e', flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontSize: '14px', color: '#374151' }}>{pro}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Cons */}
      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ fontSize: '14px', fontWeight: '700', color: '#dc2626', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <XCircle style={{ width: '16px', height: '16px' }} />
          Disadvantages
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {strategy.cons.map((con, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              style={{ display: 'flex', alignItems: 'start', gap: '8px' }}
            >
              <XCircle style={{ width: '16px', height: '16px', color: '#ef4444', flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontSize: '14px', color: '#374151' }}>{con}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Confidence Score */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '24px', borderTop: '2px solid #e5e7eb' }}>
        <ConfidenceGauge score={strategy.confidenceScore} size="md" />
      </div>
    </motion.div>
  )
}

// Main Component
export default function ExitStrategyComparison() {
  const [properties, setProperties] = useState([])
  const [selectedPropertyId, setSelectedPropertyId] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedStrategy, setSelectedStrategy] = useState('refinance')

  // Fetch available properties
  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const response = await fetch('/api/properties')
        const data = await response.json()
        const propertiesList = data.properties || data
        setProperties(propertiesList)
        if (propertiesList.length > 0) {
          setSelectedPropertyId(propertiesList[0].id)
        }
      } catch (err) {
        console.error('Failed to fetch properties:', err)
        setError('Failed to load properties')
      }
    }
    fetchProperties()
  }, [])

  // Fetch analysis when property changes
  useEffect(() => {
    if (selectedPropertyId) {
      fetchExitAnalysis(selectedPropertyId)
    }
  }, [selectedPropertyId])

  const fetchExitAnalysis = async (propertyId) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/exit-strategy/analyze/${propertyId}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch exit analysis')
      }
      
      const data = await response.json()
      console.log('Exit analysis data:', data)
      setAnalysis(data)
    } catch (err) {
      setError(err.message)
      console.error('Exit analysis error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          border: '4px solid #e5e7eb',
          borderTop: '4px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{
          marginTop: '16px',
          fontSize: '16px',
          color: '#6b7280',
          fontWeight: '600'
        }}>Analyzing exit strategies...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  // Error state
  if (error && !analysis) {
    return (
      <div style={{
        padding: '24px',
        backgroundColor: '#fef2f2',
        border: '2px solid #fecaca',
        borderRadius: '12px',
        maxWidth: '600px',
        margin: '0 auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#991b1b', marginBottom: '8px' }}>
          <XCircle style={{ width: '20px', height: '20px' }} />
          <span style={{ fontWeight: '600' }}>Analysis Error</span>
        </div>
        <p style={{ color: '#b91c1c', marginTop: '8px' }}>{error}</p>
        <button
          onClick={() => selectedPropertyId && fetchExitAnalysis(selectedPropertyId)}
          style={{
            marginTop: '16px',
            padding: '8px 16px',
            backgroundColor: '#dc2626',
            color: '#ffffff',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Retry Analysis
        </button>
      </div>
    )
  }

  // Convert analysis data to strategy format
  const strategies = analysis ? {
    hold: {
      id: 'hold',
      name: 'Hold Strategy',
      icon: Home,
      recommended: analysis.recommended_strategy === 'hold',
      metrics: {
        irr: analysis.hold.irr,
        projectedNOI: analysis.hold.projected_noi,
        terminalValue: analysis.hold.terminal_value,
        holdPeriod: analysis.hold.hold_period
      },
      pros: analysis.hold.pros,
      cons: analysis.hold.cons,
      confidenceScore: analysis.hold.confidence_score,
      description: analysis.hold.description
    },
    refinance: {
      id: 'refinance',
      name: 'Refinance Strategy',
      icon: RefreshCw,
      recommended: analysis.recommended_strategy === 'refinance',
      metrics: {
        monthlySavings: analysis.refinance.monthly_savings,
        newDSCR: analysis.refinance.new_dscr,
        cashOut: analysis.refinance.cash_out,
        newRate: analysis.refinance.new_rate
      },
      pros: analysis.refinance.pros,
      cons: analysis.refinance.cons,
      confidenceScore: analysis.refinance.confidence_score,
      description: analysis.refinance.description
    },
    sale: {
      id: 'sale',
      name: 'Sale Strategy',
      icon: DollarSign,
      recommended: analysis.recommended_strategy === 'sale',
      metrics: {
        netProceeds: analysis.sale.net_proceeds,
        transactionCosts: analysis.sale.transaction_costs,
        annualizedReturn: analysis.sale.annualized_return,
        salePrice: analysis.sale.sale_price
      },
      pros: analysis.sale.pros,
      cons: analysis.sale.cons,
      confidenceScore: analysis.sale.confidence_score,
      description: analysis.sale.description
    }
  } : null

  const strategyArray = strategies ? [strategies.hold, strategies.refinance, strategies.sale] : []
  const recommended = strategyArray.find(s => s.recommended)

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
      {/* Property Selector */}
      <div style={{
        marginBottom: '24px',
        padding: '20px',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        border: '2px solid #e5e7eb',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '700',
              color: '#111827',
              marginBottom: '4px'
            }}>Select Property for Exit Strategy Analysis</h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280'
            }}>Choose a property to analyze exit options</p>
          </div>
          <select
            value={selectedPropertyId || ''}
            onChange={(e) => setSelectedPropertyId(Number(e.target.value))}
            style={{
              padding: '12px 16px',
              fontSize: '16px',
              fontWeight: '600',
              color: '#111827',
              backgroundColor: '#ffffff',
              border: '2px solid #3b82f6',
              borderRadius: '8px',
              cursor: 'pointer',
              minWidth: '300px',
              outline: 'none'
            }}
          >
            {properties.map(property => (
              <option key={property.id} value={property.id}>
                {property.name} - ${((property.current_market_value || property.value) / 1000000).toFixed(1)}M
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Property Context Banner */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            marginBottom: '24px',
            padding: '20px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            borderRadius: '12px',
            color: '#ffffff'
          }}
        >
          <h2 style={{
            fontSize: '24px',
            fontWeight: '700',
            marginBottom: '8px'
          }}>{analysis.property_name}</h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginTop: '16px'
          }}>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8 }}>Purchase Price</div>
              <div style={{ fontSize: '20px', fontWeight: '700' }}>
                ${(analysis.purchase_price / 1000000).toFixed(2)}M
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8 }}>Current Value</div>
              <div style={{ fontSize: '20px', fontWeight: '700' }}>
                ${(analysis.current_value / 1000000).toFixed(2)}M
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8 }}>Annual NOI</div>
              <div style={{ fontSize: '20px', fontWeight: '700' }}>
                ${(analysis.noi / 1000000).toFixed(2)}M
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8 }}>Years Held</div>
              <div style={{ fontSize: '20px', fontWeight: '700' }}>
                {analysis.years_held.toFixed(1)}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Summary Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '24px' }}
      >
        <p style={{ color: '#6b7280', fontSize: '16px' }}>
          Compare three strategic options for maximizing property value and returns
        </p>
      </motion.div>

      {/* Recommended Strategy Banner */}
      {recommended && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            marginBottom: '32px',
            background: 'linear-gradient(90deg, #22c55e 0%, #10b981 100%)',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#ffffff', flexWrap: 'wrap', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ padding: '12px', backgroundColor: 'rgba(255, 255, 255, 0.2)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}>
                <Award style={{ width: '32px', height: '32px' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '24px', fontWeight: '900' }}>Recommended Strategy</h3>
                <p style={{ color: '#d1fae5', fontSize: '18px', marginTop: '4px' }}>
                  Based on current market conditions and financial analysis
                </p>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '30px', fontWeight: '900' }}>{recommended.name}</p>
              <p style={{ color: '#d1fae5', fontSize: '14px', marginTop: '4px' }}>
                {recommended.confidenceScore}% Confidence Score
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Strategy Cards Grid */}
      {strategies && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {strategyArray.map((strategy) => (
            <StrategyCard
              key={strategy.id}
              strategy={strategy}
              onSelect={setSelectedStrategy}
              isSelected={selectedStrategy === strategy.id}
            />
          ))}
        </div>
      )}

      {/* Comparison Summary */}
      {strategies && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '2px solid #e5e7eb'
          }}
        >
          <h3 style={{ fontSize: '24px', fontWeight: '900', color: '#111827', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Calculator style={{ width: '24px', height: '24px', color: '#3b82f6' }} />
            Quick Comparison
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
            {/* Best Return */}
            <div style={{ padding: '16px', background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)', borderRadius: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <TrendingUp style={{ width: '20px', height: '20px', color: '#2563eb' }} />
                <h4 style={{ fontWeight: '700', color: '#111827' }}>Best Return</h4>
              </div>
              <p style={{ fontSize: '30px', fontWeight: '900', color: '#2563eb' }}>
                Sale: {strategies.sale.metrics.annualizedReturn}%
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>Highest annualized return</p>
            </div>

            {/* Most Cash Flow */}
            <div style={{ padding: '16px', background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', borderRadius: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <DollarSign style={{ width: '20px', height: '20px', color: '#16a34a' }} />
                <h4 style={{ fontWeight: '700', color: '#111827' }}>Most Cash Flow</h4>
              </div>
              <p style={{ fontSize: '30px', fontWeight: '900', color: '#16a34a' }}>
                Refinance: ${(strategies.refinance.metrics.monthlySavings / 1000).toFixed(0)}K/mo
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>Monthly savings improvement</p>
            </div>

            {/* Most Stable */}
            <div style={{ padding: '16px', background: 'linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%)', borderRadius: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Clock style={{ width: '20px', height: '20px', color: '#ea580c' }} />
                <h4 style={{ fontWeight: '700', color: '#111827' }}>Most Stable</h4>
              </div>
              <p style={{ fontSize: '30px', fontWeight: '900', color: '#ea580c' }}>
                Hold: {strategies.hold.metrics.irr}% IRR
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>Steady long-term growth</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

