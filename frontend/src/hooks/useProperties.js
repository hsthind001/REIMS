import React, { useMemo } from 'react';
import { useQuery } from './useQuery';
import api from '../api';

/**
 * Mock properties data for fallback/demo purposes
 */
const MOCK_PROPERTIES_DATA = [
  {
    id: 'prop-001',
    name: 'Sunset Apartments',
    address: '123 Sunset Blvd, Los Angeles, CA 90028',
    occupancy_rate: 0.95,
    noi: 450000,
    dscr: 1.45,
    status: 'healthy',
    property_type: 'residential',
    units: 24,
    square_footage: 18500,
    year_built: 2018,
  },
  {
    id: 'prop-002',
    name: 'Downtown Commercial Plaza',
    address: '456 Main St, San Francisco, CA 94102',
    occupancy_rate: 0.88,
    noi: 1200000,
    dscr: 1.62,
    status: 'healthy',
    property_type: 'commercial',
    units: 8,
    square_footage: 45000,
    year_built: 2015,
  },
  {
    id: 'prop-003',
    name: 'Riverside Condos',
    address: '789 River Rd, Portland, OR 97201',
    occupancy_rate: 0.72,
    noi: 280000,
    dscr: 1.15,
    status: 'alert',
    property_type: 'residential',
    units: 16,
    square_footage: 12800,
    year_built: 2010,
  },
  {
    id: 'prop-004',
    name: 'Tech Park Office Building',
    address: '321 Innovation Dr, Austin, TX 78701',
    occupancy_rate: 0.92,
    noi: 890000,
    dscr: 1.58,
    status: 'healthy',
    property_type: 'commercial',
    units: 12,
    square_footage: 38000,
    year_built: 2019,
  },
  {
    id: 'prop-005',
    name: 'Garden View Apartments',
    address: '555 Garden Ave, Seattle, WA 98101',
    occupancy_rate: 0.96,
    noi: 520000,
    dscr: 1.52,
    status: 'healthy',
    property_type: 'residential',
    units: 32,
    square_footage: 24000,
    year_built: 2020,
  },
  {
    id: 'prop-006',
    name: 'Lakefront Retail Center',
    address: '888 Lake St, Chicago, IL 60601',
    occupancy_rate: 0.68,
    noi: 350000,
    dscr: 1.08,
    status: 'alert',
    property_type: 'retail',
    units: 6,
    square_footage: 28000,
    year_built: 2008,
  },
  // Add more mock properties for pagination testing
  ...Array.from({ length: 14 }, (_, i) => ({
    id: `prop-${String(i + 7).padStart(3, '0')}`,
    name: `Property ${i + 7}`,
    address: `${100 + i} Test St, City, ST 12345`,
    occupancy_rate: 0.7 + Math.random() * 0.25,
    noi: 200000 + Math.random() * 800000,
    dscr: 1.1 + Math.random() * 0.5,
    status: Math.random() > 0.7 ? 'alert' : 'healthy',
    property_type: ['residential', 'commercial', 'retail', 'industrial'][Math.floor(Math.random() * 4)],
    units: Math.floor(Math.random() * 40) + 5,
    square_footage: Math.floor(Math.random() * 40000) + 10000,
    year_built: 2000 + Math.floor(Math.random() * 23),
  })),
];

/**
 * Custom hook for fetching properties list with pagination, filtering, sorting, and search
 * 
 * @param {Object} options - Hook configuration options
 * @param {number} options.skip - Number of records to skip (default: 0)
 * @param {number} options.limit - Number of records to fetch (default: 20)
 * @param {string} options.status - Filter by status: 'healthy', 'alert', or null for all
 * @param {string} options.sortBy - Sort field: 'name', 'occupancy_rate', 'noi', 'dscr'
 * @param {string} options.sortOrder - Sort order: 'asc' or 'desc' (default: 'asc')
 * @param {string} options.search - Search query for name or address
 * @param {string} options.propertyType - Filter by property type
 * @param {boolean} options.useMockData - Force use of mock data (default: false)
 * @param {boolean} options.enableAutoRefetch - Enable auto-refetch (default: false)
 * @param {number} options.refetchInterval - Refetch interval in ms (default: 5 min)
 * @param {number} options.staleTime - Cache duration in ms (default: 3 min)
 * 
 * @returns {Object} Properties data and state
 */
export function useProperties(options = {}) {
  const {
    skip = 0,
    limit = 20,
    status = null,
    sortBy = 'name',
    sortOrder = 'asc',
    search = '',
    propertyType = null,
    useMockData = false,
    enableAutoRefetch = false,
    refetchInterval = 5 * 60 * 1000,
    staleTime = 3 * 60 * 1000,
  } = options;

  // Generate cache key based on query parameters
  const cacheKey = useMemo(() => {
    const params = {
      skip,
      limit,
      status,
      sortBy,
      sortOrder,
      search,
      propertyType,
    };
    const paramString = Object.entries(params)
      .filter(([_, value]) => value !== null && value !== '')
      .map(([key, value]) => `${key}:${value}`)
      .join('|');
    return `properties-${paramString}`;
  }, [skip, limit, status, sortBy, sortOrder, search, propertyType]);

  // Use mock data if requested
  if (useMockData) {
    const mockResult = getMockPropertiesData({
      skip,
      limit,
      status,
      sortBy,
      sortOrder,
      search,
      propertyType,
    });

    return {
      properties: mockResult.properties,
      total: mockResult.total,
      isLoading: false,
      error: null,
      refetch: () => Promise.resolve(mockResult),
      isFetching: false,
      isError: false,
      isSuccess: true,
      hasNextPage: skip + limit < mockResult.total,
      hasPreviousPage: skip > 0,
      currentPage: Math.floor(skip / limit) + 1,
      totalPages: Math.ceil(mockResult.total / limit),
      usingMockData: true,
    };
  }

  // Fetch properties data using useQuery hook
  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
    isError,
    isSuccess,
  } = useQuery(
    cacheKey,
    async () => {
      try {
        // Build query parameters
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
        });

        if (status) params.append('status', status);
        if (sortBy) params.append('sort_by', sortBy);
        if (sortOrder) params.append('sort_order', sortOrder);
        if (search) params.append('search', search);
        if (propertyType) params.append('property_type', propertyType);

        const response = await api.get(`/api/properties?${params.toString()}`);
        
        // Handle different response formats
        const responseData = response.data || response;
        
        // Normalize the data
        return normalizePropertiesData(responseData);
      } catch (error) {
        console.error('Failed to fetch properties:', error);
        
        // Fallback to mock data on error
        console.warn('Using mock properties data due to fetch error');
        return getMockPropertiesData({
          skip,
          limit,
          status,
          sortBy,
          sortOrder,
          search,
          propertyType,
        });
      }
    },
    {
      refetchInterval: enableAutoRefetch ? refetchInterval : null,
      staleTime,
      retry: 2,
      refetchOnWindowFocus: false,
      cacheEnabled: true,
    }
  );

  // Determine if mock data is being used
  const usingMockData = data?.usingMockData || false;

  // Format error message
  const errorMessage = useMemo(() => {
    if (!error) return null;
    if (typeof error === 'string') return error;
    if (error.message) return error.message;
    return 'Failed to load properties data';
  }, [error]);

  // Extract properties data with fallback
  const properties = useMemo(() => {
    return data?.properties || [];
  }, [data]);

  const total = useMemo(() => {
    return data?.total || 0;
  }, [data]);

  // Calculate pagination info
  const hasNextPage = skip + limit < total;
  const hasPreviousPage = skip > 0;
  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return {
    properties,
    total,
    isLoading,
    error: errorMessage,
    refetch,
    isFetching,
    isError,
    isSuccess,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
    usingMockData,
  };
}

/**
 * Normalize properties data to ensure consistent structure
 */
function normalizePropertiesData(data) {
  const properties = (data.properties || data.items || data).map(property => ({
    id: property.id || property.property_id,
    name: property.name || property.property_name || 'Unknown',
    address: property.address || property.location || '',
    occupancy_rate: Number(property.occupancy_rate || 0),
    noi: Number(property.noi || property.net_operating_income || 0),
    dscr: Number(property.dscr || property.debt_service_coverage_ratio || 0),
    status: property.status || (property.occupancy_rate >= 0.8 ? 'healthy' : 'alert'),
    property_type: property.property_type || property.type || 'residential',
    units: Number(property.units || 0),
    square_footage: Number(property.square_footage || property.sqft || 0),
    year_built: Number(property.year_built || new Date().getFullYear()),
  }));

  const total = data.total || data.count || properties.length;

  return {
    properties,
    total,
  };
}

/**
 * Get mock properties data with filtering, sorting, and pagination
 */
function getMockPropertiesData(options = {}) {
  const {
    skip = 0,
    limit = 20,
    status = null,
    sortBy = 'name',
    sortOrder = 'asc',
    search = '',
    propertyType = null,
  } = options;

  let filteredProperties = [...MOCK_PROPERTIES_DATA];

  // Apply status filter
  if (status) {
    filteredProperties = filteredProperties.filter(
      prop => prop.status === status
    );
  }

  // Apply property type filter
  if (propertyType) {
    filteredProperties = filteredProperties.filter(
      prop => prop.property_type === propertyType
    );
  }

  // Apply search filter
  if (search) {
    const searchLower = search.toLowerCase();
    filteredProperties = filteredProperties.filter(
      prop =>
        prop.name.toLowerCase().includes(searchLower) ||
        prop.address.toLowerCase().includes(searchLower)
    );
  }

  // Apply sorting
  filteredProperties.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];

    // Handle string comparison
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
    } else {
      return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
    }
  });

  // Apply pagination
  const total = filteredProperties.length;
  const paginatedProperties = filteredProperties.slice(skip, skip + limit);

  return {
    properties: paginatedProperties,
    total,
    usingMockData: true,
  };
}

/**
 * Hook for fetching a single property by ID
 */
export function useProperty(propertyId, options = {}) {
  const {
    useMockData = false,
    refetchInterval = null,
    staleTime = 3 * 60 * 1000,
  } = options;

  // Use mock data if requested
  if (useMockData) {
    const property = MOCK_PROPERTIES_DATA.find(p => p.id === propertyId);
    return {
      property: property || null,
      isLoading: false,
      error: property ? null : 'Property not found',
      refetch: () => Promise.resolve(property),
      isFetching: false,
      isError: !property,
      isSuccess: !!property,
      usingMockData: true,
    };
  }

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
    isError,
    isSuccess,
  } = useQuery(
    `property-${propertyId}`,
    async () => {
      try {
        const response = await api.get(`/api/properties/${propertyId}`);
        const responseData = response.data || response;
        return normalizePropertyData(responseData);
      } catch (error) {
        console.error(`Failed to fetch property ${propertyId}:`, error);
        
        // Fallback to mock data
        const mockProperty = MOCK_PROPERTIES_DATA.find(p => p.id === propertyId);
        if (mockProperty) {
          return { ...mockProperty, usingMockData: true };
        }
        throw new Error('Property not found');
      }
    },
    {
      refetchInterval,
      staleTime,
      retry: 2,
    }
  );

  return {
    property: data || null,
    isLoading,
    error: error ? (typeof error === 'string' ? error : error.message) : null,
    refetch,
    isFetching,
    isError,
    isSuccess,
    usingMockData: data?.usingMockData || false,
  };
}

/**
 * Normalize single property data
 */
function normalizePropertyData(data) {
  return {
    id: data.id || data.property_id,
    name: data.name || data.property_name || 'Unknown',
    address: data.address || data.location || '',
    occupancy_rate: Number(data.occupancy_rate || 0),
    noi: Number(data.noi || data.net_operating_income || 0),
    dscr: Number(data.dscr || data.debt_service_coverage_ratio || 0),
    status: data.status || (data.occupancy_rate >= 0.8 ? 'healthy' : 'alert'),
    property_type: data.property_type || data.type || 'residential',
    units: Number(data.units || 0),
    square_footage: Number(data.square_footage || data.sqft || 0),
    year_built: Number(data.year_built || new Date().getFullYear()),
  };
}

/**
 * Hook for fetching properties with infinite scroll
 */
export function useInfiniteProperties(options = {}) {
  const {
    limit = 20,
    ...otherOptions
  } = options;

  const [allProperties, setAllProperties] = React.useState([]);
  const [currentSkip, setCurrentSkip] = React.useState(0);

  const { properties, total, isLoading, hasNextPage, ...rest } = useProperties({
    skip: currentSkip,
    limit,
    ...otherOptions,
  });

  React.useEffect(() => {
    if (properties.length > 0) {
      if (currentSkip === 0) {
        setAllProperties(properties);
      } else {
        setAllProperties(prev => [...prev, ...properties]);
      }
    }
  }, [properties, currentSkip]);

  const loadMore = () => {
    if (hasNextPage) {
      setCurrentSkip(prev => prev + limit);
    }
  };

  const reset = () => {
    setCurrentSkip(0);
    setAllProperties([]);
  };

  return {
    properties: allProperties,
    total,
    isLoading,
    hasNextPage,
    loadMore,
    reset,
    ...rest,
  };
}

/**
 * Export mock data for testing
 */
export { MOCK_PROPERTIES_DATA };

export default useProperties;

