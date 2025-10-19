# useProperties Hook - Documentation

**Custom React hook for fetching and managing properties list with pagination, filtering, sorting, and search capabilities.**

---

## 🎯 Features

✅ **Pagination Support** - Skip/limit with page navigation  
✅ **Filtering** - By status, property type  
✅ **Sorting** - By name, occupancy, NOI, DSCR  
✅ **Search** - By name or address  
✅ **Caching** - Smart cache keys based on query params  
✅ **Mock Data Fallback** - Demo mode when API unavailable  
✅ **Loading States** - Track loading and fetching  
✅ **Error Handling** - User-friendly error messages  
✅ **Single Property Fetch** - `useProperty(id)` variant  
✅ **Infinite Scroll** - `useInfiniteProperties()` variant  

---

## 🚀 Quick Start

### Basic Usage

```jsx
import useProperties from '@/hooks/useProperties';

function PropertiesList() {
  const { properties, isLoading, error } = useProperties();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {properties.map(property => (
        <div key={property.id}>
          <h3>{property.name}</h3>
          <p>{property.address}</p>
          <p>Occupancy: {(property.occupancy_rate * 100).toFixed(1)}%</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 📖 API Reference

### useProperties(options)

Main hook for fetching properties list.

#### Parameters

```typescript
options: {
  skip?: number,              // Records to skip (default: 0)
  limit?: number,             // Records per page (default: 20)
  status?: 'healthy' | 'alert' | null,  // Filter by status
  sortBy?: 'name' | 'occupancy_rate' | 'noi' | 'dscr',  // Sort field
  sortOrder?: 'asc' | 'desc', // Sort direction (default: 'asc')
  search?: string,            // Search query
  propertyType?: 'residential' | 'commercial' | 'retail' | 'industrial' | null,
  useMockData?: boolean,      // Force mock data (default: false)
  enableAutoRefetch?: boolean, // Auto-refetch (default: false)
  refetchInterval?: number,   // Refetch interval ms (default: 5 min)
  staleTime?: number,         // Cache duration ms (default: 3 min)
}
```

#### Return Object

```typescript
{
  properties: Array<Property>,  // Properties array
  total: number,                // Total count
  isLoading: boolean,           // Initial load state
  error: string | null,         // Error message
  refetch: () => Promise,       // Manual refetch function
  isFetching: boolean,          // Background fetch state
  isError: boolean,             // Error flag
  isSuccess: boolean,           // Success flag
  hasNextPage: boolean,         // More results available
  hasPreviousPage: boolean,     // Previous page exists
  currentPage: number,          // Current page number
  totalPages: number,           // Total pages
  usingMockData: boolean,       // Mock data indicator
}
```

### Property Object Structure

```typescript
{
  id: string,
  name: string,
  address: string,
  occupancy_rate: number,       // 0-1 (e.g., 0.95 = 95%)
  noi: number,                  // Net Operating Income
  dscr: number,                 // Debt Service Coverage Ratio
  status: 'healthy' | 'alert',
  property_type: 'residential' | 'commercial' | 'retail' | 'industrial',
  units: number,
  square_footage: number,
  year_built: number,
}
```

---

## 📊 Examples

### 1. Basic List

```jsx
function BasicList() {
  const { properties, isLoading } = useProperties({
    limit: 10,
  });

  return (
    <div>
      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}
```

### 2. Pagination

```jsx
function PaginatedList() {
  const [skip, setSkip] = useState(0);
  const limit = 10;

  const {
    properties,
    total,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
  } = useProperties({ skip, limit });

  return (
    <div>
      <div>Page {currentPage} of {totalPages}</div>
      
      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}

      <button
        onClick={() => setSkip(skip - limit)}
        disabled={!hasPreviousPage}
      >
        Previous
      </button>

      <button
        onClick={() => setSkip(skip + limit)}
        disabled={!hasNextPage}
      >
        Next
      </button>
    </div>
  );
}
```

### 3. Filtering

```jsx
function FilteredList() {
  const [status, setStatus] = useState(null);

  const { properties } = useProperties({
    status,
    limit: 20,
  });

  return (
    <div>
      <select value={status || ''} onChange={(e) => setStatus(e.target.value || null)}>
        <option value="">All</option>
        <option value="healthy">Healthy</option>
        <option value="alert">Alert</option>
      </select>

      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}
```

### 4. Sorting

```jsx
function SortedList() {
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  const { properties } = useProperties({
    sortBy,
    sortOrder,
  });

  return (
    <div>
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="name">Name</option>
        <option value="occupancy_rate">Occupancy</option>
        <option value="noi">NOI</option>
        <option value="dscr">DSCR</option>
      </select>

      <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>

      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}
```

### 5. Search

```jsx
function SearchableList() {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 500);
    return () => clearTimeout(timer);
  }, [search]);

  const { properties, total } = useProperties({
    search: debouncedSearch,
  });

  return (
    <div>
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search properties..."
      />

      <p>Found {total} properties</p>

      {properties.map(property => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}
```

### 6. Combined Filters

```jsx
function AdvancedList() {
  const [filters, setFilters] = useState({
    status: null,
    sortBy: 'name',
    sortOrder: 'asc',
    search: '',
    skip: 0,
    limit: 10,
  });

  const { properties, total, currentPage, totalPages } = useProperties(filters);

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      skip: 0, // Reset to first page
    }));
  };

  return (
    <div>
      {/* Filters UI */}
      {/* Results */}
    </div>
  );
}
```

---

## 🎯 Hook Variants

### 1. useProperty(id, options)

Fetch a single property by ID.

```jsx
import { useProperty } from '@/hooks/useProperties';

function PropertyDetail({ id }) {
  const { property, isLoading, error } = useProperty(id);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!property) return <div>Not found</div>;

  return (
    <div>
      <h1>{property.name}</h1>
      <p>{property.address}</p>
      <p>Occupancy: {(property.occupancy_rate * 100).toFixed(1)}%</p>
    </div>
  );
}
```

### 2. useInfiniteProperties(options)

Infinite scroll implementation.

```jsx
import { useInfiniteProperties } from '@/hooks/useProperties';

function InfiniteList() {
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
      {properties.map((property, index) => (
        <PropertyCard key={`${property.id}-${index}`} property={property} />
      ))}

      {hasNextPage && (
        <button onClick={loadMore} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

---

## 🔄 Caching Behavior

### Cache Keys

The hook generates unique cache keys based on query parameters:

```javascript
// Different cache keys for different queries
'properties-skip:0|limit:20|sortBy:name'
'properties-skip:0|limit:20|status:healthy'
'properties-skip:0|limit:20|search:sunset'
```

### Cache Duration

- **Default:** 3 minutes
- **Customizable:** via `staleTime` option

```jsx
const { properties } = useProperties({
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

### Auto-Refresh

```jsx
const { properties } = useProperties({
  enableAutoRefetch: true,
  refetchInterval: 2 * 60 * 1000, // 2 minutes
});
```

---

## 🛡️ Error Handling

### Network Errors

```jsx
const { properties, error, refetch } = useProperties();

if (error) {
  return (
    <div>
      <p>Error: {error}</p>
      <button onClick={refetch}>Retry</button>
    </div>
  );
}
```

### Mock Data Fallback

```jsx
// Automatically falls back to mock data on API error
const { properties, usingMockData } = useProperties();

if (usingMockData) {
  return (
    <div className="warning">
      Using demo data - API unavailable
    </div>
  );
}
```

### Force Mock Data

```jsx
const { properties } = useProperties({
  useMockData: true, // Always use mock data
});
```

---

## 📱 Responsive Pagination

### Calculate Page Info

```jsx
const { currentPage, totalPages, hasNextPage, hasPreviousPage } = useProperties({
  skip: page * limit,
  limit,
});

// currentPage: 1, 2, 3, ...
// totalPages: calculated from total / limit
// hasNextPage: boolean
// hasPreviousPage: boolean
```

### Page Navigation

```jsx
function PaginationControls({ currentPage, totalPages, onPageChange }) {
  return (
    <div>
      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={page === currentPage ? 'active' : ''}
        >
          {page}
        </button>
      ))}
    </div>
  );
}
```

---

## 💡 Best Practices

### 1. Debounce Search Input

```jsx
✅ Good: Debounce search to avoid excessive API calls
const [search, setSearch] = useState('');
const [debouncedSearch, setDebouncedSearch] = useState('');

useEffect(() => {
  const timer = setTimeout(() => setDebouncedSearch(search), 500);
  return () => clearTimeout(timer);
}, [search]);

const { properties } = useProperties({ search: debouncedSearch });
```

### 2. Reset Pagination on Filter Change

```jsx
✅ Good: Reset to first page when filters change
const updateFilter = (key, value) => {
  setFilters(prev => ({
    ...prev,
    [key]: value,
    skip: 0, // Reset!
  }));
};
```

### 3. Handle Loading States

```jsx
✅ Good: Show loading skeleton
if (isLoading) {
  return (
    <div>
      <PropertySkeleton />
      <PropertySkeleton />
      <PropertySkeleton />
    </div>
  );
}

❌ Bad: No loading indicator
```

### 4. Display Total Count

```jsx
✅ Good: Show how many results
const { properties, total } = useProperties();

return (
  <div>
    <h2>Properties ({total} total)</h2>
    {/* ... */}
  </div>
);
```

### 5. Normalize Occupancy Rate

```jsx
✅ Good: Convert 0-1 to percentage
<p>Occupancy: {(property.occupancy_rate * 100).toFixed(1)}%</p>

❌ Bad: Show raw decimal
<p>Occupancy: {property.occupancy_rate}</p>
```

---

## 🐛 Troubleshooting

### Properties Not Loading

**Problem:** Empty properties array

**Solutions:**
1. Check backend is running
2. Verify endpoint `/api/properties` exists
3. Enable mock data for testing:
   ```jsx
   const { properties } = useProperties({ useMockData: true });
   ```

### Pagination Not Working

**Problem:** Same page shows repeatedly

**Solutions:**
1. Ensure `skip` is calculated correctly:
   ```jsx
   const skip = (page - 1) * limit;
   ```
2. Check cache keys are unique per page
3. Verify `total` is returned from API

### Search Not Working

**Problem:** Search doesn't filter results

**Solutions:**
1. Debounce search input (wait 500ms)
2. Check search query is passed correctly
3. Verify backend supports `search` parameter

### Slow Performance

**Problem:** Hook re-renders too often

**Solutions:**
1. Use `useMemo` for derived values
2. Debounce search input
3. Increase `staleTime` to cache longer
4. Disable auto-refetch if not needed

---

## 📊 Performance Optimization

### Memoize Filters

```jsx
const filters = useMemo(() => ({
  status,
  sortBy,
  sortOrder,
  search: debouncedSearch,
  skip,
  limit,
}), [status, sortBy, sortOrder, debouncedSearch, skip, limit]);

const { properties } = useProperties(filters);
```

### Virtualize Long Lists

```jsx
import { FixedSizeList } from 'react-window';

function VirtualizedList() {
  const { properties } = useProperties({ limit: 1000 });

  return (
    <FixedSizeList
      height={600}
      itemCount={properties.length}
      itemSize={100}
    >
      {({ index, style }) => (
        <div style={style}>
          <PropertyCard property={properties[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

---

## 📚 API Expectations

### Expected API Response

```json
GET /api/properties?skip=0&limit=20&status=healthy&sort_by=name&sort_order=asc&search=sunset

{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop-001",
        "name": "Sunset Apartments",
        "address": "123 Sunset Blvd, Los Angeles, CA",
        "occupancy_rate": 0.95,
        "noi": 450000,
        "dscr": 1.45,
        "status": "healthy",
        "property_type": "residential",
        "units": 24,
        "square_footage": 18500,
        "year_built": 2018
      }
    ],
    "total": 184
  }
}
```

**Note:** Hook automatically extracts `data` field and normalizes property objects.

---

## ✅ Summary

The `useProperties` hook provides a complete solution for managing properties data:

✅ **Pagination** - Skip/limit with page helpers  
✅ **Filtering** - By status, type  
✅ **Sorting** - Multiple fields, asc/desc  
✅ **Search** - Name or address  
✅ **Caching** - Smart cache keys  
✅ **Error Handling** - Graceful failures  
✅ **Mock Data** - Demo mode  
✅ **Variants** - Single property, infinite scroll  

**Perfect for property management interfaces!** 🚀

