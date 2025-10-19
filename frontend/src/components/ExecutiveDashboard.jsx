import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  HomeIcon, 
  DocumentTextIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EyeIcon,
  ArrowTopRightOnSquareIcon,
  CalendarIcon,
  UserGroupIcon,
  BanknotesIcon,
  BuildingOfficeIcon,
  Bars3Icon,
  BellIcon,
  Cog6ToothIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  PlusIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

const ExecutiveDashboard = () => {
  const [dateTime, setDateTime] = useState(new Date());
  const [selectedTimeframe, setSelectedTimeframe] = useState('month');
  const [animationKey, setAnimationKey] = useState(0);
  const [kpiData, setKpiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('overview');

  // Fetch KPI data from backend
  useEffect(() => {
    const fetchKPIData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8001/api/kpis/financial');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setKpiData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch KPI data:', err);
        setError(err.message);
        // Keep existing hardcoded data as fallback
      } finally {
        setLoading(false);
      }
    };

    fetchKPIData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchKPIData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Update date/time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setDateTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Trigger animation refresh when timeframe changes
  useEffect(() => {
    setAnimationKey(prev => prev + 1);
  }, [selectedTimeframe]);

  // Executive KPI data - now dynamic based on API response
  const kpis = useMemo(() => {
    // If we have real data from API, use it
    if (kpiData && kpiData.status === 'success') {
      const { core_kpis } = kpiData;
      return [
        {
          title: 'Total Portfolio Value',
          value: core_kpis.total_portfolio_value.formatted,
          change: '+12.3%', // TODO: Calculate from historical data
          trend: 'up',
          icon: BanknotesIcon,
          color: 'from-emerald-500 to-teal-600',
          bgColor: 'from-emerald-50 to-teal-50',
          description: 'Current market value',
          realTime: true
        },
        {
          title: 'Properties Under Management',
          value: core_kpis.total_properties.value.toString(),
          change: `${core_kpis.total_properties.occupied} occupied`,
          trend: 'up',
          icon: BuildingOfficeIcon,
          color: 'from-blue-500 to-indigo-600',
          bgColor: 'from-blue-50 to-indigo-50',
          description: `${core_kpis.total_properties.available} available`,
          realTime: true
        },
        {
          title: 'Monthly Rental Income',
          value: core_kpis.monthly_rental_income.formatted,
          change: '+8.4%', // TODO: Calculate from historical data
          trend: 'up',
          icon: CurrencyDollarIcon,
          color: 'from-purple-500 to-violet-600',
          bgColor: 'from-purple-50 to-violet-50',
          description: 'Current monthly income',
          realTime: true
        },
        {
          title: 'Occupancy Rate',
          value: core_kpis.occupancy_rate.formatted,
          change: core_kpis.occupancy_rate.value > 90 ? '+good' : '-needs attention',
          trend: core_kpis.occupancy_rate.value > 90 ? 'up' : 'down',
          icon: UserGroupIcon,
          color: core_kpis.occupancy_rate.value > 90 ? 'from-emerald-500 to-teal-600' : 'from-orange-500 to-red-500',
          bgColor: core_kpis.occupancy_rate.value > 90 ? 'from-emerald-50 to-teal-50' : 'from-orange-50 to-red-50',
          description: `${core_kpis.occupancy_rate.occupied_units}/${core_kpis.occupancy_rate.total_units} units occupied`,
          realTime: true
        }
      ];
    }
    
    // Fallback to hardcoded data if API is not available
    return [
      {
        title: 'Total Portfolio Value',
        value: '$47.8M',
        change: '+12.3%',
        trend: 'up',
        icon: BanknotesIcon,
        color: 'from-emerald-500 to-teal-600',
        bgColor: 'from-emerald-50 to-teal-50',
        description: 'Compared to last quarter',
        realTime: false
      },
      {
        title: 'Properties Under Management',
        value: '184',
        change: '+7',
        trend: 'up',
        icon: BuildingOfficeIcon,
        color: 'from-blue-500 to-indigo-600',
        bgColor: 'from-blue-50 to-indigo-50',
        description: 'Active properties',
        realTime: false
      },
      {
        title: 'Monthly Rental Income',
        value: '$1.2M',
        change: '+8.4%',
        trend: 'up',
        icon: CurrencyDollarIcon,
        color: 'from-purple-500 to-violet-600',
        bgColor: 'from-purple-50 to-violet-50',
        description: 'This month vs last month',
        realTime: false
      },
      {
        title: 'Occupancy Rate',
        value: '94.6%',
        change: '-1.2%',
        trend: 'down',
        icon: UserGroupIcon,
        color: 'from-orange-500 to-red-500',
        bgColor: 'from-orange-50 to-red-50',
        description: 'Current occupancy',
        realTime: false
      }
    ];
  }, [kpiData]);

  // Market insights data
  const marketInsights = [
    {
      title: 'Market Performance',
      value: 'Strong Growth',
      indicator: '+15.7%',
      description: 'YoY market appreciation in our regions',
      color: 'text-emerald-600'
    },
    {
      title: 'Investment Opportunities',
      value: '23 Properties',
      indicator: 'Available',
      description: 'Pre-screened investment opportunities',
      color: 'text-blue-600'
    },
    {
      title: 'Risk Assessment',
      value: 'Low Risk',
      indicator: '2.1/10',
      description: 'Portfolio risk score',
      color: 'text-green-600'
    }
  ];

  // Recent activity data
  const recentActivity = [
    {
      id: 1,
      type: 'acquisition',
      title: 'New Property Acquired',
      description: 'Luxury apartment complex in Downtown District',
      value: '$3.2M',
      time: '2 hours ago',
      icon: BuildingOfficeIcon,
      color: 'text-emerald-600'
    },
    {
      id: 2,
      type: 'rental',
      title: 'Major Lease Signed',
      description: 'Corporate client - 5 year agreement',
      value: '$24k/month',
      time: '5 hours ago',
      icon: DocumentTextIcon,
      color: 'text-blue-600'
    },
    {
      id: 3,
      type: 'maintenance',
      title: 'Renovation Completed',
      description: 'Premium office space renovation',
      value: '$450k',
      time: '1 day ago',
      icon: HomeIcon,
      color: 'text-purple-600'
    },
    {
      id: 4,
      type: 'financial',
      title: 'Quarterly Report',
      description: 'Q3 financial performance review',
      value: '+18.3%',
      time: '2 days ago',
      icon: ChartBarIcon,
      color: 'text-orange-600'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12
      }
    }
  };

  const KPICard = ({ kpi, index }) => (
    <motion.div
      key={`${kpi.title}-${animationKey}`}
      variants={itemVariants}
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${kpi.bgColor} p-6 shadow-lg hover:shadow-xl transition-all duration-300 group`}
      whileHover={{ 
        scale: 1.02,
        transition: { type: "spring", stiffness: 400, damping: 25 }
      }}
    >
      {/* Background Gradient Overlay */}
      <div className={`absolute inset-0 bg-gradient-to-br ${kpi.color} opacity-5 group-hover:opacity-10 transition-opacity duration-300`} />
      
      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${kpi.color} shadow-lg`}>
            <kpi.icon className="w-6 h-6 text-white" />
          </div>
          <div className="flex items-center space-x-2">
            {kpi.realTime && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-green-600 font-medium">LIVE</span>
              </div>
            )}
            <div className={`flex items-center space-x-1 text-sm font-semibold ${
              kpi.trend === 'up' ? 'text-emerald-600' : 'text-red-500'
            }`}>
              {kpi.trend === 'up' ? (
                <TrendingUpIcon className="w-4 h-4" />
              ) : (
                <TrendingDownIcon className="w-4 h-4" />
              )}
              <span>{kpi.change}</span>
            </div>
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wider">
            {kpi.title}
          </h3>
          <div className="text-3xl font-bold text-gray-900">
            {kpi.value}
          </div>
          <p className="text-sm text-gray-500">
            {kpi.description}
          </p>
        </div>
      </div>

      {/* Animated Background Element */}
      <motion.div
        className={`absolute -bottom-10 -right-10 w-24 h-24 bg-gradient-to-br ${kpi.color} rounded-full opacity-10`}
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 8 + index * 2,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </motion.div>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Executive Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <div className="inline-flex items-center space-x-3 px-6 py-3 bg-white/80 backdrop-blur-sm rounded-full shadow-lg border border-white/20">
          <CalendarIcon className="w-5 h-5 text-indigo-600" />
          <span className="text-gray-700 font-medium">
            {dateTime.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </span>
          <span className="text-gray-500">•</span>
          <span className="text-indigo-600 font-semibold">
            {dateTime.toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit'
            })}
          </span>
        </div>
        
        <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
          Executive Dashboard
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Comprehensive overview of your real estate portfolio performance and key business metrics
        </p>
      </motion.div>

      {/* Timeframe Selector */}
      <motion.div variants={itemVariants} className="flex justify-center">
        <div className="inline-flex bg-white/80 backdrop-blur-sm rounded-xl p-1 shadow-lg border border-white/20">
          {['week', 'month', 'quarter', 'year'].map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 capitalize ${
                selectedTimeframe === timeframe
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
              }`}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Loading and Error States */}
      {loading && (
        <motion.div variants={itemVariants} className="text-center py-8">
          <div className="inline-flex items-center space-x-3 px-6 py-3 bg-blue-50 rounded-full border border-blue-200">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-blue-700 font-medium">Loading financial KPIs...</span>
          </div>
        </motion.div>
      )}

      {error && (
        <motion.div variants={itemVariants} className="text-center py-8">
          <div className="inline-flex items-center space-x-3 px-6 py-3 bg-orange-50 rounded-full border border-orange-200">
            <span className="text-orange-700 font-medium">⚠️ Using cached data - Backend connection issue</span>
          </div>
        </motion.div>
      )}

      {/* Data Source Indicator */}
      {kpiData && (
        <motion.div variants={itemVariants} className="text-center">
          <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm ${
            kpiData.source === 'database' 
              ? 'bg-green-50 border border-green-200 text-green-700' 
              : 'bg-yellow-50 border border-yellow-200 text-yellow-700'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              kpiData.source === 'database' ? 'bg-green-500' : 'bg-yellow-500'
            } ${kpiData.source === 'database' ? 'animate-pulse' : ''}`} />
            <span>
              {kpiData.source === 'database' ? 'Live Data' : 'Mock Data'} • 
              Last updated: {new Date(kpiData.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </motion.div>
      )}

      {/* KPI Cards Grid */}
      <motion.div 
        variants={containerVariants}
        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
      >
        {kpis.map((kpi, index) => (
          <KPICard key={kpi.title} kpi={kpi} index={index} />
        ))}
      </motion.div>

      {/* Market Insights and Recent Activity */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Market Insights */}
        <motion.div 
          variants={itemVariants}
          className="xl:col-span-1 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20"
        >
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-amber-500 to-orange-600 rounded-lg">
              <TrendingUpIcon className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Market Insights</h2>
          </div>

          <div className="space-y-4">
            {marketInsights.map((insight, index) => (
              <motion.div
                key={insight.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-all duration-300"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                  <span className={`text-sm font-bold ${insight.color}`}>
                    {insight.indicator}
                  </span>
                </div>
                <p className="text-lg font-bold text-gray-900 mb-1">{insight.value}</p>
                <p className="text-sm text-gray-500">{insight.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div 
          variants={itemVariants}
          className="xl:col-span-2 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg">
                <EyeIcon className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
            </div>
            <button className="inline-flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors duration-200">
              <span>View All</span>
              <ArrowTopRightOnSquareIcon className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3">
            {recentActivity.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="flex items-center p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-all duration-300 group"
              >
                <div className={`p-2 rounded-lg bg-gradient-to-r ${
                  activity.type === 'acquisition' ? 'from-emerald-500 to-teal-600' :
                  activity.type === 'rental' ? 'from-blue-500 to-indigo-600' :
                  activity.type === 'maintenance' ? 'from-purple-500 to-violet-600' :
                  'from-orange-500 to-red-500'
                }`}>
                  <activity.icon className="w-5 h-5 text-white" />
                </div>
                
                <div className="ml-4 flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors duration-200">
                      {activity.title}
                    </h3>
                    <span className={`font-bold ${activity.color}`}>
                      {activity.value}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Executive Summary Card */}
      <motion.div 
        variants={itemVariants}
        className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-2xl p-8 text-white shadow-2xl"
      >
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Portfolio Performance Summary</h2>
          <p className="text-indigo-100 text-lg max-w-3xl mx-auto">
            Your real estate portfolio is performing exceptionally well with strong growth across all key metrics. 
            The 12.3% increase in portfolio value and 94.6% occupancy rate demonstrate excellent management and market positioning.
          </p>
          <div className="flex justify-center space-x-8 pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold">18.3%</div>
              <div className="text-indigo-200 text-sm">YoY Growth</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">$47.8M</div>
              <div className="text-indigo-200 text-sm">Total Value</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">184</div>
              <div className="text-indigo-200 text-sm">Properties</div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ExecutiveDashboard;