import React, { useState, useEffect } from 'react';
import { API_CONFIG, buildApiUrl } from '../config/api';

const PropertyManagement = () => {
  const [properties, setProperties] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [leases, setLeases] = useState([]);
  const [maintenanceRequests, setMaintenanceRequests] = useState([]);
  const [activeTab, setActiveTab] = useState('properties');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch data based on active tab
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = '';
      switch (activeTab) {
        case 'properties':
          endpoint = '/api/property/properties';
          break;
        case 'tenants':
          endpoint = '/api/property/tenants';
          break;
        case 'leases':
          endpoint = '/api/property/leases';
          break;
        case 'maintenance':
          endpoint = '/api/property/maintenance';
          break;
        default:
          endpoint = '/api/property/properties';
      }

      const response = await fetch(buildApiUrl(endpoint));
      if (!response.ok) {
        throw new Error(`Failed to fetch ${activeTab}`);
      }
      const data = await response.json();
      
      switch (activeTab) {
        case 'properties':
          setProperties(data);
          break;
        case 'tenants':
          setTenants(data);
          break;
        case 'leases':
          setLeases(data);
          break;
        case 'maintenance':
          setMaintenanceRequests(data);
          break;
      }
    } catch (err) {
      setError(`Error loading ${activeTab}: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'occupied':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'unavailable':
        return 'bg-red-100 text-red-800';
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderProperties = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {properties.map((property) => (
        <div key={property.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-gray-900">{property.name}</h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(property.status)}`}>
              {property.status}
            </span>
          </div>
          
          <div className="space-y-2 text-sm text-gray-600">
            <p><span className="font-medium">Code:</span> {property.property_code}</p>
            <p><span className="font-medium">Type:</span> {property.property_type}</p>
            <p><span className="font-medium">Address:</span> {property.address}</p>
            <p><span className="font-medium">City:</span> {property.city}, {property.state}</p>
            {property.square_footage && (
              <p><span className="font-medium">Size:</span> {property.square_footage} sq ft</p>
            )}
            {property.bedrooms && (
              <p><span className="font-medium">Bedrooms:</span> {property.bedrooms}</p>
            )}
            {property.monthly_rent && (
              <p><span className="font-medium">Rent:</span> {formatCurrency(property.monthly_rent)}/month</p>
            )}
          </div>
          
          <div className="mt-4 flex space-x-2">
            <button className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">
              View Details
            </button>
            <button className="flex-1 px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700">
              Edit
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderTenants = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Tenants</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Phone
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tenants.map((tenant) => (
              <tr key={tenant.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {tenant.first_name} {tenant.last_name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {tenant.tenant_code}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {tenant.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {tenant.phone || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                  <button className="text-gray-600 hover:text-gray-900">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderLeases = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Leases</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lease #
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Property
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Start Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                End Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rent
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leases.map((lease) => (
              <tr key={lease.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {lease.lease_number}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Property #{lease.property_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(lease.start_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(lease.end_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(lease.monthly_rent)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(lease.status)}`}>
                    {lease.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderMaintenance = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {maintenanceRequests.map((request) => (
        <div key={request.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-gray-900">{request.title}</h3>
            <div className="flex space-x-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(request.status)}`}>
                {request.status}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(request.priority)}`}>
                {request.priority}
              </span>
            </div>
          </div>
          
          <div className="space-y-2 text-sm text-gray-600 mb-4">
            <p><span className="font-medium">Request #:</span> {request.request_number}</p>
            <p><span className="font-medium">Property:</span> Property #{request.property_id}</p>
            <p><span className="font-medium">Category:</span> {request.category || 'General'}</p>
            <p><span className="font-medium">Reported:</span> {formatDate(request.reported_date)}</p>
            {request.estimated_cost && (
              <p><span className="font-medium">Est. Cost:</span> {formatCurrency(request.estimated_cost)}</p>
            )}
          </div>
          
          <p className="text-sm text-gray-700 mb-4">{request.description}</p>
          
          <div className="flex space-x-2">
            <button className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">
              View Details
            </button>
            <button className="flex-1 px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700">
              Update Status
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Property Management</h1>
        <p className="text-gray-600">Manage properties, tenants, leases, and maintenance requests</p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'properties', label: 'Properties', icon: '🏠' },
            { id: 'tenants', label: 'Tenants', icon: '👥' },
            { id: 'leases', label: 'Leases', icon: '📄' },
            { id: 'maintenance', label: 'Maintenance', icon: '🔧' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading {activeTab}...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-red-400">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && (
        <>
          {activeTab === 'properties' && renderProperties()}
          {activeTab === 'tenants' && renderTenants()}
          {activeTab === 'leases' && renderLeases()}
          {activeTab === 'maintenance' && renderMaintenance()}
        </>
      )}

      {/* Add Button */}
      <div className="fixed bottom-8 right-8">
        <button className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default PropertyManagement;