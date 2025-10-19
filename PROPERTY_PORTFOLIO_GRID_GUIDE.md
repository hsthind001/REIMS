# 🏢 REIMS Property Portfolio Grid - Complete Guide

**A comprehensive property management grid with filtering, search, and interactive cards**

---

## 📋 Overview

The Property Portfolio Grid provides:

✅ **Property cards** with image/gradient overlays  
✅ **Key metrics** (occupancy, NOI, DSCR) with color coding  
✅ **Status badges** (healthy/warning/critical)  
✅ **Quick action buttons** (view, edit, analyze)  
✅ **Search functionality** by name/address  
✅ **Status filtering** (all/healthy/warning/critical)  
✅ **Sorting options** (name, occupancy, NOI, DSCR)  
✅ **Hover effects** revealing additional metrics  
✅ **Responsive grid** layout  
✅ **Dark mode support**  

---

## 🚀 Quick Start

### Basic Usage

```jsx
import PropertyPortfolioGrid from '@/components/PropertyPortfolioGrid'

function Dashboard() {
  const properties = [
    {
      id: 1,
      name: 'Sunset Apartments',
      address: '123 Main St, Los Angeles, CA',
      type: 'Residential',
      status: 'healthy',
      occupancy: 96.5,
      noi: 85000,
      dscr: 1.75,
      units: 24,
      value: 4200000,
      yearBuilt: 2018,
      capRate: 6.2,
      image: null // or image URL
    },
    // ... more properties
  ]

  return (
    <PropertyPortfolioGrid
      properties={properties}
      onViewProperty={(property) => console.log('View', property)}
      onEditProperty={(property) => console.log('Edit', property)}
      onAnalyzeProperty={(property) => console.log('Analyze', property)}
    />
  )
}
```

---

## 📖 Component API

### PropertyPortfolioGrid Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `properties` | `array` | `[]` | Array of property objects |
| `onViewProperty` | `function` | `null` | Callback when view button clicked |
| `onEditProperty` | `function` | `null` | Callback when edit button clicked |
| `onAnalyzeProperty` | `function` | `null` | Callback when analyze button clicked |

### Property Object Structure

```typescript
{
  id: number | string           // Unique identifier
  name: string                  // Property name
  address: string               // Full address
  type: string                  // 'Residential', 'Commercial', 'Mixed-Use'
  status: string                // 'healthy', 'warning', 'critical'
  occupancy: number             // Percentage (0-100)
  noi: number                   // Net Operating Income (annual)
  dscr: number                  // Debt Service Coverage Ratio
  units: number                 // Number of units
  value: number                 // Property value
  yearBuilt: number             // Year built
  capRate: number               // Capitalization rate (percentage)
  image?: string                // Optional image URL
}
```

---

## 🎨 Features Breakdown

### 1. Search Functionality

Real-time search across property names and addresses:

```jsx
// Searches both name and address fields
<input
  type="text"
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  placeholder="Search properties..."
/>
```

**Features:**
- Case-insensitive search
- Instant results
- Searches name and address
- Clear search indicator

### 2. Status Filtering

Filter properties by health status:

```jsx
const statusCounts = {
  all: properties.length,
  healthy: properties.filter(p => p.status === 'healthy').length,
  warning: properties.filter(p => p.status === 'warning').length,
  critical: properties.filter(p => p.status === 'critical').length,
}
```

**Status Types:**
- **Healthy** (🟢): All metrics in good range
- **Warning** (🟡): Some metrics need attention
- **Critical** (🔴): Critical issues detected

### 3. Sorting Options

Sort by any key metric:

```jsx
// Available sort fields
const sortOptions = [
  { value: 'name', label: 'Name' },
  { value: 'occupancy', label: 'Occupancy' },
  { value: 'noi', label: 'NOI' },
  { value: 'dscr', label: 'DSCR' },
]

// Toggle between ascending/descending
const toggleSort = (field) => {
  if (sortBy === field) {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  } else {
    setSortBy(field)
    setSortOrder('asc')
  }
}
```

### 4. Property Cards

Each card displays:

**Always Visible:**
- Property image or gradient placeholder
- Property name
- Address with map pin icon
- Property type badge
- Status badge
- Occupancy percentage
- NOI (Net Operating Income)
- DSCR (Debt Service Coverage Ratio)
- Action buttons (View, Edit, Analyze)

**Revealed on Hover:**
- Number of units
- Property value
- Year built
- Capitalization rate

### 5. Color-Coded Metrics

Automatic color coding based on thresholds:

```javascript
const getMetricColor = (value, type) => {
  if (type === 'occupancy') {
    if (value >= 95) return 'text-growth-emerald-600' // Green
    if (value >= 85) return 'text-status-warning-600'  // Yellow
    return 'text-status-error-600'                     // Red
  }
  // ... similar for NOI and DSCR
}
```

**Occupancy Thresholds:**
- 🟢 ≥95%: Excellent
- 🟡 85-94%: Good
- 🔴 <85%: Needs Attention

**NOI Thresholds:**
- 🟢 ≥$50K: Strong
- 🟡 $25K-$50K: Moderate
- 🔴 <$25K: Weak

**DSCR Thresholds:**
- 🟢 ≥1.5: Excellent
- 🟡 1.2-1.49: Adequate
- 🔴 <1.2: At Risk

### 6. Image/Gradient Overlays

Properties without images get beautiful gradient placeholders:

```jsx
{property.image ? (
  <img src={property.image} alt={property.name} />
) : (
  <div className="bg-gradient-to-br from-brand-blue-400 via-accent-purple-400 to-brand-teal-400">
    <Home className="w-16 h-16 text-white/30" />
  </div>
)}

{/* Gradient overlay on all images */}
<div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
```

### 7. Quick Actions

Three action buttons per card:

```jsx
<button onClick={() => onView()}>
  <Eye /> View
</button>

<button onClick={() => onEdit()}>
  <Edit /> Edit
</button>

<button onClick={() => onAnalyze()}>
  <BarChart3 /> Analyze
</button>
```

**Features:**
- Toast notifications on click
- Distinct styling per action
- Hover/tap animations
- Event propagation control

---

## 🎯 Complete Example

```jsx
import { useState } from 'react'
import PropertyPortfolioGrid, { generateSampleProperties } from '@/components/PropertyPortfolioGrid'
import { ToastProvider, useToast } from '@/components/ui/Toast'

function PropertyManagement() {
  const { toast } = useToast()
  const [properties] = useState(() => generateSampleProperties(12))

  const handleViewProperty = (property) => {
    toast.info(`Opening ${property.name}`)
    // Navigate to property detail page
    navigate(`/properties/${property.id}`)
  }

  const handleEditProperty = (property) => {
    toast.info(`Editing ${property.name}`)
    // Open edit modal or navigate to edit page
    setEditingProperty(property)
    setShowEditModal(true)
  }

  const handleAnalyzeProperty = (property) => {
    toast.info(`Analyzing ${property.name}`)
    // Fetch AI insights
    analyzePropertyWithAI(property.id)
  }

  return (
    <div className="p-8">
      <h1>Property Portfolio</h1>
      
      <PropertyPortfolioGrid
        properties={properties}
        onViewProperty={handleViewProperty}
        onEditProperty={handleEditProperty}
        onAnalyzeProperty={handleAnalyzeProperty}
      />
    </div>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <PropertyManagement />
    </ToastProvider>
  )
}
```

---

## 🎨 Hover Effects

### Card Lift

```jsx
// Card lifts up 8px on hover
whileHover={{ y: -8 }}
```

### Shadow Expansion

```css
shadow-lg hover:shadow-2xl
```

### Glow Effect

```jsx
<motion.div
  style={{
    boxShadow: isHovered ? '0 0 40px rgba(37, 99, 235, 0.3)' : 'none',
  }}
/>
```

### Image Zoom

```css
.group-hover:scale-110
transition-transform duration-500
```

### Reveal Additional Metrics

```jsx
<AnimatePresence>
  {isHovered && (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
    >
      {/* Additional metrics */}
    </motion.div>
  )}
</AnimatePresence>
```

---

## 📱 Responsive Design

### Grid Breakpoints

```jsx
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
```

| Breakpoint | Columns |
|------------|---------|
| Mobile (< 768px) | 1 |
| Tablet (768px - 1024px) | 2 |
| Desktop (1024px - 1280px) | 3 |
| Large (≥ 1280px) | 4 |

### Mobile Optimizations

- Stack filters vertically
- Full-width search bar
- Touch-friendly buttons
- Larger tap targets
- Readable font sizes

---

## 🔍 Search & Filter Logic

### Combined Filtering

```javascript
const filteredAndSortedProperties = useMemo(() => {
  let filtered = properties

  // 1. Apply search filter
  if (searchQuery) {
    filtered = filtered.filter(property =>
      property.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      property.address.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  // 2. Apply status filter
  if (statusFilter !== 'all') {
    filtered = filtered.filter(property => property.status === statusFilter)
  }

  // 3. Apply sorting
  filtered = [...filtered].sort((a, b) => {
    const aValue = a[sortBy]
    const bValue = b[sortBy]
    
    if (typeof aValue === 'number') {
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
    }
    
    return sortOrder === 'asc'
      ? aValue.localeCompare(bValue)
      : bValue.localeCompare(aValue)
  })

  return filtered
}, [properties, searchQuery, statusFilter, sortBy, sortOrder])
```

---

## 🎭 Animations

### Card Entry

```jsx
initial={{ opacity: 0, scale: 0.9 }}
animate={{ opacity: 1, scale: 1 }}
transition={{ delay: index * 0.05 }}
```

**Effect:** Staggered fade-in with scale

### Filter Panel

```jsx
initial={{ height: 0, opacity: 0 }}
animate={{ height: 'auto', opacity: 1 }}
exit={{ height: 0, opacity: 0 }}
```

**Effect:** Smooth expand/collapse

### Button Interactions

```jsx
whileHover={{ scale: 1.05 }}
whileTap={{ scale: 0.95 }}
```

**Effect:** Gentle press feedback

---

## 🧪 Testing

### Test Scenarios

1. **Search**
   - Search by property name
   - Search by address
   - Clear search
   - No results state

2. **Filtering**
   - Filter by each status
   - View status counts
   - Combine with search

3. **Sorting**
   - Sort by name
   - Sort by occupancy
   - Sort by NOI
   - Sort by DSCR
   - Toggle asc/desc

4. **Interactions**
   - Hover card
   - Click action buttons
   - Toast notifications

5. **Responsive**
   - Mobile view
   - Tablet view
   - Desktop view
   - Large screens

---

## 💾 Data Integration

### Real API Data

```jsx
import { useQuery } from '@tanstack/react-query'

function PropertyPortfolio() {
  const { data: properties, isLoading } = useQuery({
    queryKey: ['properties'],
    queryFn: async () => {
      const response = await fetch('/api/properties')
      return response.json()
    }
  })

  if (isLoading) {
    return <SkeletonGrid />
  }

  return <PropertyPortfolioGrid properties={properties} />
}
```

### Live Updates

```jsx
// Poll for updates every 30 seconds
useQuery({
  queryKey: ['properties'],
  queryFn: fetchProperties,
  refetchInterval: 30000
})
```

---

## 🎨 Customization

### Custom Thresholds

```javascript
// Override metric thresholds
const getMetricColor = (value, type) => {
  if (type === 'occupancy') {
    if (value >= 98) return 'text-growth-emerald-600' // Higher bar
    if (value >= 90) return 'text-status-warning-600'
    return 'text-status-error-600'
  }
}
```

### Custom Status Badges

```jsx
const statusConfig = {
  healthy: {
    color: 'bg-growth-emerald-500',
    label: 'Excellent',
    icon: TrendingUp,
  },
  // ... custom statuses
}
```

### Custom Grid Layout

```jsx
// 5 columns on very large screens
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5"
```

---

## 🛠️ Helper Functions

### Generate Sample Data

```javascript
import { generateSampleProperties } from '@/components/PropertyPortfolioGrid'

// Generate 20 sample properties
const properties = generateSampleProperties(20)
```

---

## 📊 Component Stats

- ✅ **600+ lines** of code
- ✅ **Search, filter, sort** functionality
- ✅ **Color-coded metrics** (3 types)
- ✅ **Status badges** (3 states)
- ✅ **Quick actions** (3 buttons)
- ✅ **Hover effects** (multiple)
- ✅ **Responsive grid** (4 breakpoints)
- ✅ **Dark mode** support
- ✅ **Animation** powered
- ✅ **Production-ready**

---

## 🎉 Summary

### What You Have

✅ **Property Grid** - Responsive card layout  
✅ **Search & Filter** - Real-time results  
✅ **Color Coding** - Automatic metric thresholds  
✅ **Status Badges** - Visual health indicators  
✅ **Hover Effects** - Reveal additional details  
✅ **Quick Actions** - View, edit, analyze  
✅ **Sorting Options** - Multiple sort fields  
✅ **Empty State** - Helpful no-results message  
✅ **Dark Mode** - Full theme support  
✅ **Animations** - Smooth transitions  

---

**Your REIMS property portfolio grid is production-ready! 🚀**

Start managing your properties with this powerful, feature-rich component!

















