# 🎨 REIMS Component Library - Quick Reference

**Fast copy-paste examples for daily development**

---

## 📦 Import

```javascript
import { 
  Card, CardHeader, CardTitle, CardContent,
  MetricCard, CompactMetricCard,
  Alert, InlineAlert,
  DataTable,
  Skeleton, SkeletonCard,
  useToast
} from '@/components/ui'
```

---

## 🃏 Cards

```jsx
// Basic Card
<Card variant="default">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Gradient Card
<GradientCard gradient="brand">
  <CardContent className="text-white">Premium feature</CardContent>
</GradientCard>

// Variants: default, blue, purple, success, warning, glass
// Gradients: brand, ai, success, premium
```

---

## 📊 Metrics

```jsx
import { DollarSign } from 'lucide-react'

// Full Metric Card
<MetricCard
  title="Revenue"
  value="$1.2M"
  change="+8.3%"
  trend="up"
  icon={DollarSign}
  variant="success"
/>

// Compact Metric
<CompactMetricCard
  title="Properties"
  value="184"
  icon={Home}
  color="blue"
/>

// Trends: up, down, neutral
// Variants: default, blue, teal, purple, success, warning
```

---

## 🚨 Alerts

```jsx
// Success Alert
<Alert variant="success" title="Success!" dismissible>
  Operation completed successfully
</Alert>

// Error Alert
<Alert variant="error" title="Error" dismissible>
  Something went wrong
</Alert>

// Inline Alert (for forms)
<InlineAlert variant="warning">
  Please check your input
</InlineAlert>

// Variants: success, warning, error, info, critical
```

---

## 📋 Data Table

```jsx
const data = [
  { id: 1, name: 'Item 1', value: '$100', status: 'Active' },
  { id: 2, name: 'Item 2', value: '$200', status: 'Pending' },
]

const columns = [
  { key: 'name', header: 'Name', sortable: true },
  { key: 'value', header: 'Value', sortable: true },
  { 
    key: 'status', 
    header: 'Status',
    render: (value) => <span className="badge">{value}</span>
  },
]

<DataTable
  data={data}
  columns={columns}
  sortable
  searchable
  exportable
  onRowClick={(row) => console.log(row)}
/>
```

---

## ⏳ Skeletons

```jsx
// Basic Skeleton
<Skeleton className="h-4 w-32" />

// Pre-built Skeletons
<SkeletonCard />
<SkeletonMetricCard />
<SkeletonTable rows={5} columns={4} />

// Conditional Loading
{loading ? <SkeletonCard /> : <Card>...</Card>}
```

---

## 🍞 Toast

```jsx
// Setup (in App.jsx)
import { ToastProvider } from '@/components/ui'

<ToastProvider>
  <App />
</ToastProvider>

// Usage
import { useToast } from '@/components/ui'

function MyComponent() {
  const { toast } = useToast()

  // Success
  toast.success('Document uploaded!')

  // Error with action
  toast.error('Upload failed', {
    title: 'Error',
    action: {
      label: 'Retry',
      onClick: () => retry()
    }
  })

  // Warning
  toast.warning('Please review')

  // Info
  toast.info('New features available')
}
```

---

## 🎨 Color Variants

**Cards & Metrics:**
- `variant="default"` - White background
- `variant="blue"` - Brand blue gradient
- `variant="purple"` - AI/premium purple
- `variant="success"` - Success green gradient
- `variant="warning"` - Warning yellow gradient
- `variant="glass"` - Glass morphism effect

**Alerts:**
- `variant="success"` - Green
- `variant="warning"` - Yellow
- `variant="error"` - Red
- `variant="info"` - Blue
- `variant="critical"` - Red gradient

---

## 🔥 Common Patterns

### Dashboard Grid

```jsx
<div className="grid grid-cols-4 gap-6">
  <MetricCard title="Revenue" value="$1.2M" trend="up" variant="success" />
  <MetricCard title="Properties" value="184" trend="up" variant="blue" />
  <MetricCard title="Occupancy" value="94%" trend="down" variant="warning" />
  <MetricCard title="Documents" value="1.2K" trend="neutral" variant="purple" />
</div>
```

### Form with Validation

```jsx
const { toast } = useToast()
const [error, setError] = useState(null)

<form onSubmit={handleSubmit}>
  {error && (
    <Alert variant="error" dismissible onDismiss={() => setError(null)}>
      {error}
    </Alert>
  )}
  
  <input type="text" />
  <button type="submit">Submit</button>
</form>

// On success:
toast.success('Form submitted!')
```

### Loading State

```jsx
{loading ? (
  <div className="space-y-6">
    <SkeletonMetricCard />
    <SkeletonTable rows={5} columns={4} />
  </div>
) : (
  <div className="space-y-6">
    <MetricCard {...data} />
    <DataTable data={tableData} columns={columns} />
  </div>
)}
```

### Property Card

```jsx
<Card variant="blue" hoverable>
  <CardHeader>
    <CardTitle>Sunset Apartments</CardTitle>
    <CardDescription>Los Angeles, CA</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="space-y-2">
      <div className="flex justify-between">
        <span>Value:</span>
        <span className="font-bold">$2.4M</span>
      </div>
      <div className="flex justify-between">
        <span>Occupancy:</span>
        <span className="font-bold">94%</span>
      </div>
    </div>
  </CardContent>
  <CardFooter>
    <button className="w-full btn-primary">View Details</button>
  </CardFooter>
</Card>
```

---

## 💡 Pro Tips

```jsx
// ✅ Combine variants for emphasis
<MetricCard variant="success" trend="up" />

// ✅ Use skeletons for better UX
{loading ? <SkeletonCard /> : <Card>...</Card>}

// ✅ Stack alerts for multiple messages
<AlertContainer alerts={alertList} />

// ✅ Custom cell renderers in tables
{
  key: 'value',
  render: (value) => <span className="font-bold text-brand-blue-600">{value}</span>
}

// ✅ Toast with actions
toast.error('Failed', {
  action: { label: 'Retry', onClick: retry }
})
```

---

## 🚀 Complete Example

```jsx
import { useState } from 'react'
import {
  Card, CardHeader, CardTitle, CardContent,
  MetricCard,
  DataTable,
  Alert,
  SkeletonMetricCard,
  useToast
} from '@/components/ui'
import { DollarSign, Home } from 'lucide-react'

function Dashboard() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  const metrics = [
    { title: 'Revenue', value: '$1.2M', change: '+8%', trend: 'up' },
    { title: 'Properties', value: '184', change: '+12', trend: 'up' },
  ]

  const tableData = [...]
  const columns = [...]

  return (
    <div className="space-y-6">
      {/* Metrics */}
      <div className="grid grid-cols-2 gap-6">
        {loading ? (
          <>
            <SkeletonMetricCard />
            <SkeletonMetricCard />
          </>
        ) : (
          metrics.map(m => (
            <MetricCard
              key={m.title}
              title={m.title}
              value={m.value}
              change={m.change}
              trend={m.trend}
              variant="success"
            />
          ))
        )}
      </div>

      {/* Alerts */}
      <Alert variant="info" title="Welcome">
        Your dashboard is ready!
      </Alert>

      {/* Data */}
      <Card>
        <CardHeader>
          <CardTitle>Properties</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            data={tableData}
            columns={columns}
            searchable
            exportable
            onRowClick={(row) => toast.info(`Viewing: ${row.name}`)}
          />
        </CardContent>
      </Card>
    </div>
  )
}
```

---

**For complete documentation, see:** `COMPONENT_LIBRARY_GUIDE.md`

















