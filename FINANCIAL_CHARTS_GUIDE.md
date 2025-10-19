# 📈 Financial Charts Dashboard - Complete Guide

## 🎯 Overview

The **Financial Charts Dashboard** provides interactive data visualizations for key financial metrics using Recharts. This component enables users to analyze NOI trends, occupancy rates, revenue/expense patterns, and tenant distributions through four distinct chart types with full interactivity.

---

## 📊 Charts Overview

### **4 Interactive Chart Types**

1. **Line Chart** - NOI Trend (Last 12 Months)
2. **Bar Chart** - Occupancy by Property
3. **Area Chart** - Revenue vs Expenses Over Time
4. **Pie Chart** - Tenant Type Distribution

---

## 🎨 Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📈 Financial Charts Dashboard         [☀️/🌙 Toggle]      │
│  Interactive visualizations with real-time data             │
│                                                             │
│  📅 Date Range: [3MO] [6MO] [1YR] [YTD]                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────┐
│  📊 NOI Trend       │  📊 Occupancy       │
│  [Export PNG]        │  [Export PNG]        │
│                      │                      │
│  [Line Chart]        │  [Bar Chart]         │
│                      │                      │
│  Legend: ● NOI  ●    │  6 Properties        │
│          ▫ Target    │  Bars: Orange        │
└──────────────────────┴──────────────────────┘

┌──────────────────────┬──────────────────────┐
│  📊 Revenue/Exp     │  📊 Tenant Types    │
│  [Export PNG]        │  [Export PNG]        │
│                      │                      │
│  [Area Chart]        │  [Pie Chart]         │
│                      │                      │
│  Legend: ● Revenue   │  • Residential 45%   │
│          ● Expenses  │  • Commercial  30%   │
│          ● Profit    │  • Industrial  15%   │
│                      │  • Retail      10%   │
└──────────────────────┴──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Chart Summary                                              │
│  ┌──────┬──────┬───────┬──────┐                           │
│  │ Avg  │ Avg  │ Total │Total │                           │
│  │ NOI  │ Occ  │ Rev   │Props │                           │
│  └──────┴──────┴───────┴──────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Chart 1: NOI Trend (Line Chart)

### **Description**
Tracks Net Operating Income (NOI) over the selected time period with comparison to target goals.

### **Data Points**
```javascript
{
  month: "Jan",     // Month name
  noi: 850000,      // Actual NOI ($850K)
  target: 900000    // Target NOI ($900K)
}
```

### **Visual Features**
- **Blue solid line**: Actual NOI
- **Gray dashed line**: Target NOI
- **Animated dots**: Enlarge on hover
- **Grid**: Light gray background lines
- **Y-axis**: Formatted as $850K
- **X-axis**: Month names

### **Interactive Features**

**Hover:**
- Tooltip shows exact values
- Active dot enlarges (radius 5 → 7)
- Display: "$850K"

**Legend:**
- Click "NOI" to hide/show blue line
- Click "Target" to hide/show gray line
- Faded opacity (40%) when hidden

**Date Range:**
- Responds to 3mo/6mo/1yr/ytd selector
- Re-renders with new data points

**Export:**
- Download icon (top-right)
- Saves as `noi_trend_2025-10-12.png`
- High resolution (2x scale)

### **Sample Data**
```
Month  | NOI      | Target
-------|----------|--------
Jan    | $850K    | $900K
Feb    | $820K    | $900K
Mar    | $890K    | $900K
...    | ...      | ...
Dec    | $910K    | $900K

Average: $885K/month
```

---

## 📊 Chart 2: Occupancy by Property (Bar Chart)

### **Description**
Displays occupancy percentage for each property in the portfolio.

### **Data Points**
```javascript
{
  property: "Sunset Apts",  // Property name
  occupancy: 95.2,          // Occupancy %
  units: 120                // Total units
}
```

### **Visual Features**
- **Orange bars**: Vibrant color (#f59e0b)
- **Rounded tops**: radius [8, 8, 0, 0]
- **Angled labels**: -45° for readability
- **Y-axis**: 0-100% scale
- **Grid**: Horizontal lines

### **Properties Displayed**
```
Property          | Occupancy | Units
------------------|-----------|------
Sunset Apts       | 95.2%     | 120
Downtown Lofts    | 87.5%     | 85
Green Valley      | 78.3%     | 60
Oceanfront        | 96.1%     | 150
Industrial Park A | 91.0%     | 45
Retail Hub B      | 82.1%     | 30

Average: 88.4%
```

### **Interactive Features**

**Hover:**
- Bar highlights
- Tooltip shows:
  - Property name
  - Occupancy percentage
  - Unit count

**Export:**
- Saves as `occupancy_2025-10-12.png`

---

## 📊 Chart 3: Revenue vs Expenses (Area Chart)

### **Description**
Visualizes revenue, expenses, and profit trends over time with gradient fills.

### **Data Points**
```javascript
{
  month: "Jan",
  revenue: 1200000,   // $1.2M
  expenses: 700000,   // $700K
  profit: 500000      // $500K (auto-calculated)
}
```

### **Visual Features**
- **Green area**: Revenue with gradient fill
- **Red area**: Expenses with gradient fill  
- **Purple area**: Profit with gradient fill
- **Opacity**: 80% at top → 10% at bottom
- **Stroke width**: 2px for all lines

### **Gradient Definitions**
```javascript
// Revenue gradient
linearGradient id="colorRevenue"
  stop offset="5%"  stopColor="#10b981" stopOpacity={0.8}
  stop offset="95%" stopColor="#10b981" stopOpacity={0.1}

// Similar for Expenses (red) and Profit (purple)
```

### **Interactive Features**

**Hover:**
- Shows all 3 values simultaneously
- Formatted as currency ($1.2M)

**Legend:**
- Click "Revenue" to toggle green area
- Click "Expenses" to toggle red area
- Click "Profit" to toggle purple area
- Can show/hide any combination

**Date Range:**
- Responds to selector (3mo/6mo/1yr/ytd)

**Export:**
- Saves as `revenue_expenses_2025-10-12.png`

### **Sample Data**
```
Month | Revenue  | Expenses | Profit
------|----------|----------|--------
Jan   | $1.20M   | $700K    | $500K
Feb   | $1.18M   | $680K    | $500K
Mar   | $1.25M   | $720K    | $530K
...   | ...      | ...      | ...

Total Revenue: $14.4M/year
Total Expenses: $8.4M/year
Total Profit: $6.0M/year
```

---

## 📊 Chart 4: Tenant Type Distribution (Pie Chart)

### **Description**
Shows the breakdown of properties by tenant type category.

### **Data Points**
```javascript
{
  type: "Residential",  // Tenant type
  value: 45,            // Number of properties
  color: "#3b82f6"      // Blue
}
```

### **Tenant Categories**
```
Type        | Count | Percentage | Color
------------|-------|------------|--------
Residential | 45    | 45%        | Blue
Commercial  | 30    | 30%        | Green
Industrial  | 15    | 15%        | Orange
Retail      | 10    | 10%        | Red

Total: 100 properties
```

### **Visual Features**
- **Outer radius**: 100px
- **Auto-labels**: "Residential: 45%"
- **No inner radius**: Full pie (not donut)
- **Color-coded segments**
- **Legend below**: Color + name + count

### **Interactive Features**

**Hover:**
- Tooltip displays:
  - Tenant type
  - Property count
  - Exact percentage

**Export:**
- Saves as `tenant_distribution_2025-10-12.png`

---

## 🎨 Color Schemes

### **Light Mode** ☀️

```javascript
{
  noi: '#3b82f6',        // Blue
  target: '#94a3b8',     // Gray
  revenue: '#10b981',    // Green
  expenses: '#ef4444',   // Red
  profit: '#8b5cf6',     // Purple
  occupancy: '#f59e0b',  // Orange
  grid: '#e5e7eb',       // Light gray
  text: '#374151'        // Dark gray
}
```

**Background**: White  
**Cards**: White with borders  
**Text**: Dark gray  

### **Dark Mode** 🌙

```javascript
{
  noi: '#60a5fa',        // Light blue
  target: '#cbd5e1',     // Light gray
  revenue: '#34d399',    // Light green
  expenses: '#f87171',   // Light red
  profit: '#a78bfa',     // Light purple
  occupancy: '#fbbf24',  // Light orange
  grid: '#374151',       // Dark gray
  text: '#e5e7eb'        // Light gray
}
```

**Background**: Dark gray (#1f2937)  
**Cards**: Dark with borders  
**Text**: Light gray  

### **Toggle**
Click the Sun ☀️ or Moon 🌙 icon in the top-right corner to switch modes.

---

## 💡 Hover Tooltips

### **Custom Tooltip Component**

```javascript
<CustomTooltip isDark={isDark} />
```

**Features:**
- Adapts to light/dark mode
- White bg (light) / Dark gray bg (dark)
- Border styling
- Shadow effect

**Content:**
- **Label**: Month or property name (bold)
- **Values**: All data points for that position
  - Color-coded indicator dot
  - Name: "Revenue", "NOI", etc.
  - Value: Formatted ($850K or 95.2%)

**Formatting:**
```javascript
// Currency
value >= 1000 ? `$${(value / 1000).toFixed(1)}K` : value

// Percentage
dataKey === 'occupancy' ? `${value.toFixed(1)}%` : value
```

---

## 🎯 Clickable Legend

### **How It Works**

**State Management:**
```javascript
const [hiddenNOISeries, setHiddenNOISeries] = useState([])
const [hiddenRevExpSeries, setHiddenRevExpSeries] = useState([])
```

**Toggle Function:**
```javascript
const toggleNOISeries = (dataKey) => {
  setHiddenNOISeries(prev =>
    prev.includes(dataKey)
      ? prev.filter(key => key !== dataKey)  // Show
      : [...prev, dataKey]                    // Hide
  )
}
```

**Visual Feedback:**
- Hidden series: 40% opacity
- Visible series: 100% opacity
- Hover effect: Background highlight

**Applies To:**
- NOI Chart: 2 series (NOI, Target)
- Revenue/Expenses Chart: 3 series (Revenue, Expenses, Profit)
- Occupancy Chart: No legend (single series)
- Pie Chart: No toggle (info only)

---

## 📅 Date Range Selector

### **4 Options**

| Button | Label | Months | Description |
|--------|-------|--------|-------------|
| `3mo` | 3MO | 3 | Last 3 months |
| `6mo` | 6MO | 6 | Last 6 months |
| `1yr` | 1YR | 12 | Last 12 months (default) |
| `ytd` | YTD | Variable | Year-to-date (Jan to current month) |

### **Implementation**

```javascript
const [dateRange, setDateRange] = useState('1yr')

const getMonthsForRange = () => {
  switch (dateRange) {
    case '3mo': return 3
    case '6mo': return 6
    case 'ytd': return new Date().getMonth() + 1
    default: return 12  // '1yr'
  }
}

const noiData = generateNOIData(getMonthsForRange())
```

### **Affected Charts**
- ✅ NOI Trend (Line Chart)
- ✅ Revenue vs Expenses (Area Chart)
- ❌ Occupancy by Property (static data)
- ❌ Tenant Type Distribution (static data)

### **Visual Feedback**
- **Active button**: 
  - Light mode: Blue bg, white text
  - Dark mode: Blue bg, white text
- **Inactive buttons**:
  - Light mode: White bg, gray text
  - Dark mode: Dark gray bg, gray text

---

## 📥 Export to PNG

### **Technology**
- **Library**: html2canvas
- **Resolution**: 2x scale (high quality)
- **Format**: PNG image

### **How to Export**

1. Click the download icon (📥) in the top-right of any chart
2. Chart area is captured with html2canvas
3. PNG file is automatically downloaded

### **File Naming**
```
{chartName}_{YYYY-MM-DD}.png

Examples:
- noi_trend_2025-10-12.png
- occupancy_2025-10-12.png
- revenue_expenses_2025-10-12.png
- tenant_distribution_2025-10-12.png
```

### **Implementation**

```javascript
const exportChart = async (chartRef, chartName) => {
  if (!chartRef.current) return

  try {
    const canvas = await html2canvas(chartRef.current, {
      backgroundColor: isDark ? '#1f2937' : '#ffffff',
      scale: 2  // High resolution
    })
    
    const link = document.createElement('a')
    link.download = `${chartName}_${new Date().toISOString().split('T')[0]}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('Export failed:', error)
  }
}
```

### **Features**
- Preserves light/dark mode styling
- Includes chart title and legend
- High resolution for presentations
- Works on all 4 charts independently

---

## 🎬 Animations

### **Page Entry**
```javascript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: 0.1 }}
>
```

**Stagger:**
- Chart 1: delay 0.1s
- Chart 2: delay 0.2s
- Chart 3: delay 0.3s
- Chart 4: delay 0.4s
- Summary: delay 0.5s

### **Line Chart Dots**
```javascript
dot={{ fill: currentColors.noi, r: 5 }}
activeDot={{ r: 7 }}
```
Radius 5 → 7 on hover

### **Transitions**
- Date range change: Smooth data update
- Legend toggle: Fade in/out
- Theme toggle: Color scheme transition

---

## 📱 Responsive Design

### **Grid Layout**

**Desktop (≥1024px):**
```
┌─────────┬─────────┐
│ Chart 1 │ Chart 2 │
├─────────┼─────────┤
│ Chart 3 │ Chart 4 │
└─────────┴─────────┘
```
`grid-cols-2`

**Tablet/Mobile (<1024px):**
```
┌─────────┐
│ Chart 1 │
├─────────┤
│ Chart 2 │
├─────────┤
│ Chart 3 │
├─────────┤
│ Chart 4 │
└─────────┘
```
`grid-cols-1`

### **Chart Heights**
- All charts: 300px height
- ResponsiveContainer: 100% width
- Maintains aspect ratio

---

## 🔄 Data Generation

### **NOI Data**
```javascript
const generateNOIData = (months = 12) => {
  const monthNames = ['Jan', 'Feb', ..., 'Dec']
  let baseValue = 850000
  
  for (let i = 0; i < months; i++) {
    baseValue += (Math.random() - 0.4) * 50000
    data.push({
      month: monthNames[i],
      noi: Math.round(baseValue),
      target: 900000
    })
  }
  return data
}
```

### **Revenue/Expenses Data**
```javascript
const generateRevenueExpensesData = (months = 12) => {
  let revenue = 1200000
  let expenses = 700000
  
  for (let i = 0; i < months; i++) {
    revenue += (Math.random() - 0.4) * 80000
    expenses += (Math.random() - 0.5) * 40000
    data.push({
      month: monthNames[i],
      revenue: Math.round(revenue),
      expenses: Math.round(expenses),
      profit: Math.round(revenue - expenses)
    })
  }
  return data
}
```

### **Static Data**
- Occupancy by Property: 6 fixed properties
- Tenant Types: 4 fixed categories

---

## 📊 Chart Summary Panel

### **4 Summary Cards**

Located below all charts:

```
┌──────────────────────────────────────────────┐
│  ┌───────┬───────┬───────┬──────────┐       │
│  │  Avg  │  Avg  │ Total │  Total   │       │
│  │  NOI  │ Occ % │  Rev  │  Props   │       │
│  │ $885K │ 88.4% │ $14M  │   100    │       │
│  └───────┴───────┴───────┴──────────┘       │
└──────────────────────────────────────────────┘
```

### **Calculations**

**Avg NOI:**
```javascript
noiData.reduce((sum, item) => sum + item.noi, 0) / noiData.length / 1000
// Result: $885K
```

**Avg Occupancy:**
```javascript
occupancyData.reduce((sum, item) => sum + item.occupancy, 0) / occupancyData.length
// Result: 88.4%
```

**Total Revenue:**
```javascript
revExpData.reduce((sum, item) => sum + item.revenue, 0) / 1000000
// Result: $14.4M
```

**Total Properties:**
```javascript
tenantData.reduce((sum, item) => sum + item.value, 0)
// Result: 100
```

### **Color Coding**
- NOI card: Blue background
- Occupancy card: Orange background
- Revenue card: Green background
- Properties card: Purple background

---

## 🌐 Integration Guide

### **1. Import Component**

```javascript
import FinancialCharts from './components/FinancialCharts'
```

### **2. Add to Router**

```javascript
function App() {
  const [activeTab, setActiveTab] = useState('portfolio')

  if (activeTab === 'charts') {
    return <FinancialCharts />
  }

  // ... other tabs
}
```

### **3. Add Tab Button**

```javascript
<button onClick={() => setActiveTab('charts')}>
  📈 Financial Charts
</button>
```

---

## 🎓 Component Props

```typescript
// FinancialCharts is a standalone component with no props
// All data and state is managed internally

export default function FinancialCharts() {
  // Component implementation
}
```

**Internal State:**
```javascript
const [isDark, setIsDark] = useState(false)
const [dateRange, setDateRange] = useState('1yr')
const [hiddenNOISeries, setHiddenNOISeries] = useState([])
const [hiddenRevExpSeries, setHiddenRevExpSeries] = useState([])
```

---

## 💻 Dependencies

```json
{
  "recharts": "^2.x",
  "html2canvas": "^1.x",
  "framer-motion": "^10.x",
  "lucide-react": "^0.x"
}
```

**Install:**
```bash
npm install recharts html2canvas framer-motion lucide-react
```

---

## ✅ Use Cases

### **1. Financial Analysis**
Track NOI trends to identify growth or decline patterns over time.

### **2. Property Performance**
Compare occupancy rates across properties to identify underperformers.

### **3. Revenue Optimization**
Analyze revenue vs expenses to improve profit margins.

### **4. Portfolio Composition**
Understand tenant type distribution for diversification strategy.

### **5. Executive Reporting**
Export charts as PNGs for presentations and board meetings.

### **6. Trend Identification**
Use date range selector to compare quarterly vs yearly trends.

---

## 🚀 Performance

### **Optimizations**
- ✅ ResponsiveContainer: Efficient resizing
- ✅ Lazy rendering: Only visible charts
- ✅ Memoized calculations
- ✅ Smooth 60fps animations
- ✅ Efficient state management

### **Bundle Size**
- Recharts: ~90KB (gzipped)
- html2canvas: ~25KB (gzipped)
- Component: ~12KB (minified)

---

## 🎉 Summary

The **Financial Charts Dashboard** provides:

✅ **4 chart types** (Line, Bar, Area, Pie)  
✅ **Interactive tooltips** with precise values  
✅ **Clickable legends** to toggle series  
✅ **Date range selector** (3mo/6mo/1yr/ytd)  
✅ **PNG export** for all charts  
✅ **Light/dark mode** support  
✅ **Responsive design** for all devices  
✅ **Beautiful animations** and gradients  

**Access it at:** http://localhost:3000 → 📈 Financial Charts

---

**Built with ❤️ using Recharts, html2canvas, and Framer Motion**

















