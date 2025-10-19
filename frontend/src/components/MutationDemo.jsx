import React, { useState } from 'react';
import {
  useMutation,
  useOptimisticMutation,
  useQueryClient,
} from '../hooks/useMutation';
import { useQuery } from '../hooks/useQuery';
import api from '../api';

/**
 * Demo Component showcasing useMutation hook features
 */
export default function MutationDemo() {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({ name: '', address: '' });

  // =========================================================================
  // Fetch Properties List
  // =========================================================================
  const { data: properties, isLoading: isLoadingProperties, refetch } = useQuery(
    'properties-mutation-demo',
    async () => {
      const response = await api.get('/api/properties');
      return response.data;
    }
  );

  // =========================================================================
  // CREATE: Basic Mutation with Cache Invalidation
  // =========================================================================
  const createMutation = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      invalidateQueries: ['properties-mutation-demo'], // Auto-refresh list
      onSuccess: (data) => {
        alert(`Property "${data.name}" created successfully!`);
        setFormData({ name: '', address: '' });
      },
      onError: (error) => {
        alert(`Failed to create property: ${error.message}`);
      },
      retry: 2, // Retry twice on failure
    }
  );

  // =========================================================================
  // UPDATE: Mutation with Retry
  // =========================================================================
  const updateMutation = useMutation(
    async ({ id, data }) => {
      const response = await api.put(`/api/properties/${id}`, data);
      return response.data;
    },
    {
      invalidateQueries: ['properties-mutation-demo'],
      retry: 3,
      retryDelay: 1000,
      onSuccess: () => alert('Property updated!'),
    }
  );

  // =========================================================================
  // DELETE: Optimistic Mutation
  // =========================================================================
  const deleteMutation = useOptimisticMutation(
    async (id) => {
      await api.delete(`/api/properties/${id}`);
      return id;
    },
    'properties-mutation-demo',
    (oldData, deletedId) => {
      // Optimistically remove from list
      return {
        ...oldData,
        properties: oldData.properties.filter((p) => p.id !== deletedId),
      };
    },
    {
      onError: (error) => {
        alert(`Failed to delete: ${error.message}`);
      },
    }
  );

  // =========================================================================
  // FILE UPLOAD: Mutation with FormData
  // =========================================================================
  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/documents/upload', formData);
      return response.data;
    },
    {
      invalidateQueries: ['documents'],
      onSuccess: (data) => {
        alert(`File "${data.filename}" uploaded successfully!`);
      },
      retry: 1,
    }
  );

  // =========================================================================
  // Handlers
  // =========================================================================
  const handleCreate = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.address) {
      alert('Please fill in all fields');
      return;
    }
    createMutation.mutate({
      ...formData,
      type: 'Commercial',
    });
  };

  const handleUpdate = (property) => {
    const newName = prompt('Enter new name:', property.name);
    if (newName && newName !== property.name) {
      updateMutation.mutate({
        id: property.id,
        data: { ...property, name: newName },
      });
    }
  };

  const handleDelete = (property) => {
    if (confirm(`Delete property "${property.name}"?`)) {
      deleteMutation.mutate(property.id);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleClearCache = () => {
    queryClient.invalidateQueries('properties-mutation-demo');
    alert('Cache cleared!');
  };

  // =========================================================================
  // Render
  // =========================================================================
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-6 shadow-lg">
        <h1 className="text-3xl font-bold mb-2">useMutation Hook Demo</h1>
        <p className="text-purple-100">
          POST, PUT, DELETE with optimistic updates & cache invalidation
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Cache Controls</h2>
        <div className="flex gap-4">
          <button
            onClick={handleClearCache}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors"
          >
            Clear Cache
          </button>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            Manual Refetch
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* CREATE Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-green-600">CREATE</span>
            {createMutation.isLoading && <span className="text-sm">🔄</span>}
          </h2>

          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter property name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) =>
                  setFormData({ ...formData, address: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter address"
              />
            </div>

            <button
              type="submit"
              disabled={createMutation.isLoading}
              className="w-full px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:bg-gray-400 transition-colors"
            >
              {createMutation.isLoading ? 'Creating...' : 'Create Property'}
            </button>

            {createMutation.isSuccess && (
              <p className="text-sm text-green-600 font-medium">
                ✓ Created successfully! (Auto-invalidated cache)
              </p>
            )}
            {createMutation.isError && (
              <p className="text-sm text-red-600">
                ✗ Error: {createMutation.error?.message}
              </p>
            )}
          </form>

          <div className="mt-4 text-sm text-gray-500 space-y-1">
            <p>• Auto cache invalidation: ✓</p>
            <p>• Retry on failure: 2 attempts</p>
            <p>• Loading state: ✓</p>
          </div>
        </div>

        {/* FILE UPLOAD */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span className="text-blue-600">FILE UPLOAD</span>
            {uploadMutation.isLoading && <span className="text-sm">⏳</span>}
          </h2>

          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                onChange={handleFileUpload}
                disabled={uploadMutation.isLoading}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className={`cursor-pointer ${
                  uploadMutation.isLoading ? 'opacity-50' : ''
                }`}
              >
                <div className="text-4xl mb-2">📄</div>
                <p className="text-sm text-gray-600">
                  Click to select file or drag and drop
                </p>
              </label>
            </div>

            {uploadMutation.isLoading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
                <span className="ml-3 text-gray-600">Uploading...</span>
              </div>
            )}

            {uploadMutation.isSuccess && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 font-medium">
                  ✓ Upload successful!
                </p>
                <p className="text-sm text-green-600 mt-1">
                  File: {uploadMutation.data?.filename}
                </p>
              </div>
            )}

            {uploadMutation.isError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">✗ Upload failed</p>
                <p className="text-sm text-red-600 mt-1">
                  {uploadMutation.error?.message}
                </p>
                <button
                  onClick={uploadMutation.reset}
                  className="mt-2 text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>

          <div className="mt-4 text-sm text-gray-500 space-y-1">
            <p>• FormData support: ✓</p>
            <p>• Retry on failure: 1 attempt</p>
            <p>• Error recovery: ✓</p>
          </div>
        </div>
      </div>

      {/* Properties List with UPDATE/DELETE */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">
            Properties List (UPDATE/DELETE)
          </h2>
          {(updateMutation.isLoading || deleteMutation.isLoading) && (
            <span className="text-sm text-gray-600">Processing...</span>
          )}
        </div>

        {isLoadingProperties && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
          </div>
        )}

        {properties?.properties && properties.properties.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No properties yet. Create one above!</p>
          </div>
        )}

        {properties?.properties && properties.properties.length > 0 && (
          <div className="space-y-3">
            {properties.properties.slice(0, 10).map((property) => (
              <div
                key={property.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900">{property.name}</p>
                  <p className="text-sm text-gray-600">{property.address}</p>
                  {property.type && (
                    <span className="inline-block mt-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {property.type}
                    </span>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleUpdate(property)}
                    disabled={updateMutation.isLoading}
                    className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
                  >
                    Update
                  </button>
                  <button
                    onClick={() => handleDelete(property)}
                    disabled={deleteMutation.isLoading}
                    className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 disabled:bg-gray-400 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 text-sm text-gray-500 space-y-1">
          <p>• UPDATE: Retry 3 times with exponential backoff</p>
          <p>• DELETE: Optimistic update (instant UI response)</p>
          <p>• Auto rollback on error</p>
        </div>
      </div>

      {/* Features Summary */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Features Demonstrated</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>POST/PUT/DELETE operations</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Loading/error/success states</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Optimistic updates</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Automatic cache invalidation</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Retry with exponential backoff</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Error recovery & rollback</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>FormData support</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Query client integration</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <span>Success/error callbacks</span>
          </div>
        </div>
      </div>

      {/* Mutation Status */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Mutation Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="p-3 bg-green-50 rounded-lg">
            <p className="text-gray-600 mb-1">CREATE</p>
            <p
              className={`font-semibold ${
                createMutation.isLoading
                  ? 'text-yellow-600'
                  : createMutation.isSuccess
                  ? 'text-green-600'
                  : createMutation.isError
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {createMutation.status}
            </p>
          </div>

          <div className="p-3 bg-blue-50 rounded-lg">
            <p className="text-gray-600 mb-1">UPDATE</p>
            <p
              className={`font-semibold ${
                updateMutation.isLoading
                  ? 'text-yellow-600'
                  : updateMutation.isSuccess
                  ? 'text-green-600'
                  : updateMutation.isError
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {updateMutation.status}
            </p>
          </div>

          <div className="p-3 bg-red-50 rounded-lg">
            <p className="text-gray-600 mb-1">DELETE</p>
            <p
              className={`font-semibold ${
                deleteMutation.isLoading
                  ? 'text-yellow-600'
                  : deleteMutation.isSuccess
                  ? 'text-green-600'
                  : deleteMutation.isError
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {deleteMutation.status}
            </p>
          </div>

          <div className="p-3 bg-purple-50 rounded-lg">
            <p className="text-gray-600 mb-1">UPLOAD</p>
            <p
              className={`font-semibold ${
                uploadMutation.isLoading
                  ? 'text-yellow-600'
                  : uploadMutation.isSuccess
                  ? 'text-green-600'
                  : uploadMutation.isError
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {uploadMutation.status}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

