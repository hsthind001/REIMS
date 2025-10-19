import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  HomeIcon, 
  DocumentTextIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CalendarIcon,
  UserGroupIcon,
  BanknotesIcon,
  BuildingOfficeIcon,
  Cog6ToothIcon,
  BellIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  MapPinIcon,
  ClockIcon,
  Bars3Icon,
  PlusIcon,
  ArrowPathIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

const ModernExecutiveDashboard = () => {
  const [dateTime, setDateTime] = useState(new Date());
  const [kpiData, setKpiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('month');
  const [chatMessages, setChatMessages] = useState([
    { id: 1, type: 'system', message: 'Welcome to REIMS Executive Dashboard', time: '08:15' },
    { id: 2, type: 'alert', message: 'Property PROP001 maintenance completed', time: '08:12' },
    { id: 3, type: 'update', message: 'Monthly revenue report generated', time: '08:05' }
  ]);
  const [newMessage, setNewMessage] = useState('');

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
      } catch (err) {
        console.error('Failed to fetch KPI data:', err);
        // Use fallback data
        setKpiData({
          status: 'error_fallback',
          source: 'mock_data',
          timestamp: new Date().toISOString(),
          core_kpis: {
            total_portfolio_value: { value: 47800000, formatted: '$47.8M' },
            total_properties: { value: 184, occupied: 174, available: 10 },
            monthly_rental_income: { value: 1200000, formatted: '$1.2M' },
            occupancy_rate: { value: 94.6, formatted: '94.6%', occupied_units: 174, total_units: 184 }
          }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchKPIData();
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

  // KPI Cards Data
  const kpiCards = useMemo(() => {
    if (!kpiData?.core_kpis) return [];
    
    const { core_kpis } = kpiData;
    return [
      {
        title: 'Portfolio Value',
        value: core_kpis.total_portfolio_value.formatted,
        change: '+12.3%',
        trend: 'up',
        icon: BanknotesIcon,
        color: 'from-emerald-400 to-teal-600',
        bgColor: 'bg-emerald-50',
        textColor: 'text-emerald-700'
      },
      {
        title: 'Active Properties',
        value: core_kpis.total_properties.value.toString(),
        change: `${core_kpis.total_properties.occupied} occupied`,
        trend: 'up',
        icon: BuildingOfficeIcon,
        color: 'from-blue-400 to-indigo-600',
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-700'
      },
      {
        title: 'Monthly Revenue',
        value: core_kpis.monthly_rental_income.formatted,
        change: '+8.4%',
        trend: 'up',
        icon: CurrencyDollarIcon,
        color: 'from-purple-400 to-violet-600',
        bgColor: 'bg-purple-50',
        textColor: 'text-purple-700'
      },
      {
        title: 'Occupancy Rate',
        value: core_kpis.occupancy_rate.formatted,
        change: core_kpis.occupancy_rate.value > 90 ? '+excellent' : 'needs attention',
        trend: core_kpis.occupancy_rate.value > 90 ? 'up' : 'down',
        icon: UserGroupIcon,
        color: core_kpis.occupancy_rate.value > 90 ? 'from-emerald-400 to-teal-600' : 'from-orange-400 to-red-500',
        bgColor: core_kpis.occupancy_rate.value > 90 ? 'bg-emerald-50' : 'bg-orange-50',
        textColor: core_kpis.occupancy_rate.value > 90 ? 'text-emerald-700' : 'text-orange-700'
      }
    ];
  }, [kpiData]);

  // Chart data for visualization
  const chartData = [
    { month: 'Jan', revenue: 1.1, occupancy: 92 },
    { month: 'Feb', revenue: 1.15, occupancy: 94 },
    { month: 'Mar', revenue: 1.18, occupancy: 96 },
    { month: 'Apr', revenue: 1.2, occupancy: 95 },
    { month: 'May', revenue: 1.22, occupancy: 97 },
    { month: 'Jun', revenue: 1.25, occupancy: 94 }
  ];

  const propertyTypes = [
    { type: 'Residential', count: 120, color: 'bg-blue-500' },
    { type: 'Commercial', count: 45, color: 'bg-purple-500' },
    { type: 'Industrial', count: 19, color: 'bg-orange-500' }
  ];

  const addChatMessage = () => {
    if (!newMessage.trim()) return;
    
    const message = {
      id: Date.now(),
      type: 'user',
      message: newMessage,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
    
    setChatMessages(prev => [...prev, message]);
    setNewMessage('');
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'ai',
        message: 'I understand your query. Let me analyze the data and provide insights.',
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setChatMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4 overflow-hidden">
      {/* Modern Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 p-4 mb-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <HomeIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                REIMS Executive
              </h1>
              <p className="text-sm text-gray-500">Real Estate Intelligence & Management</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-700">
                {dateTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
              </div>
              <div className="text-lg font-bold text-blue-600">
                {dateTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <MagnifyingGlassIcon className="w-5 h-5 text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
                <BellIcon className="w-5 h-5 text-gray-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Cog6ToothIcon className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
        {/* Left Column - KPIs and Charts */}
        <div className="col-span-8 space-y-6">
          {/* KPI Cards */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-4 gap-4"
          >
            {kpiCards.map((kpi, index) => (
              <motion.div
                key={kpi.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`${kpi.bgColor} rounded-2xl p-4 border border-white/20 shadow-lg hover:shadow-xl transition-all duration-300 group cursor-pointer`}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-xl bg-gradient-to-r ${kpi.color} shadow-lg`}>
                    <kpi.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className={`flex items-center space-x-1 text-xs font-semibold ${
                    kpi.trend === 'up' ? 'text-emerald-600' : 'text-red-500'
                  }`}>
                    {kpi.trend === 'up' ? (
                      <TrendingUpIcon className="w-3 h-3" />
                    ) : (
                      <TrendingDownIcon className="w-3 h-3" />
                    )}
                    <span>{kpi.change}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-gray-600 font-medium uppercase tracking-wider">
                    {kpi.title}
                  </p>
                  <p className={`text-2xl font-bold ${kpi.textColor}`}>
                    {kpi.value}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Charts Section */}
          <div className="grid grid-cols-2 gap-6 h-64">
            {/* Revenue Chart */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/90 backdrop-blur-lg rounded-2xl p-6 shadow-xl border border-white/20"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-800">Revenue Trend</h3>
                <div className="flex space-x-2">
                  {['week', 'month', 'quarter'].map((period) => (
                    <button
                      key={period}
                      onClick={() => setSelectedTimeframe(period)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                        selectedTimeframe === period
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {period.charAt(0).toUpperCase() + period.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Simple Bar Chart */}
              <div className="flex items-end justify-between h-32 space-x-2">
                {chartData.map((data, index) => (
                  <div key={data.month} className="flex flex-col items-center flex-1">
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${(data.revenue / 1.25) * 100}%` }}
                      transition={{ delay: index * 0.1 }}
                      className="w-full bg-gradient-to-t from-blue-500 to-purple-600 rounded-t-lg mb-2"
                    />
                    <span className="text-xs text-gray-600 font-medium">{data.month}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Property Distribution */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/90 backdrop-blur-lg rounded-2xl p-6 shadow-xl border border-white/20"
            >
              <h3 className="text-lg font-bold text-gray-800 mb-4">Property Distribution</h3>
              <div className="space-y-4">
                {propertyTypes.map((type, index) => (
                  <motion.div
                    key={type.type}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full ${type.color}`} />
                      <span className="text-sm font-medium text-gray-700">{type.type}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold text-gray-800">{type.count}</span>
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(type.count / 120) * 60}px` }}
                        transition={{ delay: index * 0.1 + 0.3 }}
                        className={`h-2 rounded-full ${type.color}`}
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Action Buttons */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-4 gap-4"
          >
            {[
              { label: 'Add Property', icon: PlusIcon, color: 'from-green-500 to-emerald-600' },
              { label: 'Generate Report', icon: DocumentTextIcon, color: 'from-blue-500 to-indigo-600' },
              { label: 'View Analytics', icon: ChartBarIcon, color: 'from-purple-500 to-violet-600' },
              { label: 'Sync Data', icon: ArrowPathIcon, color: 'from-orange-500 to-red-600' }
            ].map((action, index) => (
              <motion.button
                key={action.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`bg-gradient-to-r ${action.color} text-white p-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-3 group`}
              >
                <action.icon className="w-5 h-5" />
                <span className="font-medium">{action.label}</span>
                <ChevronRightIcon className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            ))}
          </motion.div>
        </div>

        {/* Right Column - Chat & Activity */}
        <div className="col-span-4 space-y-6">
          {/* Data Status */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/90 backdrop-blur-lg rounded-2xl p-4 shadow-xl border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  kpiData?.source === 'database' ? 'bg-green-500 animate-pulse' : 'bg-orange-500'
                }`} />
                <span className="text-sm font-medium text-gray-700">
                  {loading ? 'Loading...' : kpiData?.source === 'database' ? 'Live Data' : 'Mock Data'}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {kpiData?.timestamp ? new Date(kpiData.timestamp).toLocaleTimeString() : '--:--'}
              </span>
            </div>
          </motion.div>

          {/* Chat Interface */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/90 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 flex flex-col h-96"
          >
            <div className="p-4 border-b border-gray-200 flex items-center space-x-3">
              <ChatBubbleLeftRightIcon className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-gray-800">AI Assistant</h3>
              <div className="flex-1" />
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
            
            <div className="flex-1 p-4 space-y-3 overflow-y-auto">
              <AnimatePresence>
                {chatMessages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs p-3 rounded-xl ${
                      msg.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : msg.type === 'ai'
                        ? 'bg-gray-100 text-gray-800'
                        : msg.type === 'alert'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      <p className="text-sm">{msg.message}</p>
                      <p className="text-xs opacity-75 mt-1">{msg.time}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addChatMessage()}
                  placeholder="Ask about your portfolio..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={addChatMessage}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Send
                </motion.button>
              </div>
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white/90 backdrop-blur-lg rounded-2xl p-4 shadow-xl border border-white/20"
          >
            <h3 className="font-bold text-gray-800 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { icon: MapPinIcon, label: 'View Properties Map', color: 'text-blue-600' },
                { icon: DocumentTextIcon, label: 'Monthly Report', color: 'text-green-600' },
                { icon: ClockIcon, label: 'Schedule Maintenance', color: 'text-orange-600' }
              ].map((action, index) => (
                <motion.button
                  key={action.label}
                  whileHover={{ scale: 1.02 }}
                  className="w-full flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-xl transition-all duration-200 group"
                >
                  <action.icon className={`w-5 h-5 ${action.color}`} />
                  <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
                    {action.label}
                  </span>
                  <div className="flex-1" />
                  <ChevronRightIcon className="w-4 h-4 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default ModernExecutiveDashboard;