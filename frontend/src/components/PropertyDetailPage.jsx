import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, DollarSign, Home, Percent } from 'lucide-react';
import { motion } from 'framer-motion';
import ChartCard from './charts/ChartCard';
import MetricCard from './charts/MetricCard';
import PropertyNOIChart from './charts/PropertyNOIChart';
import PropertyRevenueChart from './charts/PropertyRevenueChart';

export default function PropertyDetailPage() {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  const [propertyData, setPropertyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch property-specific data
  useEffect(() => {
    const fetchPropertyData = async () => {
      try {
        console.log('🔄 Fetching property data for ID:', propertyId);
        setLoading(true);
        
        const response = await fetch(`http://localhost:8001/api/properties/${propertyId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch property: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Property data received:', data);
        console.log('📊 Property metrics:', {
          name: data.name,
          value: data.current_market_value,
          rent: data.monthly_rent,
          noi: data.noi,
          occupancy: data.occupancy_rate
        });
        setPropertyData(data);
      } catch (err) {
        console.error('❌ Error fetching property data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (propertyId) {
      fetchPropertyData();
    }
  }, [propertyId]);

  const calculateYearlyReturn = () => {
    if (!propertyData) return 0;
    const annualNOI = propertyData.noi || 0;
    const propertyValue = propertyData.current_market_value || 1;
    return ((annualNOI / propertyValue) * 100).toFixed(1);
  };

  const formatCurrency = (value) => {
    if (!value || value === 0) return '$0';
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value?.toFixed(0) || 0}`;
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '60px',
            height: '60px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <div style={{
            fontSize: '18px',
            color: '#6b7280',
            fontWeight: '500'
          }}>
            Loading property data...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '500px', padding: '24px' }}>
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px'
          }}>
            <div style={{
              fontSize: '16px',
              color: '#dc2626',
              fontWeight: '500'
            }}>
              Error loading property: {error}
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
          >
            <ArrowLeft size={20} />
            BACK TO PORTFOLIO
          </button>
        </div>
      </div>
    );
  }

  if (!propertyData) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '18px',
            color: '#6b7280',
            fontWeight: '500'
          }}>
            Property not found
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
      padding: '24px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '32px',
            marginBottom: '32px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '1px solid #e5e7eb'
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '24px'
          }}>
            <button
              onClick={() => navigate('/')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#f3f4f6',
                color: '#374151',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#e5e7eb'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#f3f4f6'}
            >
              <ArrowLeft size={16} />
              Back to Portfolio
            </button>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              backgroundColor: '#3b82f6',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Home size={28} color="white" />
            </div>
            <div>
              <h1 style={{
                fontSize: '32px',
                fontWeight: 'bold',
                color: '#111827',
                margin: '0 0 8px 0'
              }}>
                {propertyData.name}
              </h1>
              <div style={{
                fontSize: '16px',
                color: '#6b7280'
              }}>
                {propertyData.address}, {propertyData.city}, {propertyData.state}
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '24px',
            marginTop: '32px'
          }}>
            <div style={{
              backgroundColor: '#f0f9ff',
              border: '1px solid #bae6fd',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <DollarSign size={20} color="#0284c7" />
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#0284c7',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Market Value
                </div>
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#0c4a6e'
              }}>
                {formatCurrency(propertyData.current_market_value)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <TrendingUp size={20} color="#16a34a" />
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#16a34a',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Annual NOI
                </div>
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#14532d'
              }}>
                {formatCurrency(propertyData.noi)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#fefce8',
              border: '1px solid #fde047',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Percent size={20} color="#ca8a04" />
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#ca8a04',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Cap Rate
                </div>
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#a16207'
              }}>
                {calculateYearlyReturn()}%
              </div>
            </div>

            <div style={{
              backgroundColor: '#f3e8ff',
              border: '1px solid #c4b5fd',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Home size={20} color="#7c3aed" />
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#7c3aed',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Occupancy
                </div>
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#5b21b6'
              }}>
                {formatPercentage(propertyData.occupancy_rate)}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Charts Section */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(600px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {/* NOI Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              border: '1px solid #e5e7eb'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '24px'
            }}>
              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: '#111827',
                  margin: '0 0 4px 0'
                }}>
                  Net Operating Income
                </h3>
                <div style={{
                  fontSize: '14px',
                  color: '#6b7280'
                }}>
                  Monthly NOI trends and projections
                </div>
              </div>
            </div>
            <div style={{ height: '400px', marginBottom: '20px' }}>
              {propertyData && (
                <>
                  {console.log('🔍 Passing to NOI Chart:', { 
                    noi: propertyData.noi, 
                    monthly_rent: propertyData.monthly_rent,
                    id: propertyData.id 
                  })}
                  <PropertyNOIChart propertyData={propertyData} />
                </>
              )}
            </div>
          </motion.div>

          {/* Revenue Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '24px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              border: '1px solid #e5e7eb'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '24px'
            }}>
              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: '#111827',
                  margin: '0 0 4px 0'
                }}>
                  Revenue Analysis
                </h3>
                <div style={{
                  fontSize: '14px',
                  color: '#6b7280'
                }}>
                  Revenue breakdown and growth metrics
                </div>
              </div>
            </div>
            <div style={{ height: '400px', marginBottom: '20px' }}>
              {propertyData && (
                <>
                  {console.log('🔍 Passing to Revenue Chart:', { 
                    noi: propertyData.noi, 
                    monthly_rent: propertyData.monthly_rent,
                    id: propertyData.id 
                  })}
                  <PropertyRevenueChart propertyData={propertyData} />
                </>
              )}
            </div>
          </motion.div>
        </div>

        {/* Property Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '1px solid #e5e7eb'
          }}
        >
          <h3 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#111827',
            margin: '0 0 24px 0'
          }}>
            Property Details
          </h3>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Property Type
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {propertyData.property_type}
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Year Built
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {propertyData.year_built}
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Square Footage
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {propertyData.square_footage ? `${propertyData.square_footage.toLocaleString()} sq ft` : 'N/A'}
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Purchase Price
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {propertyData.purchase_price ? formatCurrency(propertyData.purchase_price) : 'N/A'}
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Monthly Rent
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {formatCurrency(propertyData.monthly_rent)}
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                Status
              </div>
              <div style={{
                fontSize: '16px',
                color: '#111827',
                fontWeight: '500'
              }}>
                {propertyData.status}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Add CSS animation for loading spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}