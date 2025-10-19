import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Activity,
  Target,
  PieChart,
  LineChart,
  BarChart,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Building,
  Users,
  FileText,
  Brain,
  Zap
} from 'lucide-react';

// Main Advanced Analytics Dashboard
export function AdvancedAnalyticsDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/analytics/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      
      const data = await response.json();
      setDashboardData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 300000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        <span className="ml-3">Loading analytics dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-2 text-red-800">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-semibold">Dashboard Error</span>
        </div>
        <p className="text-red-700 mt-2">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-8">
        <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Analytics Dashboard</h1>
          <p className="text-gray-600">Real-time metrics and performance insights</p>
        </div>
        <div className="flex items-center gap-4">
          {lastUpdated && (
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </div>
          )}
          <button
            onClick={fetchDashboardData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <KPICards data={dashboardData} />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PropertyMetricsChart data={dashboardData.property_metrics} />
        <FinancialMetricsChart data={dashboardData.financial_metrics} />
        <AlertMetricsChart data={dashboardData.alert_metrics} />
        <AIMetricsChart data={dashboardData.ai_metrics} />
      </div>

      {/* Performance Overview */}
      <PerformanceOverview data={dashboardData.performance_metrics} />

      {/* Real-time Metrics */}
      <RealTimeMetrics />
    </div>
  );
}

// KPI Cards Component
function KPICards({ data }) {
  const kpis = [
    {
      title: 'Total Properties',
      value: data.property_metrics?.total_properties || 0,
      icon: <Building className="w-6 h-6" />,
      color: 'blue',
      trend: '+5%'
    },
    {
      title: 'Portfolio Value',
      value: `$${((data.financial_metrics?.portfolio_metrics?.portfolio_value || 0) / 1000000).toFixed(1)}M`,
      icon: <DollarSign className="w-6 h-6" />,
      color: 'green',
      trend: '+12%'
    },
    {
      title: 'Occupancy Rate',
      value: `${((data.property_metrics?.occupancy_rate || 0) * 100).toFixed(1)}%`,
      icon: <Users className="w-6 h-6" />,
      color: 'purple',
      trend: '+2%'
    },
    {
      title: 'AI Analyses',
      value: data.ai_metrics?.ai_utilization?.total_ai_analyses || 0,
      icon: <Brain className="w-6 h-6" />,
      color: 'orange',
      trend: '+25%'
    },
    {
      title: 'Processing Rate',
      value: `${((data.performance_metrics?.processing_rate || 0) * 100).toFixed(1)}%`,
      icon: <Zap className="w-6 h-6" />,
      color: 'indigo',
      trend: '+8%'
    },
    {
      title: 'Active Alerts',
      value: data.alert_metrics?.pending_alerts || 0,
      icon: <AlertTriangle className="w-6 h-6" />,
      color: 'red',
      trend: '-15%'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {kpis.map((kpi, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`bg-white rounded-lg p-6 border-l-4 ${
            kpi.color === 'blue' ? 'border-blue-500' :
            kpi.color === 'green' ? 'border-green-500' :
            kpi.color === 'purple' ? 'border-purple-500' :
            kpi.color === 'orange' ? border-orange-500' :
            kpi.color === 'indigo' ? 'border-indigo-500' :
            'border-red-500'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{kpi.title}</p>
              <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
            </div>
            <div className={`p-3 rounded-full ${
              kpi.color === 'blue' ? 'bg-blue-100 text-blue-600' :
              kpi.color === 'green' ? 'bg-green-100 text-green-600' :
              kpi.color === 'purple' ? 'bg-purple-100 text-purple-600' :
              kpi.color === 'orange' ? 'bg-orange-100 text-orange-600' :
              kpi.color === 'indigo' ? 'bg-indigo-100 text-indigo-600' :
              'bg-red-100 text-red-600'
            }`}>
              {kpi.icon}
            </div>
          </div>
          <div className="mt-2 flex items-center gap-1">
            <span className={`text-sm ${
              kpi.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'
            }`}>
              {kpi.trend}
            </span>
            <span className="text-xs text-gray-500">vs last month</span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// Property Metrics Chart
function PropertyMetricsChart({ data }) {
  const chartData = data?.properties_by_type ? Object.entries(data.properties_by_type) : [];

  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Properties by Type</h3>
        <PieChart className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        {chartData.map(([type, count], index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${
                index === 0 ? 'bg-blue-500' :
                index === 1 ? 'bg-green-500' :
                index === 2 ? 'bg-purple-500' :
                'bg-orange-500'
              }`}></div>
              <span className="text-sm text-gray-600 capitalize">{type}</span>
            </div>
            <span className="font-semibold">{count}</span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total Properties</span>
          <span className="font-semibold">{data?.total_properties || 0}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total Square Footage</span>
          <span className="font-semibold">{((data?.total_sqft || 0) / 1000).toFixed(0)}K sq ft</span>
        </div>
      </div>
    </div>
  );
}

// Financial Metrics Chart
function FinancialMetricsChart({ data }) {
  const portfolioMetrics = data?.portfolio_metrics || {};
  
  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Financial Performance</h3>
        <BarChart className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total NOI</span>
          <span className="font-semibold">${(portfolioMetrics.total_noi || 0).toLocaleString()}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Avg Cap Rate</span>
          <span className="font-semibold">{((portfolioMetrics.avg_cap_rate || 0) * 100).toFixed(2)}%</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Avg Occupancy</span>
          <span className="font-semibold">{((portfolioMetrics.avg_occupancy || 0) * 100).toFixed(1)}%</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Portfolio Value</span>
          <span className="font-semibold">${((portfolioMetrics.portfolio_value || 0) / 1000000).toFixed(1)}M</span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-gray-500">
          Based on {data?.metrics_count || 0} financial metrics
        </div>
      </div>
    </div>
  );
}

// Alert Metrics Chart
function AlertMetricsChart({ data }) {
  const alertLevels = data?.alerts_by_level || {};
  
  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Alert Status</h3>
        <AlertTriangle className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Recent Alerts</span>
          <span className="font-semibold">{data?.recent_alerts || 0}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Pending Alerts</span>
          <span className="font-semibold text-orange-600">{data?.pending_alerts || 0}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Active Locks</span>
          <span className="font-semibold text-red-600">{data?.active_locks || 0}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Recent Anomalies</span>
          <span className="font-semibold text-purple-600">{data?.recent_anomalies || 0}</span>
        </div>
      </div>
      
      {Object.keys(alertLevels).length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="text-sm font-medium text-gray-700 mb-2">Alerts by Level</div>
          {Object.entries(alertLevels).map(([level, count]) => (
            <div key={level} className="flex justify-between text-sm">
              <span className="text-gray-600 capitalize">{level}</span>
              <span className="font-semibold">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// AI Metrics Chart
function AIMetricsChart({ data }) {
  const aiUtilization = data?.ai_utilization || {};
  
  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">AI Performance</h3>
        <Brain className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Market Analyses</span>
          <span className="font-semibold">{data?.market_analyses || 0}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Exit Analyses</span>
          <span className="font-semibold">{data?.exit_analyses || 0}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Avg Confidence</span>
          <span className="font-semibold">{((data?.avg_confidence || 0) * 100).toFixed(1)}%</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total AI Analyses</span>
          <span className="font-semibold">{aiUtilization.total_ai_analyses || 0}</span>
        </div>
      </div>
      
      {Object.keys(data?.analysis_types || {}).length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="text-sm font-medium text-gray-700 mb-2">Analysis Types</div>
          {Object.entries(data.analysis_types).map(([type, count]) => (
            <div key={type} className="flex justify-between text-sm">
              <span className="text-gray-600 capitalize">{type.replace('_', ' ')}</span>
              <span className="font-semibold">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Performance Overview
function PerformanceOverview({ data }) {
  const systemHealth = data?.system_health || {};
  
  return (
    <div className="bg-white rounded-lg p-6 border">
      <h3 className="text-lg font-semibold mb-4">System Performance</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{data?.total_documents || 0}</div>
          <div className="text-sm text-gray-600">Total Documents</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {((data?.processing_rate || 0) * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Processing Rate</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{data?.recent_uploads || 0}</div>
          <div className="text-sm text-gray-600">Recent Uploads</div>
        </div>
        
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{data?.user_activity || 0}</div>
          <div className="text-sm text-gray-600">User Activity</div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">System Status</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-green-600">Operational</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Real-time Metrics Component
function RealTimeMetrics() {
  const [realTimeData, setRealTimeData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRealTimeData = async () => {
    try {
      const response = await fetch('/api/analytics/real-time-metrics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      setRealTimeData(data);
    } catch (error) {
      console.error('Error fetching real-time data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRealTimeData();
    
    // Update every 30 seconds
    const interval = setInterval(fetchRealTimeData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 border">
        <div className="flex items-center gap-2">
          <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          <span className="text-sm text-gray-600">Loading real-time metrics...</span>
        </div>
      </div>
    );
  }

  if (!realTimeData) {
    return null;
  }

  const indicators = realTimeData.real_time_indicators || {};

  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Real-time System Status</h3>
        <Activity className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${
              indicators.database_health === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">Database</span>
          </div>
          <div className="text-xs text-gray-600 capitalize">{indicators.database_health}</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${
              indicators.ai_services === 'available' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">AI Services</span>
          </div>
          <div className="text-xs text-gray-600 capitalize">{indicators.ai_services}</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${
              indicators.storage_health === 'operational' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">Storage</span>
          </div>
          <div className="text-xs text-gray-600 capitalize">{indicators.storage_health}</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${
              indicators.system_status === 'operational' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium">System</span>
          </div>
          <div className="text-xs text-gray-600 capitalize">{indicators.system_status}</div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
        Last updated: {new Date(indicators.last_update).toLocaleTimeString()}
      </div>
    </div>
  );
}

// Export Analytics Component
export function ExportAnalytics() {
  const [isExporting, setIsExporting] = useState(false);

  const exportData = async (format) => {
    setIsExporting(true);
    
    try {
      const response = await fetch(`/api/analytics/export-analytics?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      
      // Create download link
      const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg p-6 border">
      <h3 className="text-lg font-semibold mb-4">Export Analytics Data</h3>
      
      <div className="flex gap-4">
        <button
          onClick={() => exportData('json')}
          disabled={isExporting}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          {isExporting ? 'Exporting...' : 'Export JSON'}
        </button>
        
        <button
          onClick={() => exportData('csv')}
          disabled={isExporting}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          {isExporting ? 'Exporting...' : 'Export CSV'}
        </button>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        Export includes dashboard metrics, portfolio analytics, and KPI data
      </div>
    </div>
  );
}

