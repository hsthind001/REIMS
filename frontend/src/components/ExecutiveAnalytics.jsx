import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  ArrowTopRightOnSquareIcon,
  DocumentChartBarIcon,
  BanknotesIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  PresentationChartLineIcon,
  ClockIcon,
  StarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const ExecutiveAnalytics = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('month');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    setAnimationKey(prev => prev + 1);
  }, [selectedTimeframe, selectedMetric]);

  // Mock analytics data
  const analyticsData = {
    revenue: {
      current: 1847000,
      previous: 1623000,
      growth: 13.8,
      trend: 'up',
      forecast: 2100000,
      breakdown: [
        { month: 'Jan', value: 1520000 },
        { month: 'Feb', value: 1680000 },
        { month: 'Mar', value: 1750000 },
        { month: 'Apr', value: 1690000 },
        { month: 'May', value: 1820000 },
        { month: 'Jun', value: 1847000 }
      ]
    },
    occupancy: {
      current: 94.6,
      previous: 91.2,
      growth: 3.7,
      trend: 'up',
      forecast: 96.1,
      breakdown: [
        { month: 'Jan', value: 89.5 },
        { month: 'Feb', value: 90.8 },
        { month: 'Mar', value: 92.1 },
        { month: 'Apr', value: 91.5 },
        { month: 'May', value: 93.2 },
        { month: 'Jun', value: 94.6 }
      ]
    },
    expenses: {
      current: 425000,
      previous: 398000,
      growth: 6.8,
      trend: 'up',
      forecast: 445000,
      breakdown: [
        { month: 'Jan', value: 380000 },
        { month: 'Feb', value: 395000 },
        { month: 'Mar', value: 410000 },
        { month: 'Apr', value: 402000 },
        { month: 'May', value: 418000 },
        { month: 'Jun', value: 425000 }
      ]
    },
    roi: {
      current: 12.3,
      previous: 10.8,
      growth: 13.9,
      trend: 'up',
      forecast: 13.1,
      breakdown: [
        { month: 'Jan', value: 9.8 },
        { month: 'Feb', value: 10.2 },
        { month: 'Mar', value: 11.1 },
        { month: 'Apr', value: 10.9 },
        { month: 'May', value: 11.8 },
        { month: 'Jun', value: 12.3 }
      ]
    }
  };

  const keyInsights = [
    {
      title: 'Revenue Growth Acceleration',
      description: 'Monthly revenue has increased by 13.8% compared to last period, driven by new lease signings and rent adjustments.',
      impact: 'high',
      trend: 'positive',
      value: '+$224K',
      actionRequired: false
    },
    {
      title: 'Occupancy Rate Optimization',
      description: 'Portfolio occupancy reached 94.6%, exceeding industry average of 92%. Prime properties showing strongest performance.',
      impact: 'medium',
      trend: 'positive',
      value: '+3.4%',
      actionRequired: false
    },
    {
      title: 'Maintenance Cost Alert',
      description: 'Maintenance expenses increased 15% this quarter. Industrial properties require attention to prevent escalation.',
      impact: 'medium',
      trend: 'negative',
      value: '+$63K',
      actionRequired: true
    },
    {
      title: 'Market Expansion Opportunity',
      description: 'Analysis shows potential 8-12% ROI improvement in emerging downtown district. Recommend market study.',
      impact: 'high',
      trend: 'opportunity',
      value: 'Est. +8-12%',
      actionRequired: true
    }
  ];

  const performanceMetrics = [
    {
      title: 'Portfolio Performance',
      value: '12.3%',
      change: '+1.5%',
      trend: 'up',
      icon: PresentationChartLineIcon,
      color: 'from-emerald-500 to-teal-600',
      description: 'Average ROI across all properties'
    },
    {
      title: 'Tenant Retention',
      value: '89.2%',
      change: '+2.1%',
      trend: 'up',
      icon: UserGroupIcon,
      color: 'from-blue-500 to-indigo-600',
      description: 'Annual tenant retention rate'
    },
    {
      title: 'Average Lease Duration',
      value: '3.2 years',
      change: '+0.3',
      trend: 'up',
      icon: ClockIcon,
      color: 'from-purple-500 to-violet-600',
      description: 'Portfolio average lease term'
    },
    {
      title: 'Property Rating',
      value: '4.7/5',
      change: '+0.2',
      trend: 'up',
      icon: StarIcon,
      color: 'from-orange-500 to-red-500',
      description: 'Tenant satisfaction score'
    }
  ];

  const propertyTypeAnalysis = [
    { type: 'Commercial', revenue: 680000, growth: 15.2, properties: 45, color: 'from-emerald-400 to-teal-500' },
    { type: 'Residential', revenue: 520000, growth: 8.7, properties: 89, color: 'from-blue-400 to-indigo-500' },
    { type: 'Industrial', revenue: 425000, growth: 6.3, properties: 32, color: 'from-purple-400 to-violet-500' },
    { type: 'Luxury', revenue: 322000, growth: 22.1, properties: 18, color: 'from-orange-400 to-red-500' }
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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value);
  };

  const MetricCard = ({ metric, index }) => (
    <motion.div
      key={`${metric.title}-${animationKey}`}
      variants={itemVariants}
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${metric.color} p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300`}
      whileHover={{ 
        scale: 1.02,
        transition: { type: "spring", stiffness: 400, damping: 25 }
      }}
    >
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <metric.icon className="w-8 h-8 text-white/80" />
          <div className={`flex items-center space-x-1 text-sm font-semibold ${
            metric.trend === 'up' ? 'text-emerald-200' : 'text-red-200'
          }`}>
            {metric.trend === 'up' ? (
              <TrendingUpIcon className="w-4 h-4" />
            ) : (
              <TrendingDownIcon className="w-4 h-4" />
            )}
            <span>{metric.change}</span>
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-white/80 uppercase tracking-wider">
            {metric.title}
          </h3>
          <div className="text-3xl font-bold text-white">
            {metric.value}
          </div>
          <p className="text-sm text-white/70">
            {metric.description}
          </p>
        </div>
      </div>

      {/* Animated background element */}
      <motion.div
        className="absolute -bottom-8 -right-8 w-20 h-20 bg-white/10 rounded-full"
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

  const ChartVisualization = ({ data, title }) => (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
      <h3 className="text-xl font-bold text-gray-900 mb-6">{title}</h3>
      <div className="space-y-4">
        {data.breakdown.map((item, index) => (
          <motion.div
            key={item.month}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index }}
            className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-100"
          >
            <span className="font-medium text-gray-700">{item.month}</span>
            <div className="flex items-center space-x-3">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <motion.div
                  className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.value / Math.max(...data.breakdown.map(d => d.value))) * 100}%` }}
                  transition={{ delay: 0.2 + index * 0.1, duration: 0.8 }}
                />
              </div>
              <span className="font-bold text-gray-900 min-w-[80px] text-right">
                {selectedMetric === 'revenue' || selectedMetric === 'expenses' 
                  ? formatCurrency(item.value)
                  : selectedMetric === 'roi'
                  ? `${item.value}%`
                  : `${item.value}%`
                }
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Analytics Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
          Business Intelligence
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Advanced analytics and insights to drive strategic decision-making across your real estate portfolio
        </p>
      </motion.div>

      {/* Control Panel */}
      <motion.div variants={itemVariants} className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Time Period:</span>
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {['week', 'month', 'quarter', 'year'].map((period) => (
              <button
                key={period}
                onClick={() => setSelectedTimeframe(period)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 capitalize ${
                  selectedTimeframe === period
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {period}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Focus Metric:</span>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
          >
            <option value="revenue">Revenue Analysis</option>
            <option value="occupancy">Occupancy Trends</option>
            <option value="expenses">Expense Management</option>
            <option value="roi">ROI Performance</option>
          </select>
        </div>
      </motion.div>

      {/* Performance Metrics Grid */}
      <motion.div 
        variants={containerVariants}
        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
      >
        {performanceMetrics.map((metric, index) => (
          <MetricCard key={metric.title} metric={metric} index={index} />
        ))}
      </motion.div>

      {/* Main Analytics Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Chart Visualization */}
        <motion.div variants={itemVariants} className="xl:col-span-2">
          <ChartVisualization 
            data={analyticsData[selectedMetric]} 
            title={`${selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)} Trend Analysis`}
          />
        </motion.div>

        {/* Property Type Performance */}
        <motion.div variants={itemVariants} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Property Type Performance</h3>
          <div className="space-y-4">
            {propertyTypeAnalysis.map((type, index) => (
              <motion.div
                key={type.type}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100"
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-gray-900">{type.type}</h4>
                  <span className={`text-sm font-bold ${
                    type.growth > 10 ? 'text-emerald-600' : type.growth > 5 ? 'text-blue-600' : 'text-orange-600'
                  }`}>
                    +{type.growth}%
                  </span>
                </div>
                <div className="text-lg font-bold text-gray-900 mb-1">
                  {formatCurrency(type.revenue)}
                </div>
                <div className="text-sm text-gray-500 mb-3">
                  {type.properties} properties
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className={`bg-gradient-to-r ${type.color} h-2 rounded-full`}
                    initial={{ width: 0 }}
                    animate={{ width: `${(type.revenue / Math.max(...propertyTypeAnalysis.map(p => p.revenue))) * 100}%` }}
                    transition={{ delay: 0.3 + index * 0.1, duration: 0.8 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Key Insights */}
      <motion.div variants={itemVariants} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
        <div className="flex items-center space-x-3 mb-6">
          <DocumentChartBarIcon className="w-6 h-6 text-indigo-600" />
          <h2 className="text-2xl font-bold text-gray-900">Strategic Insights & Recommendations</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {keyInsights.map((insight, index) => (
            <motion.div
              key={insight.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className={`p-5 rounded-xl border-l-4 ${
                insight.impact === 'high' 
                  ? 'bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-500'
                  : insight.impact === 'medium'
                  ? 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-500'
                  : 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-500'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-bold text-gray-900 text-lg">{insight.title}</h3>
                <div className="flex items-center space-x-2">
                  {insight.actionRequired && (
                    <ExclamationTriangleIcon className="w-5 h-5 text-orange-500" />
                  )}
                  <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                    insight.trend === 'positive' 
                      ? 'bg-emerald-100 text-emerald-700'
                      : insight.trend === 'negative'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {insight.value}
                  </span>
                </div>
              </div>
              <p className="text-gray-700 text-sm leading-relaxed">
                {insight.description}
              </p>
              {insight.actionRequired && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <button className="text-sm font-medium text-indigo-600 hover:text-indigo-700 flex items-center space-x-1">
                    <span>View Action Plan</span>
                    <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Executive Summary */}
      <motion.div 
        variants={itemVariants}
        className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 rounded-2xl p-8 text-white shadow-2xl"
      >
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Executive Summary</h2>
          <p className="text-indigo-100 text-lg max-w-4xl mx-auto">
            Portfolio performance remains strong with revenue growth of 13.8% and occupancy at 94.6%. 
            Strategic focus should be on maintenance cost optimization and expansion opportunities in emerging markets. 
            Current trajectory supports projected 15% ROI improvement over the next 12 months.
          </p>
          <div className="flex justify-center space-x-8 pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold">+13.8%</div>
              <div className="text-indigo-200 text-sm">Revenue Growth</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">94.6%</div>
              <div className="text-indigo-200 text-sm">Occupancy Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">12.3%</div>
              <div className="text-indigo-200 text-sm">Portfolio ROI</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">$1.85M</div>
              <div className="text-indigo-200 text-sm">Monthly Revenue</div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ExecutiveAnalytics;