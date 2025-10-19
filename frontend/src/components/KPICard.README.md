# KPICard Component - Documentation

**Reusable KPI (Key Performance Indicator) Card component for displaying metrics with animations, trends, and beautiful styling.**

---

## 🎯 Features

✅ **Animated Numbers** - Smooth count-up animation from 0 to value  
✅ **Trend Indicators** - Show positive/negative trends with arrows and colors  
✅ **Number Formatting** - Auto-format currency ($1.2M), percentages (94.6%), counts  
✅ **Color Themes** - 6 gradient color options  
✅ **Hover Effects** - Smooth shadow elevation on hover  
✅ **Icons** - Optional icon display  
✅ **Responsive** - Works on all screen sizes  
✅ **Loading State** - Built-in skeleton loader  
✅ **Clickable** - Optional onClick handler  

---

## 🚀 Quick Start

### Basic Usage

```jsx
import KPICard from '@/components/KPICard';

function Dashboard() {
  return (
    <KPICard
      title="Total Revenue"
      value={47800000}
      unit="$"
      trend={8.2}
      trendUp={true}
      color="blue"
      subtitle="vs last month"
    />
  );
}
```

**Result:** A blue card showing "$47.8M" with a green upward trend of "+8.2%"

---

## 📖 API Reference

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | **Required** | Card title/label |
| `value` | `number \| string` | **Required** | Metric value |
| `unit` | `string` | `''` | Unit suffix: "$", "%", etc. |
| `trend` | `number \| null` | `null` | Percentage change (positive or negative) |
| `trendUp` | `boolean \| null` | `null` | Override trend direction (green=true, red=false) |
| `icon` | `React.Component` | `null` | Icon component to display |
| `color` | `string` | `'blue'` | Color theme: 'blue', 'green', 'purple', 'orange', 'red', 'indigo' |
| `subtitle` | `string` | `null` | Optional subtitle text |
| `loading` | `boolean` | `false` | Show loading skeleton |
| `onClick` | `Function` | `null` | Click handler (makes card clickable) |
| `className` | `string` | `''` | Additional CSS classes |

---

## 🎨 Examples

### 1. Currency (Large Numbers)

```jsx
<KPICard
  title="Total Portfolio Value"
  value={47800000}  // Displays as "$47.8M"
  unit="$"
  trend={8.2}
  color="blue"
/>
```

### 2. Percentage

```jsx
<KPICard
  title="Occupancy Rate"
  value={94.6}  // Displays as "94.6%"
  unit="%"
  trend={2.4}
  color="green"
/>
```

### 3. Count/Number

```jsx
<KPICard
  title="Total Properties"
  value={184}  // Displays as "184"
  trend={12}
  color="purple"
/>
```

### 4. With Icon

```jsx
import { DollarIcon } from '@heroicons/react/outline';

<KPICard
  title="Monthly Revenue"
  value={3750000}
  unit="$"
  trend={5.7}
  icon={DollarIcon}
  color="green"
/>
```

### 5. Negative Trend (Good)

```jsx
<KPICard
  title="Vacancy Rate"
  value={5.4}
  unit="%"
  trend={-2.1}
  trendUp={true}  // Green arrow even though trend is negative
  color="green"
  subtitle="improvement"
/>
```

### 6. No Trend

```jsx
<KPICard
  title="Total Assets"
  value={89500000}
  unit="$"
  color="blue"
  subtitle="as of today"
/>
```

### 7. Loading State

```jsx
<KPICard
  title="Total Revenue"
  value={0}
  loading={true}
  color="blue"
/>
```

### 8. Clickable Card

```jsx
<KPICard
  title="View Details"
  value={184}
  trend={12}
  color="blue"
  onClick={() => navigate('/properties')}
  subtitle="Click to view"
/>
```

---

## 🎨 Color Options

### Available Colors

| Color | Best For | Gradient |
|-------|----------|----------|
| `blue` | General metrics, revenue | Blue gradient |
| `green` | Positive metrics, growth | Green gradient |
| `purple` | Analytics, percentages | Purple gradient |
| `orange` | Warnings, attention | Orange gradient |
| `red` | Critical, errors | Red gradient |
| `indigo` | Special metrics | Indigo gradient |

### Example

```jsx
<KPICardGrid columns={3}>
  <KPICard title="Revenue" value={47800000} unit="$" color="blue" />
  <KPICard title="Growth" value={15.3} unit="%" color="green" />
  <KPICard title="Risk Score" value={23} color="orange" />
</KPICardGrid>
```

---

## 📊 Number Formatting

The component automatically formats numbers based on magnitude:

### Currency (unit="$")

| Input | Output |
|-------|--------|
| `125000000` | `$125M` |
| `47800000` | `$47.8M` |
| `3750000` | `$3.8M` |
| `125000` | `$125K` |
| `2850` | `$2,850` |

### Percentage (unit="%")

| Input | Output |
|-------|--------|
| `94.6` | `94.6%` |
| `7.2` | `7.2%` |
| `0.3` | `0.3%` |

### Count (no unit)

| Input | Output |
|-------|--------|
| `2500000` | `2.5M` |
| `184000` | `184K` |
| `1247` | `1,247` |
| `42` | `42` |

---

## 🎭 Trend Display

Trends are displayed with:
- **Arrow icon** (up/down)
- **Percentage value**
- **Color**: Green for positive, Red for negative

### Auto-Detection

By default, the component auto-detects positive/negative:
- `trend={8.2}` → Green upward arrow
- `trend={-3.2}` → Red downward arrow

### Manual Override

Use `trendUp` to override (useful when negative is good):

```jsx
// Vacancy decreased by 2.1% (good!)
<KPICard
  title="Vacancy Rate"
  value={5.4}
  unit="%"
  trend={-2.1}
  trendUp={true}  // Force green arrow
  color="green"
/>
```

---

## 🎬 Animations

### Number Count-Up

Numbers animate from 0 to the target value when the component mounts:

```jsx
<KPICard
  title="Revenue"
  value={47800000}  // Counts up from $0 to $47.8M
  unit="$"
/>
```

### Hover Effect

Cards smoothly scale and elevate on hover:
- Scale: 1.01x (or 1.02x if clickable)
- Shadow: Elevated box shadow

### Entrance Animation

Cards fade in and slide up when they first appear.

---

## 🎯 Grid Layout

Use `KPICardGrid` for responsive layouts:

```jsx
import { KPICardGrid } from '@/components/KPICard';

<KPICardGrid columns={4}>
  <KPICard title="Metric 1" value={100} />
  <KPICard title="Metric 2" value={200} />
  <KPICard title="Metric 3" value={300} />
  <KPICard title="Metric 4" value={400} />
</KPICardGrid>
```

### Grid Columns

| Columns | Behavior |
|---------|----------|
| `1` | 1 column on all screens |
| `2` | 1 col mobile, 2 cols desktop |
| `3` | 1 col mobile, 2 cols tablet, 3 cols desktop |
| `4` | 1 col mobile, 2 cols tablet, 4 cols desktop (default) |
| `5` | 1→2→3→5 cols responsive |
| `6` | 1→2→3→6 cols responsive |

---

## 🔄 Loading State

### Individual Card

```jsx
<KPICard
  title="Total Revenue"
  value={0}
  loading={true}
  color="blue"
/>
```

### Skeleton Component

```jsx
import { KPICardSkeleton } from '@/components/KPICard';

<KPICardGrid columns={4}>
  <KPICardSkeleton color="blue" />
  <KPICardSkeleton color="green" />
  <KPICardSkeleton color="purple" />
  <KPICardSkeleton color="orange" />
</KPICardGrid>
```

---

## 🎯 Real-World Example

### Dashboard with Multiple KPIs

```jsx
import KPICard, { KPICardGrid } from '@/components/KPICard';
import { useQuery } from '@/hooks/useQuery';
import api from '@/api';

function Dashboard() {
  const { data, isLoading } = useQuery(
    'kpis',
    () => api.get('/api/kpis/financial')
  );

  if (isLoading) {
    return (
      <KPICardGrid columns={4}>
        <KPICardSkeleton color="blue" />
        <KPICardSkeleton color="green" />
        <KPICardSkeleton color="purple" />
        <KPICardSkeleton color="orange" />
      </KPICardGrid>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>

      <KPICardGrid columns={4}>
        <KPICard
          title="Total Portfolio Value"
          value={data.total_portfolio_value.value}
          unit="$"
          trend={data.total_portfolio_value.trend}
          color="blue"
          subtitle="vs last quarter"
          onClick={() => navigate('/properties')}
        />

        <KPICard
          title="Total Properties"
          value={data.total_properties}
          trend={data.properties_trend}
          color="green"
          subtitle={`${data.new_properties} new this month`}
        />

        <KPICard
          title="Average Occupancy"
          value={data.average_occupancy}
          unit="%"
          trend={data.occupancy_trend}
          color="purple"
          subtitle="across all properties"
        />

        <KPICard
          title="Monthly NOI"
          value={data.monthly_noi}
          unit="$"
          trend={data.noi_trend}
          color="indigo"
          subtitle="net operating income"
        />
      </KPICardGrid>
    </div>
  );
}
```

---

## 🎨 Customization

### Custom Styling

Add custom classes via `className` prop:

```jsx
<KPICard
  title="Custom Card"
  value={1234}
  className="shadow-2xl border-4 border-blue-300"
/>
```

### Custom Icons

Use any icon library (Heroicons, Font Awesome, etc.):

```jsx
import { ChartBarIcon } from '@heroicons/react/outline';
// or
import { FaChartLine } from 'react-icons/fa';

<KPICard
  title="Revenue"
  value={47800000}
  unit="$"
  icon={ChartBarIcon} // or FaChartLine
  color="blue"
/>
```

---

## 💡 Best Practices

### 1. Choose Appropriate Colors

```jsx
✅ Green for positive metrics (revenue, growth)
✅ Blue for neutral/general metrics
✅ Purple for analytics/percentages
✅ Orange for warnings/attention needed
✅ Red for critical/error states
```

### 2. Use Meaningful Subtitles

```jsx
✅ Good: subtitle="vs last quarter"
✅ Good: subtitle="12 new this month"
❌ Bad: subtitle="data"
❌ Bad: subtitle="info"
```

### 3. Format Numbers Consistently

```jsx
✅ Use unit="$" for currency
✅ Use unit="%" for percentages
✅ Let the component handle formatting
❌ Don't pre-format: value="$47.8M"
```

### 4. Handle Loading States

```jsx
✅ Show skeleton loaders while loading
✅ Use KPICardSkeleton for consistent UX
❌ Don't show empty/broken cards
```

### 5. Group Related Metrics

```jsx
<KPICardGrid columns={4}>
  {/* Financial metrics together */}
  <KPICard title="Revenue" ... />
  <KPICard title="Expenses" ... />
  <KPICard title="Profit" ... />
  <KPICard title="ROI" ... />
</KPICardGrid>

<KPICardGrid columns={3}>
  {/* Operational metrics together */}
  <KPICard title="Properties" ... />
  <KPICard title="Tenants" ... />
  <KPICard title="Occupancy" ... />
</KPICardGrid>
```

---

## 🐛 Troubleshooting

### Numbers Not Animating

**Issue:** Numbers appear instantly without animation

**Solution:** Ensure value is a number, not a string:
```jsx
❌ value="47800000"
✅ value={47800000}
```

### Trend Color Wrong

**Issue:** Negative trend shows green (or vice versa)

**Solution:** Use `trendUp` prop to override:
```jsx
<KPICard
  title="Costs"
  value={1000000}
  unit="$"
  trend={-5.2}
  trendUp={true}  // Cost reduction is good!
  color="green"
/>
```

### Card Not Clickable

**Issue:** Card doesn't respond to clicks

**Solution:** Add `onClick` prop:
```jsx
<KPICard
  title="Revenue"
  value={47800000}
  unit="$"
  onClick={() => console.log('Clicked')}
/>
```

---

## 📚 See Also

- [KPICard.examples.jsx](./KPICard.examples.jsx) - 8 complete examples
- [useQuery Hook](../hooks/README.md) - Fetch KPI data
- [Framer Motion Docs](https://www.framer.com/motion/) - Animation library

---

## 🎉 Summary

The KPICard component provides a beautiful, flexible way to display metrics in your dashboard:

✅ **Easy to Use** - Simple props, works out of the box  
✅ **Beautiful** - Gradient backgrounds, smooth animations  
✅ **Flexible** - Many customization options  
✅ **Responsive** - Works on all devices  
✅ **Performant** - Optimized animations  

**Perfect for dashboards, reports, and analytics views!** 🚀

