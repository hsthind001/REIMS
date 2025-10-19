import React, { useState } from 'react';
import { useQuery, useMutation, clearQueryCache } from '../hooks/useQuery';
import api from '../api';

/**
 * Demo Component showcasing useQuery hook features
 */
export default function QueryDemo() {
  const [selectedPropertyId, setSelectedPropertyId] = useState(null);
  const [autoRefetch, setAutoRefetch] = useState(false);

  // =========================================================================
  // Example 1: Basic Query with Auto-refetch
  // =========================================================================
  const kpisQuery = useQuery(
    'kpis-demo',
    async () => {
      const response = await api.get('/api/kpis/financial');
      return response.data;
    },
    {
      refetchInterval: autoRefetch ? 10000 : null, // Refetch every 10 seconds if enabled
      staleTime: 30000, // Cache for 30 seconds
    }
  );

  // =========================================================================
  // Example 2: Properties List
  // =========================================================================
  const propertiesQuery = useQuery(
    'properties-demo',
    async () => {
      const response = await api.get('/api/properties');
      return response.data;
    },
    {
      staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    }
  );

  // =========================================================================
  // Example 3: Conditional Query (only fetch if property selected)
  // =========================================================================
  const propertyDetailsQuery = useQuery(
    `property-${selectedPropertyId}`,
    async () => {
      const response = await api.get(`/api/properties/${selectedPropertyId}`);
      return response.data;
    },
    {
      enabled: !!selectedPropertyId, // Only fetch if property is selected
      staleTime: 2 * 60 * 1000,
    }
  );

  // =========================================================================
  // Example 4: Real-time Processing Status (no cache)
  // =========================================================================
  const [documentId, setDocumentId] = useState(null);
  const processingQuery = useQuery(
    `processing-${documentId}`,
    async () => {
      const response = await api.get(`/ai/process/${documentId}/status`);
      return response.data;
    },
    {
      enabled: !!documentId,
      refetchInterval: documentId ? 3000 : null, // Poll every 3 seconds
      cacheEnabled: false, // Don't cache real-time data
    }
  );

  // =========================================================================
  // Example 5: Mutation for Creating Property
  // =========================================================================
  const createPropertyMutation = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        alert('Property created successfully!');
        // Refetch properties list
        propertiesQuery.refetch();
      },
      onError: (error) => {
        alert(`Failed to create property: ${error.message}`);
      },
    }
  );

  // =========================================================================
  // Handlers
  // =========================================================================
  const handleCreateProperty = () => {
    const propertyData = {
      name: `Test Property ${Date.now()}`,
      address: '123 Test St',
      type: 'Commercial',
    };
    createPropertyMutation.mutate(propertyData);
  };

  const handleClearCache = () => {
    clearQueryCache('kpis-demo');
    clearQueryCache('properties-demo');
    alert('Cache cleared!');
  };

  const handleSelectProperty = (id) => {
    setSelectedPropertyId(id);
  };

  // =========================================================================
  // Render
  // =========================================================================
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6 shadow-lg">
        <h1 className="text-3xl font-bold mb-2">useQuery Hook Demo</h1>
        <p className="text-blue-100">
          Demonstration of custom data fetching hook features
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Controls</h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => setAutoRefetch(!autoRefetch)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              autoRefetch
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Auto-Refetch: {autoRefetch ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={handleClearCache}
            className="px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
          >
            Clear Cache
          </button>

          <button
            onClick={kpisQuery.refetch}
            disabled={kpisQuery.isFetching}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
          >
            {kpisQuery.isFetching ? 'Refetching...' : 'Manual Refetch KPIs'}
          </button>

          <button
            onClick={handleCreateProperty}
            disabled={createPropertyMutation.isLoading}
            className="px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:bg-gray-400 transition-colors"
          >
            {createPropertyMutation.isLoading
              ? 'Creating...'
              : 'Create Test Property'}
          </button>
        </div>
      </div>

      {/* KPIs Query Demo */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">
            1. KPIs Query {kpisQuery.isFetching && '🔄'}
          </h2>
          <div className="flex items-center gap-4">
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                kpisQuery.isLoading
                  ? 'bg-yellow-100 text-yellow-800'
                  : kpisQuery.isSuccess
                  ? 'bg-green-100 text-green-800'
                  : kpisQuery.isError
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {kpisQuery.isLoading
                ? 'Loading'
                : kpisQuery.isSuccess
                ? 'Success'
                : kpisQuery.isError
                ? 'Error'
                : 'Idle'}
            </span>
          </div>
        </div>

        {kpisQuery.isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          </div>
        )}

        {kpisQuery.isError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">Error: {kpisQuery.error?.message}</p>
          </div>
        )}

        {kpisQuery.isSuccess && kpisQuery.data && (
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Total Portfolio Value</p>
              <p className="text-2xl font-bold text-blue-600">
                {kpisQuery.data.total_portfolio_value?.formatted || 'N/A'}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Total Properties</p>
              <p className="text-2xl font-bold text-green-600">
                {kpisQuery.data.total_properties || 0}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Average Occupancy</p>
              <p className="text-2xl font-bold text-purple-600">
                {kpisQuery.data.average_occupancy || 0}%
              </p>
            </div>
          </div>
        )}

        <div className="mt-4 text-sm text-gray-500">
          <p>
            • Auto-refetch: {autoRefetch ? 'Enabled (10s interval)' : 'Disabled'}
          </p>
          <p>• Cache time: 30 seconds</p>
          <p>• Retry on failure: 1 attempt</p>
        </div>
      </div>

      {/* Properties List Query Demo */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">
            2. Properties List {propertiesQuery.isFetching && '🔄'}
          </h2>
          <button
            onClick={propertiesQuery.refetch}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-sm"
          >
            Refresh
          </button>
        </div>

        {propertiesQuery.isLoading && <p>Loading properties...</p>}

        {propertiesQuery.isError && (
          <p className="text-red-600">
            Error: {propertiesQuery.error?.message}
          </p>
        )}

        {propertiesQuery.isSuccess && (
          <div className="space-y-2">
            {propertiesQuery.data?.properties?.slice(0, 5).map((property) => (
              <div
                key={property.id}
                onClick={() => handleSelectProperty(property.id)}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedPropertyId === property.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{property.name}</p>
                    <p className="text-sm text-gray-600">{property.address}</p>
                  </div>
                  <span className="text-sm text-gray-500">
                    {property.occupancy}% occupied
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 text-sm text-gray-500">
          <p>• Cache time: 5 minutes</p>
          <p>• Refetch on window focus: Enabled</p>
          <p>• Click a property to load details</p>
        </div>
      </div>

      {/* Conditional Query Demo */}
      {selectedPropertyId && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">
            3. Property Details (Conditional Query)
          </h2>

          {propertyDetailsQuery.isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            </div>
          )}

          {propertyDetailsQuery.isError && (
            <p className="text-red-600">
              Error: {propertyDetailsQuery.error?.message}
            </p>
          )}

          {propertyDetailsQuery.isSuccess && (
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <p>
                <strong>Name:</strong> {propertyDetailsQuery.data?.name}
              </p>
              <p>
                <strong>Address:</strong> {propertyDetailsQuery.data?.address}
              </p>
              <p>
                <strong>Type:</strong> {propertyDetailsQuery.data?.type}
              </p>
              <p>
                <strong>Occupancy:</strong> {propertyDetailsQuery.data?.occupancy}
                %
              </p>
            </div>
          )}

          <div className="mt-4 text-sm text-gray-500">
            <p>• Only fetches when property is selected</p>
            <p>• Cache time: 2 minutes</p>
          </div>
        </div>
      )}

      {/* Status Legend */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Status Indicators</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 font-medium">
              Loading
            </span>
            <span className="text-gray-600">Initial fetch</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-green-100 text-green-800 font-medium">
              Success
            </span>
            <span className="text-gray-600">Data loaded</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-red-100 text-red-800 font-medium">
              Error
            </span>
            <span className="text-gray-600">Fetch failed</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔄</span>
            <span className="text-gray-600">Background refetch</span>
          </div>
        </div>
      </div>

      {/* Features Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Features Demonstrated</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Loading, error, and success states</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Automatic refetching at intervals</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Manual refetch function</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>localStorage caching (5 min default)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Retry logic on failure</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Conditional queries (enabled/disabled)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Background refetch (no loading state)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            <span>Mutations with callbacks</span>
          </div>
        </div>
      </div>
    </div>
  );
}

