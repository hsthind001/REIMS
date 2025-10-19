# 🎨 REIMS Component Library Guide

**A comprehensive, colorful, and highly functional UI component library built with shadcn/ui principles**

---

## 📚 Table of Contents

1. [Installation](#installation)
2. [Card Components](#card-components)
3. [Metric/KPI Cards](#metrickpi-cards)
4. [Alert Components](#alert-components)
5. [Data Table](#data-table)
6. [Skeleton Loaders](#skeleton-loaders)
7. [Toast Notifications](#toast-notifications)
8. [Component Showcase](#component-showcase)

---

## 📦 Installation

All components are located in `frontend/src/components/ui/` and can be imported individually or via the index file:

```javascript
// Import individual components
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { MetricCard } from '@/components/ui/MetricCard'
import { Alert } from '@/components/ui/Alert'

// Or import from index (recommended)
import { Card, MetricCard, Alert, useToast } from '@/components/ui'
```

### Required Dependencies

```bash
npm install framer-motion lucide-react clsx tailwind-merge
```

---

## 🃏 Card Components

Beautiful cards with shadow, hover effects, and gradient options.

### Basic Card

```jsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui'

<Card variant="default" hoverable>
  <CardHeader>
    <CardTitle>Dashboard Overview</CardTitle>
    <CardDescription>Your real estate portfolio at a glance</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Portfolio value: $47.8M</p>
  </CardContent>
  <CardFooter>
    <button>View Details</button>
  </CardFooter>
</Card>
```

### Card Variants

```jsx
// Default - Clean white card
<Card variant="default">...</Card>

// Blue gradient - Brand colors
<Card variant="blue">...</Card>

// Purple gradient - AI features
<Card variant="purple">...</Card>

// Success gradient - Positive metrics
<Card variant="success">...</Card>

// Warning gradient - Attention needed
<Card variant="warning">...</Card>

// Glass effect - Modern premium look
<Card variant="glass">...</Card>
```

### Gradient Card

Bold gradient cards for special features:

```jsx
import { GradientCard } from '@/components/ui'

<GradientCard gradient="brand">
  <CardHeader>
    <CardTitle className="text-white">Premium Feature</CardTitle>
    <CardDescription className="text-white/80">Exclusive access</CardDescription>
  </CardHeader>
  <CardContent>
    <p className="text-white/90">Unlock advanced analytics...</p>
  </CardContent>
</GradientCard>
```

**Gradient Options:**
- `brand` - Blue to teal
- `ai` - Purple to indigo
- `success` - Emerald to lime
- `premium` - Indigo to purple

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'default'` | Card style variant |
| `gradient` | `string` | `'brand'` | Gradient type (GradientCard only) |
| `hoverable` | `boolean` | `true` | Enable hover animations |
| `className` | `string` | `''` | Additional CSS classes |

---

## 📊 Metric/KPI Cards

Display metrics with trend indicators and beautiful animations.

### MetricCard

```jsx
import { MetricCard } from '@/components/ui'
import { DollarSign } from 'lucide-react'

<MetricCard
  title="Monthly Revenue"
  value="$1.2M"
  change="+8.3%"
  trend="up"
  icon={DollarSign}
  variant="success"
  subtitle="Last 30 days"
/>
```

### Variants

```jsx
// Default - White background
<MetricCard variant="default" ... />

// Gradient variants with white text
<MetricCard variant="blue" ... />
<MetricCard variant="teal" ... />
<MetricCard variant="purple" ... />
<MetricCard variant="success" ... />
<MetricCard variant="warning" ... />
```

### Trend Indicators

```jsx
// Positive trend (green arrow up)
<MetricCard trend="up" change="+15%" ... />

// Negative trend (red arrow down)
<MetricCard trend="down" change="-5%" ... />

// Neutral trend (gray dash)
<MetricCard trend="neutral" change="0%" ... />
```

### Compact Metric Card

For dashboard grids:

```jsx
import { CompactMetricCard } from '@/components/ui'
import { Home } from 'lucide-react'

<CompactMetricCard
  title="Properties"
  value="184"
  icon={Home}
  color="blue"
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | required | Metric title |
| `value` | `string/number` | required | Metric value |
| `change` | `string` | `null` | Change percentage |
| `trend` | `'up'/'down'/'neutral'` | `'neutral'` | Trend direction |
| `icon` | `Component` | `null` | Lucide icon component |
| `variant` | `string` | `'default'` | Style variant |
| `subtitle` | `string` | `null` | Additional description |
| `loading` | `boolean` | `false` | Show loading state |

---

## 🚨 Alert Components

Beautiful alerts with icons, animations, and dismissible option.

### Basic Alert

```jsx
import { Alert } from '@/components/ui'

<Alert
  variant="success"
  title="Success!"
  dismissible
  onDismiss={() => console.log('Dismissed')}
>
  Your document has been uploaded successfully.
</Alert>
```

### Alert Variants

```jsx
// Success - Green
<Alert variant="success" title="Success!">
  Operation completed successfully
</Alert>

// Warning - Yellow
<Alert variant="warning" title="Warning">
  Please review pending items
</Alert>

// Error - Red
<Alert variant="error" title="Error">
  Failed to upload document
</Alert>

// Info - Blue
<Alert variant="info" title="Information">
  New features available
</Alert>

// Critical - Red gradient
<Alert variant="critical" title="Critical Alert">
  System maintenance in progress
</Alert>
```

### Inline Alert

For forms and content sections:

```jsx
import { InlineAlert } from '@/components/ui'

<InlineAlert variant="success">
  Changes saved successfully
</InlineAlert>

<InlineAlert variant="error">
  Invalid email format
</InlineAlert>
```

### Alert Container

Manage multiple alerts:

```jsx
import { AlertContainer } from '@/components/ui'

const [alerts, setAlerts] = useState([
  { id: 1, variant: 'success', title: 'Success', message: 'Done!', dismissible: true },
  { id: 2, variant: 'warning', title: 'Warning', message: 'Be careful', dismissible: true },
])

<AlertContainer
  alerts={alerts}
  onDismiss={(id) => setAlerts(alerts.filter(a => a.id !== id))}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'info'` | Alert type |
| `title` | `string` | `null` | Alert title |
| `children` | `node` | required | Alert message |
| `dismissible` | `boolean` | `false` | Show dismiss button |
| `onDismiss` | `function` | `null` | Dismiss handler |
| `icon` | `Component` | `null` | Custom icon |

---

## 📋 Data Table

Feature-rich table with sorting, filtering, searching, and export.

### Basic Usage

```jsx
import { DataTable } from '@/components/ui'

const data = [
  { id: 1, name: 'Property A', value: '$2.4M', status: 'Active' },
  { id: 2, name: 'Property B', value: '$5.2M', status: 'Pending' },
]

const columns = [
  { key: 'name', header: 'Property Name', sortable: true },
  { key: 'value', header: 'Value', sortable: true },
  { 
    key: 'status', 
    header: 'Status',
    render: (value) => (
      <span className={`badge ${value.toLowerCase()}`}>{value}</span>
    )
  },
]

<DataTable
  data={data}
  columns={columns}
  sortable
  searchable
  filterable
  exportable
  onRowClick={(row) => console.log('Clicked:', row)}
/>
```

### Column Configuration

```jsx
const columns = [
  {
    key: 'property',        // Data key
    header: 'Property Name', // Column header
    sortable: true,         // Enable sorting (default: true)
    render: (value, row) => { // Custom render function
      return <strong>{value}</strong>
    }
  },
]
```

### Features

**Sorting:** Click column headers to sort ascending/descending

**Searching:** Global search across all columns

**Filtering:** Filter by specific columns

**Export:** Export data as CSV

**Pagination:** Automatic pagination (default: 10 per page)

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `array` | `[]` | Table data |
| `columns` | `array` | `[]` | Column configuration |
| `sortable` | `boolean` | `true` | Enable sorting |
| `searchable` | `boolean` | `true` | Enable search |
| `filterable` | `boolean` | `true` | Enable filtering |
| `exportable` | `boolean` | `false` | Enable CSV export |
| `pageSize` | `number` | `10` | Rows per page |
| `onRowClick` | `function` | `null` | Row click handler |

---

## ⏳ Skeleton Loaders

Beautiful loading placeholders for data fetching.

### Basic Skeleton

```jsx
import { Skeleton } from '@/components/ui'

<Skeleton className="h-4 w-32" />
<Skeleton className="h-10 w-full" />
<Skeleton className="h-64 w-64 rounded-full" />
```

### Pre-built Skeletons

```jsx
import { 
  SkeletonCard, 
  SkeletonMetricCard, 
  SkeletonTable,
  SkeletonChart,
  SkeletonText,
  SkeletonDashboard 
} from '@/components/ui'

// Card skeleton
<SkeletonCard />

// Metric card skeleton
<SkeletonMetricCard />

// Table skeleton
<SkeletonTable rows={5} columns={4} />

// Chart skeleton
<SkeletonChart />

// Text skeleton
<SkeletonText lines={3} />

// Complete dashboard skeleton
<SkeletonDashboard />
```

### Conditional Loading

```jsx
{loading ? (
  <SkeletonMetricCard />
) : (
  <MetricCard title="Revenue" value="$1.2M" />
)}
```

---

## 🍞 Toast Notifications

Beautiful toast notifications with animations and auto-dismiss.

### Setup

Wrap your app with `ToastProvider`:

```jsx
import { ToastProvider } from '@/components/ui'

function App() {
  return (
    <ToastProvider>
      <YourApp />
    </ToastProvider>
  )
}
```

### Usage

```jsx
import { useToast } from '@/components/ui'

function MyComponent() {
  const { toast } = useToast()

  const handleSuccess = () => {
    toast.success('Document uploaded successfully!')
  }

  const handleError = () => {
    toast.error('Failed to upload document', {
      title: 'Upload Error',
      action: {
        label: 'Retry',
        onClick: () => handleRetry()
      }
    })
  }

  const handleWarning = () => {
    toast.warning('Please review pending items')
  }

  const handleInfo = () => {
    toast.info('New features are available!')
  }

  return (
    <button onClick={handleSuccess}>Upload</button>
  )
}
```

### Custom Options

```jsx
toast.success('Saved!', {
  title: 'Changes Saved',
  duration: 3000, // ms (default: 5000)
  action: {
    label: 'Undo',
    onClick: () => undoChanges()
  }
})

// Infinite duration (must be dismissed manually)
toast.info('Important message', {
  duration: Infinity
})
```

### Toast Methods

```javascript
toast.success(message, options)  // Green toast
toast.error(message, options)    // Red toast
toast.warning(message, options)  // Yellow toast
toast.info(message, options)     // Blue toast
toast(message)                   // Default info toast
```

---

## 🎨 Component Showcase

View all components in action with the interactive showcase:

```jsx
import ComponentShowcase from '@/components/ComponentShowcase'

function App() {
  return <ComponentShowcase />
}
```

Navigate to `/showcase` (after setting up routing) to see:
- All card variants
- Metric cards with different trends
- All alert types
- Data table with sorting/filtering
- Skeleton loaders
- Toast notification demos

---

## 🎯 Design Features

### Color System Integration

All components use the REIMS color system:
- **Brand colors:** Blue/Teal for trust and innovation
- **Accent colors:** Purple for AI features
- **Status colors:** Green/Yellow/Red for states
- **Gradients:** Professional gradient combinations

### Animations

Powered by Framer Motion:
- Smooth enter/exit animations
- Hover effects
- Scale transformations
- Stagger animations for lists

### Dark Mode

All components support dark mode:
```jsx
<html className="dark">
  {/* Components automatically adapt */}
</html>
```

### Accessibility

- WCAG AAA compliant colors
- Keyboard navigation support
- Screen reader friendly
- Focus indicators

---

## 📝 Best Practices

### Performance

```jsx
// ✅ Good - Lazy load heavy components
const DataTable = lazy(() => import('@/components/ui/DataTable'))

// ✅ Good - Show skeleton while loading
{loading ? <SkeletonCard /> : <Card>...</Card>}

// ✅ Good - Memoize table data
const memoizedData = useMemo(() => processData(rawData), [rawData])
```

### Composition

```jsx
// ✅ Good - Compose cards with content
<Card variant="blue">
  <CardHeader>
    <CardTitle>Analytics</CardTitle>
  </CardHeader>
  <CardContent>
    <MetricCard title="Revenue" value="$1.2M" />
  </CardContent>
</Card>
```

### Error Handling

```jsx
// ✅ Good - Show errors with alerts and toasts
try {
  await uploadDocument()
  toast.success('Upload successful!')
} catch (error) {
  toast.error(error.message, {
    title: 'Upload Failed',
    action: { label: 'Retry', onClick: retry }
  })
}
```

---

## 🚀 Quick Start Examples

### Dashboard with Metrics

```jsx
import { MetricCard, Card, CardContent } from '@/components/ui'
import { DollarSign, Users, Home } from 'lucide-react'

function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-6">
        <MetricCard
          title="Revenue"
          value="$1.2M"
          change="+8.3%"
          trend="up"
          icon={DollarSign}
          variant="success"
        />
        <MetricCard
          title="Properties"
          value="184"
          change="+12"
          trend="up"
          icon={Home}
          variant="blue"
        />
        <MetricCard
          title="Occupancy"
          value="94.6%"
          change="-2.1%"
          trend="down"
          icon={Users}
          variant="warning"
        />
      </div>
    </div>
  )
}
```

### Property List with Table

```jsx
import { DataTable } from '@/components/ui'

function PropertyList({ properties }) {
  const columns = [
    { key: 'name', header: 'Property' },
    { key: 'location', header: 'Location' },
    { key: 'value', header: 'Value' },
  ]

  return (
    <DataTable
      data={properties}
      columns={columns}
      searchable
      exportable
    />
  )
}
```

### Upload with Feedback

```jsx
import { useToast } from '@/components/ui'
import { Alert } from '@/components/ui'

function FileUpload() {
  const { toast } = useToast()
  const [error, setError] = useState(null)

  const handleUpload = async (file) => {
    try {
      await uploadFile(file)
      toast.success('File uploaded successfully!')
      setError(null)
    } catch (err) {
      setError(err.message)
      toast.error('Upload failed')
    }
  }

  return (
    <div>
      {error && (
        <Alert variant="error" dismissible onDismiss={() => setError(null)}>
          {error}
        </Alert>
      )}
      <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
    </div>
  )
}
```

---

## 🎨 Component Summary

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `Card` | Content container | 6 variants, hover effects, gradients |
| `MetricCard` | KPI display | Trend indicators, icons, loading state |
| `Alert` | User notifications | 5 variants, dismissible, animations |
| `DataTable` | Data display | Sorting, filtering, search, export |
| `Skeleton` | Loading states | Pre-built layouts, smooth animations |
| `Toast` | Feedback | Auto-dismiss, actions, 4 types |

---

**Your REIMS component library is ready for production! 🎉**

**Start building beautiful, colorful interfaces today!**

















