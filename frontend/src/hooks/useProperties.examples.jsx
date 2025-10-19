/**
 * useProperties Hook - Usage Examples
 * 
 * Demonstrates various use cases for the properties fetching hook
 */

import React, { useState } from 'react';
import useProperties, { useProperty, useInfiniteProperties } from './useProperties';

// ============================================================================
// Example 1: Basic Properties List
// ============================================================================

export function BasicPropertiesList() {
  const { properties, isLoading, error, refetch } = useProperties();

  if (isLoading) {
    return <div>Loading properties...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Properties ({properties.length})</h2>
      <ul>
        {properties.map(property => (
          <li key={property.id}>
            <strong>{property.name}</strong>
            <br />
            {property.address}
            <br />
            Occupancy: {(property.occupancy_rate * 100).toFixed(1)}%
          </li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================================
// Example 2: Properties with Pagination
// ============================================================================

export function PaginatedPropertiesList() {
  const [skip, setSkip] = useState(0);
  const limit = 10;

  const {
    properties,
    total,
    isLoading,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
  } = useProperties({ skip, limit });

  const goToNextPage = () => {
    if (hasNextPage) {
      setSkip(skip + limit);
    }
  };

  const goToPreviousPage = () => {
    if (hasPreviousPage) {
      setSkip(Math.max(0, skip - limit));
    }
  };

  const goToPage = (page) => {
    setSkip((page - 1) * limit);
  };

  return (
    <div>
      <h2>Properties ({total} total)</h2>
      
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {properties.map(property => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={goToPreviousPage}
              disabled={!hasPreviousPage}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Previous
            </button>

            <span>
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={goToNextPage}
              disabled={!hasNextPage}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Next
            </button>
          </div>

          {/* Page Numbers */}
          <div className="flex gap-2 mt-4 justify-center">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <button
                key={page}
                onClick={() => goToPage(page)}
                className={`
                  px-3 py-1 rounded
                  ${page === currentPage
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 hover:bg-gray-300'
                  }
                `}
              >
                {page}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================================
// Example 3: Properties with Filtering and Sorting
// ============================================================================

export function FilteredPropertiesList() {
  const [status, setStatus] = useState(null);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  const { properties, total, isLoading } = useProperties({
    status,
    sortBy,
    sortOrder,
    limit: 20,
  });

  return (
    <div>
      <div className="mb-6 flex gap-4">
        {/* Status Filter */}
        <select
          value={status || ''}
          onChange={(e) => setStatus(e.target.value || null)}
          className="px-4 py-2 border rounded"
        >
          <option value="">All Statuses</option>
          <option value="healthy">Healthy</option>
          <option value="alert">Alert</option>
        </select>

        {/* Sort By */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="name">Name</option>
          <option value="occupancy_rate">Occupancy Rate</option>
          <option value="noi">NOI</option>
          <option value="dscr">DSCR</option>
        </select>

        {/* Sort Order */}
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>

      <h2>Properties ({total} total)</h2>

      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <div className="space-y-4">
          {properties.map(property => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 4: Properties with Search
// ============================================================================

export function SearchablePropertiesList() {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const { properties, total, isLoading, isFetching } = useProperties({
    search: debouncedSearch,
    limit: 20,
  });

  return (
    <div>
      {/* Search Input */}
      <div className="mb-6">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by name or address..."
          className="w-full px-4 py-2 border rounded"
        />
        {isFetching && <span className="text-sm text-gray-500 mt-2">Searching...</span>}
      </div>

      <h2>
        {debouncedSearch
          ? `Search results for "${debouncedSearch}" (${total})`
          : `All Properties (${total})`
        }
      </h2>

      {isLoading ? (
        <div>Loading...</div>
      ) : properties.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No properties found matching your search
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {properties.map(property => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 5: Single Property Detail
// ============================================================================

export function PropertyDetail({ propertyId }) {
  const { property, isLoading, error, refetch } = useProperty(propertyId);

  if (isLoading) {
    return <div>Loading property...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    );
  }

  if (!property) {
    return <div>Property not found</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">{property.name}</h1>
      
      <div className="space-y-2">
        <p><strong>Address:</strong> {property.address}</p>
        <p><strong>Type:</strong> {property.property_type}</p>
        <p><strong>Units:</strong> {property.units}</p>
        <p><strong>Square Footage:</strong> {property.square_footage.toLocaleString()} sqft</p>
        <p><strong>Year Built:</strong> {property.year_built}</p>
        <p>
          <strong>Occupancy Rate:</strong>{' '}
          {(property.occupancy_rate * 100).toFixed(1)}%
        </p>
        <p><strong>NOI:</strong> ${property.noi.toLocaleString()}</p>
        <p><strong>DSCR:</strong> {property.dscr.toFixed(2)}</p>
        <p>
          <strong>Status:</strong>{' '}
          <span className={
            property.status === 'healthy'
              ? 'text-green-600 font-semibold'
              : 'text-red-600 font-semibold'
          }>
            {property.status.toUpperCase()}
          </span>
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// Example 6: Infinite Scroll Properties List
// ============================================================================

export function InfiniteScrollPropertiesList() {
  const {
    properties,
    total,
    isLoading,
    hasNextPage,
    loadMore,
  } = useInfiniteProperties({
    limit: 10,
  });

  return (
    <div>
      <h2>All Properties ({total} total)</h2>
      <p className="text-sm text-gray-600 mb-4">
        Loaded: {properties.length} / {total}
      </p>

      <div className="space-y-4">
        {properties.map((property, index) => (
          <PropertyCard key={`${property.id}-${index}`} property={property} />
        ))}
      </div>

      {hasNextPage && (
        <div className="mt-6 text-center">
          <button
            onClick={loadMore}
            disabled={isLoading}
            className="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      {!hasNextPage && properties.length > 0 && (
        <div className="mt-6 text-center text-gray-500">
          All properties loaded
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Example 7: Properties with Combined Filters
// ============================================================================

export function AdvancedPropertiesFilter() {
  const [filters, setFilters] = useState({
    status: null,
    propertyType: null,
    sortBy: 'name',
    sortOrder: 'asc',
    search: '',
    skip: 0,
    limit: 10,
  });

  const {
    properties,
    total,
    isLoading,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
  } = useProperties(filters);

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      skip: 0, // Reset to first page when filter changes
    }));
  };

  const nextPage = () => {
    setFilters(prev => ({
      ...prev,
      skip: prev.skip + prev.limit,
    }));
  };

  const previousPage = () => {
    setFilters(prev => ({
      ...prev,
      skip: Math.max(0, prev.skip - prev.limit),
    }));
  };

  const clearFilters = () => {
    setFilters({
      status: null,
      propertyType: null,
      sortBy: 'name',
      sortOrder: 'asc',
      search: '',
      skip: 0,
      limit: 10,
    });
  };

  const activeFiltersCount = [
    filters.status,
    filters.propertyType,
    filters.search,
  ].filter(Boolean).length;

  return (
    <div>
      <div className="mb-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Properties</h2>
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Clear all filters ({activeFiltersCount})
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search..."
            value={filters.search}
            onChange={(e) => updateFilter('search', e.target.value)}
            className="px-4 py-2 border rounded"
          />

          <select
            value={filters.status || ''}
            onChange={(e) => updateFilter('status', e.target.value || null)}
            className="px-4 py-2 border rounded"
          >
            <option value="">All Statuses</option>
            <option value="healthy">Healthy</option>
            <option value="alert">Alert</option>
          </select>

          <select
            value={filters.propertyType || ''}
            onChange={(e) => updateFilter('propertyType', e.target.value || null)}
            className="px-4 py-2 border rounded"
          >
            <option value="">All Types</option>
            <option value="residential">Residential</option>
            <option value="commercial">Commercial</option>
            <option value="retail">Retail</option>
            <option value="industrial">Industrial</option>
          </select>

          <select
            value={`${filters.sortBy}-${filters.sortOrder}`}
            onChange={(e) => {
              const [sortBy, sortOrder] = e.target.value.split('-');
              updateFilter('sortBy', sortBy);
              updateFilter('sortOrder', sortOrder);
            }}
            className="px-4 py-2 border rounded"
          >
            <option value="name-asc">Name (A-Z)</option>
            <option value="name-desc">Name (Z-A)</option>
            <option value="occupancy_rate-desc">Occupancy (High-Low)</option>
            <option value="occupancy_rate-asc">Occupancy (Low-High)</option>
            <option value="noi-desc">NOI (High-Low)</option>
            <option value="noi-asc">NOI (Low-High)</option>
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {properties.length} of {total} properties
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : properties.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No properties found matching your criteria
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {properties.map(property => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={previousPage}
              disabled={!hasPreviousPage}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Previous
            </button>

            <span className="text-sm">
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={nextPage}
              disabled={!hasNextPage}
              className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================================
// Example 8: Properties with Demo Mode
// ============================================================================

export function DemoPropertiesList() {
  const { properties, total, usingMockData } = useProperties({
    useMockData: true,
    limit: 10,
  });

  return (
    <div>
      {usingMockData && (
        <div className="bg-yellow-100 border border-yellow-400 rounded p-3 mb-4">
          ⚠️ Using demo data for demonstration
        </div>
      )}

      <h2>Properties ({total} total)</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {properties.map(property => (
          <PropertyCard key={property.id} property={property} />
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Helper Component: Property Card
// ============================================================================

function PropertyCard({ property }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-lg">{property.name}</h3>
        <span
          className={`
            px-2 py-1 rounded text-xs font-medium
            ${property.status === 'healthy'
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
            }
          `}
        >
          {property.status}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-3">{property.address}</p>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-500">Occupancy:</span>
          <span className="ml-1 font-medium">
            {(property.occupancy_rate * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <span className="text-gray-500">NOI:</span>
          <span className="ml-1 font-medium">
            ${(property.noi / 1000).toFixed(0)}K
          </span>
        </div>
        <div>
          <span className="text-gray-500">DSCR:</span>
          <span className="ml-1 font-medium">
            {property.dscr.toFixed(2)}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Units:</span>
          <span className="ml-1 font-medium">
            {property.units}
          </span>
        </div>
      </div>
    </div>
  );
}

