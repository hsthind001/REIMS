/**
 * useQuery Hook - Usage Examples
 * 
 * This file demonstrates various use cases for the custom useQuery hook
 */

import { useQuery, useMutation } from './useQuery';
import api from '../api';

// ============================================================================
// Example 1: Basic Usage
// ============================================================================

export function PropertiesListBasic() {
  const { data, isLoading, error, refetch } = useQuery(
    'properties',
    async () => {
      const response = await api.get('/api/properties');
      return response.data;
    }
  );

  if (isLoading) return <div>Loading properties...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <button onClick={refetch}>Refresh</button>
      <ul>
        {data?.properties?.map((property) => (
          <li key={property.id}>{property.name}</li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 2: With Auto-Refetch Interval (30 seconds)
// ============================================================================

export function RealTimeKPIs() {
  const { data, isLoading, isFetching } = useQuery(
    'kpis-financial',
    async () => {
      const response = await api.get('/api/kpis/financial');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      staleTime: 60000, // Cache for 1 minute
    }
  );

  return (
    <div>
      <h2>Financial KPIs {isFetching && '🔄'}</h2>
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <p>Total Value: {data?.total_value}</p>
          <p>NOI: {data?.noi}</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 3: Conditional Query (enabled option)
// ============================================================================

export function PropertyDetails({ propertyId }) {
  const { data, isLoading, error } = useQuery(
    `property-${propertyId}`,
    async () => {
      const response = await api.get(`/api/properties/${propertyId}`);
      return response.data;
    },
    {
      enabled: !!propertyId, // Only fetch if propertyId exists
      staleTime: 10 * 60 * 1000, // Cache for 10 minutes
    }
  );

  if (!propertyId) return <div>Select a property</div>;
  if (isLoading) return <div>Loading property details...</div>;
  if (error) return <div>Error loading property</div>;

  return (
    <div>
      <h2>{data?.name}</h2>
      <p>Address: {data?.address}</p>
      <p>Occupancy: {data?.occupancy}%</p>
    </div>
  );
}

// ============================================================================
// Example 4: Disable Window Focus Refetch
// ============================================================================

export function StaticAnalytics() {
  const { data, isLoading } = useQuery(
    'analytics-overview',
    async () => {
      const response = await api.get('/api/analytics/overview');
      return response.data;
    },
    {
      refetchOnWindowFocus: false, // Don't refetch on focus
      staleTime: 15 * 60 * 1000, // Cache for 15 minutes
    }
  );

  if (isLoading) return <div>Loading analytics...</div>;

  return (
    <div>
      <h2>Analytics Overview</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

// ============================================================================
// Example 5: Multiple Queries in One Component
// ============================================================================

export function Dashboard() {
  const properties = useQuery('properties', async () => {
    const response = await api.get('/api/properties');
    return response.data;
  });

  const kpis = useQuery(
    'kpis',
    async () => {
      const response = await api.get('/api/kpis/financial');
      return response.data;
    },
    { refetchInterval: 30000 }
  );

  const alerts = useQuery('alerts', async () => {
    const response = await api.get('/api/alerts');
    return response.data;
  });

  const isLoading = properties.isLoading || kpis.isLoading || alerts.isLoading;

  if (isLoading) return <div>Loading dashboard...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <section>
        <h2>Properties ({properties.data?.count || 0})</h2>
        {/* Render properties */}
      </section>
      <section>
        <h2>KPIs</h2>
        {/* Render KPIs */}
      </section>
      <section>
        <h2>Alerts ({alerts.data?.length || 0})</h2>
        {/* Render alerts */}
      </section>
    </div>
  );
}

// ============================================================================
// Example 6: With Error Handling and Retry
// ============================================================================

export function DocumentsList() {
  const { data, isLoading, error, isError, refetch } = useQuery(
    'documents',
    async () => {
      const response = await api.get('/api/documents');
      return response.data;
    },
    {
      retry: 2, // Retry twice on failure
      staleTime: 5 * 60 * 1000,
    }
  );

  if (isLoading) return <div>Loading documents...</div>;

  if (isError) {
    return (
      <div className="error-container">
        <p>Failed to load documents: {error.message}</p>
        <button onClick={refetch}>Try Again</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Documents</h2>
      <button onClick={refetch}>Refresh</button>
      <ul>
        {data?.documents?.map((doc) => (
          <li key={doc.id}>{doc.filename}</li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 7: Disable Caching
// ============================================================================

export function LiveProcessingStatus({ documentId }) {
  const { data, isLoading, isFetching } = useQuery(
    `processing-status-${documentId}`,
    async () => {
      const response = await api.get(`/ai/process/${documentId}/status`);
      return response.data;
    },
    {
      refetchInterval: 2000, // Check every 2 seconds
      cacheEnabled: false, // Don't cache (always fresh data)
      staleTime: 0,
    }
  );

  return (
    <div>
      <h3>Processing Status {isFetching && '⏳'}</h3>
      {isLoading ? (
        <p>Loading status...</p>
      ) : (
        <div>
          <p>Status: {data?.status}</p>
          <p>Progress: {data?.progress}%</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 8: Using useMutation for POST/PUT/DELETE
// ============================================================================

export function PropertyForm() {
  const { mutate, isLoading, isSuccess, error } = useMutation(
    async (propertyData) => {
      const response = await api.post('/api/properties', propertyData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        console.log('Property created:', data);
        alert('Property created successfully!');
      },
      onError: (error) => {
        console.error('Failed to create property:', error);
        alert('Failed to create property');
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const propertyData = Object.fromEntries(formData);
    mutate(propertyData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Property Name" required />
      <input name="address" placeholder="Address" required />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Property'}
      </button>
      {isSuccess && <p className="success">Property created!</p>}
      {error && <p className="error">{error.message}</p>}
    </form>
  );
}

// ============================================================================
// Example 9: Mutation with Query Invalidation
// ============================================================================

export function DocumentUpload() {
  const documentsQuery = useQuery('documents', async () => {
    const response = await api.get('/api/documents');
    return response.data;
  });

  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/api/documents/upload', formData);
      return response.data;
    },
    {
      onSuccess: () => {
        // Refetch documents list after successful upload
        documentsQuery.refetch();
      },
    }
  );

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  return (
    <div>
      <h2>Upload Document</h2>
      <input
        type="file"
        onChange={handleFileChange}
        disabled={uploadMutation.isLoading}
      />
      {uploadMutation.isLoading && <p>Uploading...</p>}
      {uploadMutation.isSuccess && <p>Upload successful!</p>}

      <h2>Documents</h2>
      {documentsQuery.isLoading ? (
        <p>Loading documents...</p>
      ) : (
        <ul>
          {documentsQuery.data?.documents?.map((doc) => (
            <li key={doc.id}>{doc.filename}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ============================================================================
// Example 10: Dependent Queries
// ============================================================================

export function PropertyFinancials({ propertyId }) {
  // First query: Get property details
  const propertyQuery = useQuery(
    `property-${propertyId}`,
    async () => {
      const response = await api.get(`/api/properties/${propertyId}`);
      return response.data;
    },
    {
      enabled: !!propertyId,
    }
  );

  // Second query: Get financials (depends on first query)
  const financialsQuery = useQuery(
    `property-${propertyId}-financials`,
    async () => {
      const response = await api.get(
        `/api/properties/${propertyId}/financials`
      );
      return response.data;
    },
    {
      enabled: !!propertyId && propertyQuery.isSuccess, // Only run if property loaded
      staleTime: 10 * 60 * 1000,
    }
  );

  if (!propertyId) return <div>Select a property</div>;
  if (propertyQuery.isLoading) return <div>Loading property...</div>;
  if (financialsQuery.isLoading) return <div>Loading financials...</div>;

  return (
    <div>
      <h2>{propertyQuery.data?.name}</h2>
      <h3>Financial Summary</h3>
      <p>Revenue: ${financialsQuery.data?.revenue}</p>
      <p>Expenses: ${financialsQuery.data?.expenses}</p>
      <p>NOI: ${financialsQuery.data?.noi}</p>
    </div>
  );
}

// ============================================================================
// Example 11: Polling with Stop Condition
// ============================================================================

export function JobStatus({ jobId }) {
  const { data, isLoading, refetch } = useQuery(
    `job-${jobId}`,
    async () => {
      const response = await api.get(`/queue/jobs/${jobId}`);
      return response.data;
    },
    {
      refetchInterval: data?.status === 'completed' ? null : 3000, // Stop polling when completed
      enabled: !!jobId,
    }
  );

  if (isLoading) return <div>Loading job status...</div>;

  const isComplete = data?.status === 'completed';
  const isFailed = data?.status === 'failed';

  return (
    <div>
      <h3>Job Status</h3>
      <p>Status: {data?.status}</p>
      <p>Progress: {data?.progress}%</p>
      {isComplete && <p className="success">✓ Job completed!</p>}
      {isFailed && <p className="error">✗ Job failed</p>}
      {!isComplete && !isFailed && <p>⏳ Processing...</p>}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}

// ============================================================================
// Example 12: Using with Custom API Client
// ============================================================================

export function AnalyticsDashboard() {
  const { data, isLoading, error, refetch } = useQuery(
    'analytics-dashboard',
    async () => {
      // Using the custom API client from api/client.js
      const data = await api.get('/api/analytics/overview');
      return data;
    },
    {
      refetchInterval: 60000, // Refetch every minute
      staleTime: 2 * 60 * 1000, // Cache for 2 minutes
      retry: 2,
    }
  );

  return (
    <div>
      <div className="header">
        <h1>Analytics Dashboard</h1>
        <button onClick={refetch} disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && <div className="error">Error: {error.message}</div>}

      {data && (
        <div className="metrics-grid">
          <div className="metric">
            <h3>Total Documents</h3>
            <p>{data.total_documents}</p>
          </div>
          <div className="metric">
            <h3>Processed</h3>
            <p>{data.processed_documents}</p>
          </div>
          <div className="metric">
            <h3>Success Rate</h3>
            <p>{data.success_rate}%</p>
          </div>
        </div>
      )}
    </div>
  );
}

