# 📊 REIMS KPI Metric Cards - Complete Guide

**Animated, interactive KPI cards with sparklines and detailed tooltips**

---

## 📋 Overview

Premium KPI metric cards featuring:

✅ **Large animated numbers** with count-up effect  
✅ **Color-coded gradients** for each metric type  
✅ **Trend indicators** (up/down with percentage)  
✅ **Sparkline charts** showing 30-day history  
✅ **Hover tooltips** with detailed breakdowns  
✅ **Glow effects** and smooth animations  
✅ **Recharts integration** for data visualization  
✅ **Dark mode support**  

---

## 🚀 Quick Start

### Installation

```bash
npm install recharts framer-motion lucide-react
```

### Basic Usage

```jsx
import KPIMetricCard, { generateSparklineData } from '@/components/KPIMetricCard'
import { DollarSign } from 'lucide-react'

function Dashboard() {
  return (
    <KPIMetricCard
      title="Portfolio Value"
      value={47800000}
      formattedValue="$47.8M"
      trend="up"
      trendValue="+12.5%"
      sparklineData={generateSparklineData(47800000, 0.08, 30)}
      icon={DollarSign}
      type="portfolio"
      subtitle="Total Assets"
      details={{
        'Properties': '184',
        'Avg Value': '$260K',
        'YoY Growth': '+15.2%'
      }}
    />
  )
}
```

---

## 📖 Component API

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | required | Metric title |
| `value` | `number` | required | Numeric value for animation |
| `formattedValue` | `string` | required | Display format (e.g., "$47.8M") |
| `trend` | `'up'/'down'/'neutral'` | `'up'` | Trend direction |
| `trendValue` | `string` | `'+0%'` | Trend percentage/value |
| `sparklineData` | `array` | `[]` | 30-day data points |
| `icon` | `Component` | `null` | Lucide icon component |
| `type` | `string` | `'default'` | Metric type for styling |
| `subtitle` | `string` | `null` | Subtitle text |
| `details` | `object` | `{}` | Hover tooltip details |
| `className` | `string` | `''` | Additional CSS classes |

### Metric Types

Each type has unique gradient and colors:

| Type | Gradient Colors | Use For |
|------|----------------|---------|
| `'portfolio'` | Blue → Indigo → Purple | Portfolio/asset values |
| `'properties'` | Teal → Cyan → Blue | Property counts |
| `'income'` | Emerald → Lime → Emerald | Revenue/income metrics |
| `'occupancy'` | Purple → Indigo → Blue | Occupancy/usage rates |
| `'default'` | Gray → Slate → Gray | General metrics |

---

## 🎨 REIMS Specific Metrics

### 1. Portfolio Value ($47.8M)

```jsx
<KPIMetricCard
  title="Portfolio Value"
  value={47800000}
  formattedValue="$47.8M"
  trend="up"
  trendValue="+12.5%"
  sparklineData={generateSparklineData(47800000, 0.08, 30)}
  icon={Building2}
  type="portfolio"
  subtitle="Total Assets"
  details={{
    'Properties': '184',
    'Avg Value': '$260K',
    'YoY Growth': '+15.2%',
    'Market Cap': '$52M'
  }}
/>
```

**Features:**
- Blue → Purple gradient
- Currency formatting ($47.8M)
- Count-up animation
- 30-day value trend

### 2. Total Properties (184)

```jsx
<KPIMetricCard
  title="Total Properties"
  value={184}
  formattedValue="184"
  trend="up"
  trendValue="+8 units"
  sparklineData={generateSparklineData(184, 0.05, 30)}
  icon={Home}
  type="properties"
  subtitle="Active Units"
  details={{
    'Residential': '142',
    'Commercial': '42',
    'Acquired This Year': '12',
    'Under Construction': '3'
  }}
/>
```

**Features:**
- Teal → Cyan gradient
- Integer formatting (184)
- Property breakdown
- Acquisition tracking

### 3. Monthly Income ($1.2M)

```jsx
<KPIMetricCard
  title="Monthly Income"
  value={1200000}
  formattedValue="$1.2M"
  trend="up"
  trendValue="+8.3%"
  sparklineData={generateSparklineData(1200000, 0.06, 30)}
  icon={DollarSign}
  type="income"
  subtitle="Rental Revenue"
  details={{
    'Gross Revenue': '$1.4M',
    'Net Revenue': '$1.2M',
    'Expenses': '$200K',
    'Profit Margin': '85.7%'
  }}
/>
```

**Features:**
- Emerald → Lime gradient
- Revenue breakdown
- Profit margin
- Expense tracking

### 4. Occupancy Rate (94.6%)

```jsx
<KPIMetricCard
  title="Occupancy Rate"
  value={94.6}
  formattedValue="94.6%"
  trend="down"
  trendValue="-2.1%"
  sparklineData={generateSparklineData(94.6, 0.03, 30)}
  icon={Users}
  type="occupancy"
  subtitle="Current Occupancy"
  details={{
    'Occupied': '174 units',
    'Vacant': '10 units',
    'Target': '96%',
    'Historical Avg': '93.2%'
  }}
/>
```

**Features:**
- Purple → Indigo gradient
- Percentage formatting (94.6%)
- Occupied/vacant breakdown
- Target comparison

---

## ✨ Features Breakdown

### 1. Animated Numbers

Count-up animation on viewport entry:

```javascript
// Animates from 0 to target value over 2 seconds
useEffect(() => {
  if (!isInView) return
  
  const duration = 2000
  const steps = 60
  const increment = numericValue / steps
  
  const timer = setInterval(() => {
    // Increment display value
  }, duration / steps)
}, [value, isInView])
```

**Features:**
- Smooth count-up
- Viewport detection
- Format preservation
- 2-second duration

### 2. Trend Indicators

Visual trend with percentage:

```jsx
<span className="inline-flex items-center gap-1">
  <TrendingUp className="w-3.5 h-3.5" />
  <span>+12.5%</span>
</span>
```

**Trend Types:**
- 🟢 **Up:** Green, TrendingUp icon
- 🔴 **Down:** Red, TrendingDown icon
- ⚪ **Neutral:** Gray, Minus icon

### 3. Sparkline Charts

30-day historical trend using Recharts:

```jsx
<ResponsiveContainer width="100%" height="100%">
  <LineChart data={sparklineData}>
    <Line
      type="monotone"
      dataKey="value"
      stroke={config.sparklineColor}
      strokeWidth={2}
      dot={false}
      animationDuration={1500}
    />
  </LineChart>
</ResponsiveContainer>
```

**Features:**
- Responsive sizing
- Smooth animation (1.5s)
- No dots (clean look)
- Color-coded by type

### 4. Hover Tooltip

Detailed breakdown on hover:

```jsx
{isHovered && (
  <motion.div className="tooltip">
    {Object.entries(details).map(([key, val]) => (
      <div key={key}>
        <span>{key}</span>
        <span>{val}</span>
      </div>
    ))}
  </motion.div>
)}
```

**Features:**
- Fade + slide animation
- Glassmorphism backdrop
- Key-value pairs
- Auto-positioned

### 5. Background Gradients

Each metric type has unique colors:

```javascript
const typeConfig = {
  portfolio: {
    gradient: 'from-brand-blue-500 via-accent-indigo-500 to-accent-purple-500',
    accentColor: 'rgb(37, 99, 235)',
    sparklineColor: '#2563EB',
    glowColor: 'rgba(37, 99, 235, 0.4)',
  },
  // ... other types
}
```

### 6. Glow Effects

Animated glow on hover:

```jsx
<motion.div
  animate={{
    scale: isHovered ? [1, 1.2, 1] : 1,
    opacity: isHovered ? [0.3, 0.5, 0.3] : 0.2,
  }}
  transition={{ duration: 2, repeat: Infinity }}
  style={{ backgroundColor: config.glowColor }}
/>
```

---

## 📊 Generating Sparkline Data

Helper function to create realistic 30-day trends:

```javascript
import { generateSparklineData } from '@/components/KPIMetricCard'

// Generate data with 8% variance over 30 days
const data = generateSparklineData(
  47800000,  // Base value
  0.08,      // 8% variance
  30         // 30 days
)

// Returns array: [{ day: 1, value: 47234567 }, ...]
```

**Parameters:**
- `baseValue` - Starting value
- `variance` - Max deviation (0.1 = 10%)
- `days` - Number of data points (default: 30)

**Algorithm:**
- Random walk with slight upward bias
- Stays within variance bounds
- Smooth transitions

---

## 🎯 Complete Dashboard Example

```jsx
import KPIMetricCard, { generateSparklineData } from '@/components/KPIMetricCard'
import { Building2, Home, DollarSign, Users } from 'lucide-react'

function REIMSDashboard() {
  const kpis = [
    {
      title: 'Portfolio Value',
      value: 47800000,
      formattedValue: '$47.8M',
      trend: 'up',
      trendValue: '+12.5%',
      sparklineData: generateSparklineData(47800000, 0.08, 30),
      icon: Building2,
      type: 'portfolio',
      subtitle: 'Total Assets',
      details: {
        'Properties': '184',
        'Avg Value': '$260K',
        'YoY Growth': '+15.2%',
        'Market Cap': '$52M',
      }
    },
    {
      title: 'Total Properties',
      value: 184,
      formattedValue: '184',
      trend: 'up',
      trendValue: '+8 units',
      sparklineData: generateSparklineData(184, 0.05, 30),
      icon: Home,
      type: 'properties',
      subtitle: 'Active Units',
      details: {
        'Residential': '142',
        'Commercial': '42',
        'Acquired This Year': '12',
        'Under Construction': '3',
      }
    },
    {
      title: 'Monthly Income',
      value: 1200000,
      formattedValue: '$1.2M',
      trend: 'up',
      trendValue: '+8.3%',
      sparklineData: generateSparklineData(1200000, 0.06, 30),
      icon: DollarSign,
      type: 'income',
      subtitle: 'Rental Revenue',
      details: {
        'Gross Revenue': '$1.4M',
        'Net Revenue': '$1.2M',
        'Expenses': '$200K',
        'Profit Margin': '85.7%',
      }
    },
    {
      title: 'Occupancy Rate',
      value: 94.6,
      formattedValue: '94.6%',
      trend: 'down',
      trendValue: '-2.1%',
      sparklineData: generateSparklineData(94.6, 0.03, 30),
      icon: Users,
      type: 'occupancy',
      subtitle: 'Current Occupancy',
      details: {
        'Occupied': '174 units',
        'Vacant': '10 units',
        'Target': '96%',
        'Historical Avg': '93.2%',
      }
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {kpis.map(kpi => (
        <KPIMetricCard key={kpi.title} {...kpi} />
      ))}
    </div>
  )
}
```

---

## 🎨 Customization

### Custom Colors

```jsx
// Override type configuration
<KPIMetricCard
  // ... props
  className="custom-gradient"
/>

// In CSS
.custom-gradient {
  background: linear-gradient(to bottom right, #your-colors);
}
```

### Custom Animations

```jsx
// Adjust animation duration
// In AnimatedNumber component:
const duration = 3000 // 3 seconds instead of 2
```

### Custom Sparkline

```jsx
// Provide your own data
const customData = [
  { day: 1, value: 1000000 },
  { day: 2, value: 1050000 },
  // ... more data
]

<KPIMetricCard sparklineData={customData} />
```

---

## 📱 Responsive Design

### Grid Layouts

```jsx
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* Cards auto-adjust */}
</div>

// Single column on mobile
// 2 columns on tablet
// 4 columns on desktop
```

### Mobile Optimizations

- Touch-friendly hover states
- Larger tap targets
- Readable font sizes
- Optimized animations

---

## ⚡ Performance

### Optimizations

1. **Lazy Loading**
```jsx
const KPIMetricCard = lazy(() => import('@/components/KPIMetricCard'))
```

2. **Memoization**
```jsx
const memoizedSparklineData = useMemo(
  () => generateSparklineData(value, 0.08, 30),
  [value]
)
```

3. **Viewport Detection**
- Animations only trigger when in view
- Reduces unnecessary calculations
- Improves scroll performance

---

## 🧪 Testing

### Test Scenarios

1. **Animation**
   - Verify count-up works
   - Check timing (2 seconds)
   - Test viewport trigger

2. **Hover States**
   - Tooltip appears
   - Glow effect activates
   - Smooth transitions

3. **Sparklines**
   - Chart renders correctly
   - Data matches input
   - Animation plays

4. **Responsiveness**
   - Test on mobile
   - Check tablet layout
   - Verify desktop view

---

## 📊 Data Integration

### Real API Data

```jsx
import { useQuery } from '@tanstack/react-query'

function KPIDashboard() {
  const { data: kpiData } = useQuery({
    queryKey: ['kpis'],
    queryFn: async () => {
      const response = await fetch('/api/kpis/financial')
      return response.json()
    }
  })

  return (
    <KPIMetricCard
      title="Portfolio Value"
      value={kpiData?.portfolioValue}
      formattedValue={formatCurrency(kpiData?.portfolioValue)}
      // ... other props
    />
  )
}
```

### Live Updates

```jsx
// Update KPIs every 30 seconds
useQuery({
  queryKey: ['kpis'],
  queryFn: fetchKPIs,
  refetchInterval: 30000 // 30 seconds
})
```

---

## 🎉 Summary

### What You Have

✅ **Animated KPI Cards** - Count-up animations  
✅ **4 Metric Types** - Portfolio, Properties, Income, Occupancy  
✅ **Sparkline Charts** - 30-day trends with Recharts  
✅ **Hover Tooltips** - Detailed breakdowns  
✅ **Color Gradients** - Unique for each type  
✅ **Glow Effects** - Interactive animations  
✅ **Dark Mode** - Full support  
✅ **Responsive** - Mobile-optimized  

### Component Stats

- **Lines of Code:** 300+
- **Animations:** 5+ different effects
- **Props:** 11 customizable
- **Metric Types:** 5 (including default)
- **Dependencies:** Recharts, Framer Motion, Lucide

---

**Your REIMS KPI cards are production-ready! 🚀**

Start tracking portfolio performance with beautiful, animated metrics!

















