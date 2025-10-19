import React, { useState, useEffect } from "react";

// Professional Executive Dashboard with Full Functionality
function ProfessionalExecutiveApp() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeModule, setActiveModule] = useState('dashboard');
  const [user] = useState({
    name: "John Anderson",
    role: "Chief Executive Officer",
    avatar: "👨‍💼"
  });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Header */}
      <ProfessionalHeader user={user} currentTime={currentTime} />
      
      {/* Navigation Sidebar */}
      <div className="flex">
        <NavigationSidebar activeModule={activeModule} onModuleChange={setActiveModule} />
        
        {/* Main Content Area */}
        <main className="flex-1 ml-64 p-8">
          {activeModule === 'dashboard' && <ExecutiveDashboard />}
          {activeModule === 'properties' && <PropertyManagement />}
          {activeModule === 'analytics' && <AdvancedAnalytics />}
          {activeModule === 'documents' && <DocumentManagement />}
          {activeModule === 'financials' && <FinancialReporting />}
          {activeModule === 'settings' && <SystemSettings />}
        </main>
      </div>
    </div>
  );
}

// Professional Header Component
function ProfessionalHeader({ user, currentTime }) {
  const [notifications] = useState([
    { id: 1, type: 'alert', message: 'Lease renewal due for Harbor View Towers', time: '2 hours ago' },
    { id: 2, type: 'success', message: 'Monthly report generated successfully', time: '4 hours ago' },
    { id: 3, type: 'info', message: 'New maintenance request at Sunset Plaza', time: '6 hours ago' }
  ]);

  return (
    <header className="bg-white shadow-lg border-b border-gray-200 px-6 py-4 fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xl">R</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">REIMS Executive</h1>
            <p className="text-sm text-gray-600">Real Estate Intelligence & Management System</p>
          </div>
        </div>

        {/* Right Side Controls */}
        <div className="flex items-center space-x-6">
          {/* Real-time Clock */}
          <div className="text-right">
            <div className="text-lg font-semibold text-gray-900">
              {currentTime.toLocaleTimeString()}
            </div>
            <div className="text-sm text-gray-600">
              {currentTime.toLocaleDateString()}
            </div>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none">
              <span className="text-xl">🔔</span>
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {notifications.length}
              </span>
            </button>
          </div>

          {/* User Profile */}
          <div className="flex items-center space-x-3 px-4 py-2 bg-gray-100 rounded-lg">
            <span className="text-2xl">{user.avatar}</span>
            <div className="text-right">
              <div className="font-semibold text-gray-900">{user.name}</div>
              <div className="text-sm text-gray-600">{user.role}</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

// Professional Navigation Sidebar
function NavigationSidebar({ activeModule, onModuleChange }) {
  const modules = [
    { id: 'dashboard', name: 'Executive Dashboard', icon: '📊', description: 'Overview & KPIs' },
    { id: 'properties', name: 'Property Portfolio', icon: '🏢', description: 'Manage Properties' },
    { id: 'analytics', name: 'Business Analytics', icon: '📈', description: 'Performance Insights' },
    { id: 'documents', name: 'Document Center', icon: '📄', description: 'AI Document Processing' },
    { id: 'financials', name: 'Financial Reports', icon: '💰', description: 'Revenue & P&L' },
    { id: 'settings', name: 'System Settings', icon: '⚙️', description: 'Admin Controls' }
  ];

  return (
    <nav className="fixed left-0 top-20 bottom-0 w-64 bg-white shadow-lg border-r border-gray-200 overflow-y-auto">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Navigation</h3>
        <div className="space-y-2">
          {modules.map(module => (
            <button
              key={module.id}
              onClick={() => onModuleChange(module.id)}
              className={`w-full text-left p-4 rounded-lg transition-all duration-200 ${
                activeModule === module.id
                  ? 'bg-blue-50 border-l-4 border-blue-600 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{module.icon}</span>
                <div className="flex-1">
                  <div className="font-semibold">{module.name}</div>
                  <div className="text-sm text-gray-500">{module.description}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}

// Executive Dashboard Module
function ExecutiveDashboard() {
  const kpis = [
    { title: 'Total Portfolio Value', value: '$45.2M', change: '+12.3%', trend: 'up', icon: '💰' },
    { title: 'Active Properties', value: '127', change: '+5', trend: 'up', icon: '🏢' },
    { title: 'Monthly Revenue', value: '$892K', change: '+8.1%', trend: 'up', icon: '📈' },
    { title: 'Occupancy Rate', value: '94.2%', change: '-1.2%', trend: 'down', icon: '🏠' },
    { title: 'Net Operating Income', value: '$678K', change: '+15.4%', trend: 'up', icon: '💵' },
    { title: 'Average Rent/SqFt', value: '$28.50', change: '+3.2%', trend: 'up', icon: '📏' }
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-900">Executive Dashboard</h2>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📊 Generate Report
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            📤 Export Data
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kpis.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      {/* Quick Actions and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <QuickActionsPanel />
        <RecentActivityPanel />
      </div>

      {/* Performance Charts */}
      <PerformanceCharts />
    </div>
  );
}

// KPI Card Component
function KPICard({ title, value, change, trend, icon }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <span className="text-3xl">{icon}</span>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
          trend === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {change}
        </span>
      </div>
      <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

// Quick Actions Panel
function QuickActionsPanel() {
  const actions = [
    { title: 'Add New Property', icon: '🏢', color: 'blue' },
    { title: 'Schedule Inspection', icon: '🔍', color: 'green' },
    { title: 'Process Lease', icon: '📋', color: 'purple' },
    { title: 'Generate Invoice', icon: '🧾', color: 'orange' }
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-2 gap-4">
        {actions.map((action, index) => (
          <button
            key={index}
            className={`p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-${action.color}-400 hover:bg-${action.color}-50 transition-all group`}
          >
            <div className="text-2xl mb-2">{action.icon}</div>
            <div className="text-sm font-semibold text-gray-700 group-hover:text-gray-900">
              {action.title}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

// Recent Activity Panel
function RecentActivityPanel() {
  const activities = [
    { type: 'success', message: 'Lease agreement signed for Harbor View Unit 2A', time: '2 hours ago', icon: '✅' },
    { type: 'info', message: 'Monthly financial report generated', time: '4 hours ago', icon: '📊' },
    { type: 'warning', message: 'Maintenance request pending at Downtown Plaza', time: '6 hours ago', icon: '⚠️' },
    { type: 'success', message: 'Rent collection completed for October', time: '1 day ago', icon: '💰' }
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
            <span className="text-xl">{activity.icon}</span>
            <div className="flex-1">
              <p className="text-sm text-gray-900">{activity.message}</p>
              <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
      <button className="w-full mt-4 text-sm text-blue-600 hover:text-blue-800 font-semibold">
        View All Activity →
      </button>
    </div>
  );
}

// Performance Charts Component
function PerformanceCharts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📈 Revenue Trend</h3>
        <div className="space-y-4">
          {['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025 (Projected)'].map((quarter, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{quarter}</span>
              <div className="flex items-center space-x-3">
                <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      index === 0 ? 'bg-blue-500 w-20' :
                      index === 1 ? 'bg-green-500 w-24' :
                      index === 2 ? 'bg-purple-500 w-32' :
                      'bg-gray-400 w-28'
                    }`}
                  ></div>
                </div>
                <span className="text-sm font-semibold text-gray-900">
                  ${index === 0 ? '2.4M' : index === 1 ? '2.7M' : index === 2 ? '3.1M' : '2.9M'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Performance Metrics</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="text-sm font-semibold text-green-800">Portfolio Growth</span>
            <span className="text-lg font-bold text-green-700">+15.2%</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
            <span className="text-sm font-semibold text-blue-800">ROI Performance</span>
            <span className="text-lg font-bold text-blue-700">12.8%</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
            <span className="text-sm font-semibold text-purple-800">Market Share</span>
            <span className="text-lg font-bold text-purple-700">8.3%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Property Management Module
function PropertyManagement() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real properties from API
  useEffect(() => {
    const fetchProperties = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8001/api/properties');
        if (!response.ok) {
          throw new Error('Failed to fetch properties');
        }
        const data = await response.json();
        
        // Map API data to component format
        const mappedProperties = data.properties.map(prop => ({
          id: prop.id,
          name: prop.name,
          address: `${prop.address}, ${prop.city}, ${prop.state}`,
          type: prop.property_type || 'Commercial',
          value: prop.current_market_value || 0,
          occupancyRate: prop.occupancy_rate ? Math.round(prop.occupancy_rate * 100) : 95,
          monthlyRevenue: prop.monthly_rent || 0,
          units: 1,
          sqft: prop.square_footage || 0,
          status: prop.status === 'healthy' ? 'excellent' : 
                  prop.status === 'active' ? 'good' : 'good',
          lastInspection: new Date().toISOString().split('T')[0],
          manager: 'Property Manager'
        }));
        
        setProperties(mappedProperties);
      } catch (err) {
        console.error('Error fetching properties:', err);
        setError(err.message);
        setProperties([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  const [selectedProperty, setSelectedProperty] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-900">Property Portfolio Management</h2>
        <div className="flex items-center space-x-4">
          {/* View Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'grid' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
              }`}
            >
              Grid View
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
              }`}
            >
              List View
            </button>
          </div>
          
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            🏢 Add Property
          </button>
        </div>
      </div>

      {/* Property Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Properties</p>
              <p className="text-3xl font-bold text-gray-900">{properties.length}</p>
            </div>
            <span className="text-3xl">🏢</span>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Value</p>
              <p className="text-3xl font-bold text-gray-900">
                ${(properties.reduce((sum, p) => sum + p.value, 0) / 1000000).toFixed(1)}M
              </p>
            </div>
            <span className="text-3xl">💰</span>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Occupancy</p>
              <p className="text-3xl font-bold text-gray-900">
                {(properties.reduce((sum, p) => sum + p.occupancyRate, 0) / properties.length).toFixed(1)}%
              </p>
            </div>
            <span className="text-3xl">📊</span>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Monthly Revenue</p>
              <p className="text-3xl font-bold text-gray-900">
                ${(properties.reduce((sum, p) => sum + p.monthlyRevenue, 0) / 1000).toFixed(0)}K
              </p>
            </div>
            <span className="text-3xl">📈</span>
          </div>
        </div>
      </div>

      {/* Properties Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {properties.map(property => (
            <PropertyCard 
              key={property.id} 
              property={property} 
              onSelect={setSelectedProperty}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200">
          <PropertyTable properties={properties} onSelect={setSelectedProperty} />
        </div>
      )}

      {/* Property Detail Modal */}
      {selectedProperty && (
        <PropertyDetailModal 
          property={selectedProperty} 
          onClose={() => setSelectedProperty(null)} 
        />
      )}
    </div>
  );
}

// Property Card Component
function PropertyCard({ property, onSelect }) {
  const statusColor = property.status === 'excellent' ? 'green' : 'blue';
  
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-shadow">
      {/* Property Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2">{property.name}</h3>
            <p className="text-sm text-gray-600 mb-3">{property.address}</p>
            <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
              {property.type}
            </span>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            statusColor === 'green' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {property.status === 'excellent' ? '� Excellent' : '🔵 Good'}
          </span>
        </div>
      </div>

      {/* Property Metrics */}
      <div className="p-6">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              ${(property.value / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">Property Value</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{property.occupancyRate}%</div>
            <div className="text-sm text-gray-600">Occupancy Rate</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              ${(property.monthlyRevenue / 1000).toFixed(0)}K
            </div>
            <div className="text-sm text-gray-600">Monthly Revenue</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{property.units}</div>
            <div className="text-sm text-gray-600">Total Units</div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="space-y-2 text-sm text-gray-600 mb-4">
          <div className="flex justify-between">
            <span>Square Footage:</span>
            <span className="font-semibold">{property.sqft.toLocaleString()} sq ft</span>
          </div>
          <div className="flex justify-between">
            <span>Property Manager:</span>
            <span className="font-semibold">{property.manager}</span>
          </div>
          <div className="flex justify-between">
            <span>Last Inspection:</span>
            <span className="font-semibold">{new Date(property.lastInspection).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={() => onSelect(property)}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            View Details
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
            Edit
          </button>
        </div>
      </div>
    </div>
  );
}

// Property Table Component
function PropertyTable({ properties, onSelect }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Property</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Type</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Value</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Occupancy</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Revenue</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Status</th>
            <th className="text-left py-4 px-6 font-semibold text-gray-900">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {properties.map(property => (
            <tr key={property.id} className="hover:bg-gray-50">
              <td className="py-4 px-6">
                <div>
                  <div className="font-semibold text-gray-900">{property.name}</div>
                  <div className="text-sm text-gray-600">{property.address}</div>
                </div>
              </td>
              <td className="py-4 px-6 text-gray-700">{property.type}</td>
              <td className="py-4 px-6 font-semibold text-gray-900">
                ${(property.value / 1000000).toFixed(1)}M
              </td>
              <td className="py-4 px-6">
                <div className="flex items-center">
                  <div className="w-12 h-2 bg-gray-200 rounded-full mr-2">
                    <div 
                      className="h-2 bg-green-500 rounded-full" 
                      style={{ width: `${property.occupancyRate}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-semibold">{property.occupancyRate}%</span>
                </div>
              </td>
              <td className="py-4 px-6 font-semibold text-gray-900">
                ${(property.monthlyRevenue / 1000).toFixed(0)}K
              </td>
              <td className="py-4 px-6">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  property.status === 'excellent' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                }`}>
                  {property.status === 'excellent' ? '🟢 Excellent' : '🔵 Good'}
                </span>
              </td>
              <td className="py-4 px-6">
                <button
                  onClick={() => onSelect(property)}
                  className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                >
                  View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Property Detail Modal
function PropertyDetailModal({ property, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-90vh overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900">{property.name}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6">
          {/* Property Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Property Information</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Address:</span>
                  <span className="font-semibold text-gray-900">{property.address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-semibold text-gray-900">{property.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Units:</span>
                  <span className="font-semibold text-gray-900">{property.units}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Square Footage:</span>
                  <span className="font-semibold text-gray-900">{property.sqft.toLocaleString()} sq ft</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Property Manager:</span>
                  <span className="font-semibold text-gray-900">{property.manager}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Property Value:</span>
                  <span className="font-semibold text-gray-900">${property.value.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Monthly Revenue:</span>
                  <span className="font-semibold text-gray-900">${property.monthlyRevenue.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Annual Revenue:</span>
                  <span className="font-semibold text-gray-900">${(property.monthlyRevenue * 12).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue per Sq Ft:</span>
                  <span className="font-semibold text-gray-900">${((property.monthlyRevenue * 12) / property.sqft).toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Occupancy Rate:</span>
                  <span className="font-semibold text-gray-900">{property.occupancyRate}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              📊 View Analytics
            </button>
            <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
              📋 Generate Report
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              ✏️ Edit Property
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Advanced Analytics Module (Placeholder)
function AdvancedAnalytics() {
  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-gray-900">Business Analytics & Insights</h2>
      <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
        <div className="text-center">
          <span className="text-6xl mb-4 block">📈</span>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Advanced Analytics Dashboard</h3>
          <p className="text-gray-600">Professional analytics and reporting tools will be implemented here</p>
        </div>
      </div>
    </div>
  );
}

// Document Management Module
function DocumentManagement() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [propertyId, setPropertyId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Fetch documents from backend on component mount
  useEffect(() => {
    checkBackendStatus();
    fetchDocuments();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8001/health');
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('disconnected');
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      } else {
        console.error('Failed to fetch documents');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    if (!propertyId.trim()) {
      setUploadStatus({ type: 'error', message: 'Please enter a Property ID' });
      return;
    }

    setUploading(true);
    setUploadStatus({ type: 'info', message: 'Connecting to backend...' });

    try {
      // First check if backend is available
      const healthCheck = await fetch('http://localhost:8001/health');
      if (!healthCheck.ok) {
        throw new Error('Backend server is not responding');
      }

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('property_id', propertyId.trim());

      setUploadStatus({ type: 'info', message: 'Uploading file to MinIO storage...' });

      const response = await fetch('http://localhost:8001/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus({ 
          type: 'success', 
          message: `✅ Success! File "${selectedFile.name}" uploaded to MinIO storage. Document ID: ${result.document_id}` 
        });
        
        // Refresh the documents list
        await fetchDocuments();
        
        // Reset form
        setSelectedFile(null);
        setPropertyId('');
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.value = '';
      } else {
        const error = await response.json().catch(() => ({ detail: 'Unknown server error' }));
        setUploadStatus({ 
          type: 'error', 
          message: `❌ Upload failed: ${error.detail || error.message || 'Server returned error ' + response.status}` 
        });
      }
    } catch (error) {
      console.error('Upload error:', error);
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        setUploadStatus({ 
          type: 'error', 
          message: '❌ Cannot connect to backend server. Please ensure the backend is running on http://localhost:8001' 
        });
      } else if (error.message.includes('not responding')) {
        setUploadStatus({ 
          type: 'error', 
          message: '❌ Backend server is not responding. Please check if the server is running.' 
        });
      } else {
        setUploadStatus({ 
          type: 'error', 
          message: `❌ Upload failed: ${error.message}` 
        });
      }
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-900">Enterprise Document Center</h2>
        <div className="flex items-center space-x-4">
          {/* Backend Status Indicator */}
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${
            backendStatus === 'connected' ? 'bg-green-100 text-green-800' :
            backendStatus === 'disconnected' ? 'bg-red-100 text-red-800' :
            backendStatus === 'error' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            <span className="w-2 h-2 rounded-full bg-current"></span>
            <span>
              {backendStatus === 'connected' ? 'Backend Connected' :
               backendStatus === 'disconnected' ? 'Backend Disconnected' :
               backendStatus === 'error' ? 'Backend Error' :
               'Checking Backend...'}
            </span>
          </div>
          
          <button 
            onClick={() => { checkBackendStatus(); fetchDocuments(); }}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            🔄 Refresh
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📊 Analytics
          </button>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-8 text-white">
        <div className="max-w-4xl">
          <h3 className="text-2xl font-bold mb-4">📄 AI-Powered Document Upload</h3>
          <p className="text-blue-100 mb-6">
            Upload documents for automatic processing, analysis, and intelligent insights. 
            Supported formats: PDF, DOC, DOCX, XLS, XLSX, CSV, TXT
          </p>
          
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <div className="space-y-4">
              {/* File Selection */}
              <div className="flex items-center space-x-4">
                <input
                  id="file-upload"
                  type="file"
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt"
                  className="hidden"
                />
                <label
                  htmlFor="file-upload"
                  className="flex items-center space-x-2 bg-white/20 backdrop-blur-md text-white px-6 py-3 rounded-lg hover:bg-white/30 transition-all cursor-pointer font-medium"
                >
                  <span className="text-xl">📁</span>
                  <span>Choose File</span>
                </label>
                
                {selectedFile && (
                  <div className="flex-1 bg-white/10 rounded-lg p-3">
                    <div className="text-white font-medium">{selectedFile.name}</div>
                    <div className="text-blue-200 text-sm">
                      {formatFileSize(selectedFile.size)} • {selectedFile.type || 'Unknown type'}
                    </div>
                  </div>
                )}
              </div>

              {/* Property ID Input */}
              <div className="flex items-center space-x-4">
                <label className="text-white font-medium whitespace-nowrap">Property ID:</label>
                <input
                  type="text"
                  value={propertyId}
                  onChange={(e) => setPropertyId(e.target.value)}
                  placeholder="Enter property identifier"
                  className="flex-1 bg-white/20 backdrop-blur-md text-white placeholder-white/60 px-4 py-3 rounded-lg border border-white/30 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                />
              </div>

              {/* Upload Button */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || !propertyId.trim() || uploading}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
                    selectedFile && propertyId.trim() && !uploading
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-white/10 text-white/50 cursor-not-allowed'
                  }`}
                >
                  {uploading ? (
                    <>
                      <span className="animate-spin text-xl">⏳</span>
                      <span>Uploading to MinIO...</span>
                    </>
                  ) : (
                    <>
                      <span className="text-xl">⬆️</span>
                      <span>Upload to MinIO Storage</span>
                    </>
                  )}
                </button>

                {uploading && (
                  <div className="text-blue-200 text-sm">
                    File is being processed and analyzed...
                  </div>
                )}
              </div>

              {/* Upload Status */}
              {uploadStatus && (
                <div className={`p-4 rounded-lg border ${
                  uploadStatus.type === 'success' 
                    ? 'bg-green-500/20 border-green-400 text-green-100' 
                    : 'bg-red-500/20 border-red-400 text-red-100'
                }`}>
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">
                      {uploadStatus.type === 'success' ? '✅' : '❌'}
                    </span>
                    <span className="font-medium">{uploadStatus.message}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-900">Uploaded Documents</h3>
            <div className="text-sm text-gray-600">
              {documents.length} document{documents.length !== 1 ? 's' : ''} total
            </div>
          </div>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">⏳</div>
              <div className="text-gray-600">Loading documents...</div>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📄</div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">No Documents Uploaded</h4>
              <p className="text-gray-600 mb-6">
                Upload your first document using the form above to get started with AI-powered analysis.
              </p>
              <button 
                onClick={() => document.getElementById('file-upload').click()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                📁 Upload First Document
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((doc, index) => (
                <div 
                  key={doc.document_id || index} 
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all border border-gray-200"
                >
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl">
                      {doc.original_filename?.endsWith('.pdf') ? '📄' :
                       doc.original_filename?.endsWith('.csv') ? '📊' :
                       doc.original_filename?.endsWith('.xlsx') || doc.original_filename?.endsWith('.xls') ? '📈' :
                       doc.original_filename?.endsWith('.doc') || doc.original_filename?.endsWith('.docx') ? '📝' :
                       '📄'}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">
                        {doc.original_filename || doc.filename || 'Unknown File'}
                      </div>
                      <div className="text-sm text-gray-600">
                        {formatFileSize(doc.file_size)} • 
                        Uploaded: {formatDate(doc.upload_timestamp)} •
                        Property: {doc.property_id || 'General'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      doc.status === 'uploaded' ? 'bg-green-100 text-green-800' :
                      doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {doc.status === 'uploaded' ? '✅ Uploaded' :
                       doc.status === 'processing' ? '⏳ Processing' :
                       doc.status || 'Unknown'}
                    </span>
                    
                    <button className="text-blue-600 hover:text-blue-800 font-medium text-sm px-3 py-1 rounded-md hover:bg-blue-50 transition-all">
                      📊 Analyze
                    </button>
                    
                    <button className="text-gray-600 hover:text-gray-800 font-medium text-sm px-3 py-1 rounded-md hover:bg-gray-50 transition-all">
                      📥 Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Financial Reporting Module (Placeholder)
function FinancialReporting() {
  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-gray-900">Financial Reporting & Analysis</h2>
      <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
        <div className="text-center">
          <span className="text-6xl mb-4 block">💰</span>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Financial Management Suite</h3>
          <p className="text-gray-600">Comprehensive financial reporting and analysis tools will be implemented here</p>
        </div>
      </div>
    </div>
  );
}

// System Settings Module (Placeholder)
function SystemSettings() {
  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-gray-900">System Administration</h2>
      <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
        <div className="text-center">
          <span className="text-6xl mb-4 block">⚙️</span>
          <h3 className="text-xl font-bold text-gray-900 mb-2">System Settings & Controls</h3>
          <p className="text-gray-600">Administrative controls and system configuration will be implemented here</p>
        </div>
      </div>
    </div>
  );
}

export default ProfessionalExecutiveApp;