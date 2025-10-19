# 🎨 REIMS Color Quick Reference

**Quick copy-paste reference for daily development**

---

## 🔵 Primary Actions

```jsx
// Primary Button
<button className="bg-brand-blue-500 hover:bg-brand-blue-600 text-white px-4 py-2 rounded-lg">
  Primary Action
</button>

// Secondary Button
<button className="bg-brand-teal-500 hover:bg-brand-teal-600 text-white px-4 py-2 rounded-lg">
  Secondary Action
</button>

// Outline Button
<button className="border-2 border-brand-blue-500 text-brand-blue-600 hover:bg-brand-blue-50 px-4 py-2 rounded-lg">
  Outline
</button>
```

---

## 🟣 AI Features

```jsx
// AI Badge
<span className="bg-accent-purple-100 border border-accent-purple-300 text-accent-purple-700 px-3 py-1 rounded-full text-sm font-semibold">
  ✨ AI Powered
</span>

// AI Card Header
<div className="bg-gradient-to-r from-accent-purple-500 to-accent-purple-700 text-white p-4 rounded-t-xl">
  <h3 className="text-xl font-bold">AI Market Analysis</h3>
</div>
```

---

## ✅ Status Badges

```jsx
// Success
<span className="bg-status-success-100 text-status-success-800 px-3 py-1 rounded-full text-sm font-semibold">
  Active
</span>

// Warning
<span className="bg-status-warning-100 text-status-warning-800 px-3 py-1 rounded-full text-sm font-semibold">
  Pending
</span>

// Error
<span className="bg-status-error-100 text-status-error-800 px-3 py-1 rounded-full text-sm font-semibold">
  Failed
</span>

// Info
<span className="bg-status-info-100 text-status-info-800 px-3 py-1 rounded-full text-sm font-semibold">
  Info
</span>
```

---

## 📊 Alert Boxes

```jsx
// Success Alert
<div className="bg-status-success-50 border-l-4 border-status-success-500 p-4 rounded-r">
  <p className="text-status-success-800 font-semibold">✓ Operation successful!</p>
</div>

// Warning Alert
<div className="bg-status-warning-50 border-l-4 border-status-warning-500 p-4 rounded-r">
  <p className="text-status-warning-800 font-semibold">⚠ Please review this item.</p>
</div>

// Error Alert
<div className="bg-status-error-50 border-l-4 border-status-error-500 p-4 rounded-r">
  <p className="text-status-error-800 font-semibold">✕ An error occurred.</p>
</div>

// Info Alert
<div className="bg-status-info-50 border-l-4 border-status-info-500 p-4 rounded-r">
  <p className="text-status-info-800 font-semibold">ℹ New features available.</p>
</div>
```

---

## 📈 Metric Cards

```jsx
// Positive Metric
<div className="bg-growth-emerald-50 border border-growth-emerald-200 p-4 rounded-lg">
  <div className="flex items-center justify-between">
    <span className="text-sm text-growth-emerald-600 font-semibold">Revenue</span>
    <span className="text-growth-emerald-600">↑</span>
  </div>
  <div className="text-3xl font-bold text-growth-emerald-700 mt-2">+24.5%</div>
</div>

// Neutral Metric
<div className="bg-brand-blue-50 border border-brand-blue-200 p-4 rounded-lg">
  <span className="text-sm text-brand-blue-600 font-semibold">Properties</span>
  <div className="text-3xl font-bold text-brand-blue-700 mt-2">184</div>
</div>

// Warning Metric
<div className="bg-status-warning-50 border border-status-warning-200 p-4 rounded-lg">
  <div className="flex items-center justify-between">
    <span className="text-sm text-status-warning-600 font-semibold">Occupancy</span>
    <span className="text-status-warning-600">⚠</span>
  </div>
  <div className="text-3xl font-bold text-status-warning-700 mt-2">78.3%</div>
</div>
```

---

## 📊 Chart Colors

```javascript
// Recharts Line Chart
<LineChart data={data}>
  <Line dataKey="revenue" stroke="#2563EB" strokeWidth={2} /> // Blue
  <Line dataKey="expenses" stroke="#F59E0B" strokeWidth={2} /> // Amber
  <Line dataKey="profit" stroke="#10B981" strokeWidth={2} /> // Green
</LineChart>

// Bar Chart with Status Colors
<BarChart data={data}>
  <Bar dataKey="completed" fill="#10B981" /> // Success
  <Bar dataKey="pending" fill="#F59E0B" /> // Warning
  <Bar dataKey="failed" fill="#EF4444" /> // Error
</BarChart>

// Chart Palette (10 colors)
const chartColors = [
  '#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#06B6D4', '#EC4899', '#F97316', '#6366F1', '#14B8A6'
]
```

---

## 🌙 Dark Mode

```jsx
// Card with Dark Mode
<div className="bg-white dark:bg-dark-bg-secondary border border-neutral-slate-200 dark:border-dark-border-primary rounded-lg p-6">
  <h3 className="text-neutral-slate-900 dark:text-dark-text-primary font-bold">
    Title
  </h3>
  <p className="text-neutral-slate-600 dark:text-dark-text-secondary">
    Description text
  </p>
</div>

// Button with Dark Mode
<button className="bg-brand-blue-500 hover:bg-brand-blue-600 dark:bg-brand-blue-600 dark:hover:bg-brand-blue-700 text-white px-4 py-2 rounded-lg">
  Button
</button>
```

---

## 🎨 Common Combinations

```jsx
// Card Header
<div className="bg-brand-blue-500 text-white p-4 rounded-t-xl">

// Card Body
<div className="bg-neutral-slate-50 dark:bg-dark-bg-secondary p-4">

// Accent Border
<div className="border-l-4 border-brand-teal-500">

// Hover Background
<div className="hover:bg-brand-blue-50 dark:hover:bg-brand-blue-900/20">

// Focus Ring
<input className="focus:ring-2 focus:ring-brand-blue-500">

// Gradient Button
<button className="bg-gradient-to-r from-brand-blue-500 to-brand-teal-500 text-white">
```

---

## 💡 Pro Tips

**Opacity Modifiers:**
```jsx
// 10% opacity
<div className="bg-brand-blue-500/10">

// 50% opacity
<div className="bg-brand-blue-500/50">

// 75% opacity
<div className="bg-brand-blue-500/75">
```

**Hover States:**
```jsx
// Lighter on hover
<div className="bg-brand-blue-500 hover:bg-brand-blue-600">

// Darker on hover
<div className="bg-neutral-slate-100 hover:bg-neutral-slate-200">
```

**Transitions:**
```jsx
// Smooth color transition
<div className="bg-brand-blue-500 hover:bg-brand-blue-600 transition-colors duration-200">
```

---

## 🔍 Finding Colors

**Structure:** `{category}-{color}-{shade}`

```
brand-blue-500      // Primary brand blue
accent-purple-500   // AI feature purple
status-success-500  // Success green
growth-emerald-500  // Growth green
neutral-slate-500   // Neutral gray
```

**Shades Guide:**
- 50-200: Backgrounds, subtle highlights
- 300-400: Borders, dividers
- 500: Primary/default (most saturated)
- 600-700: Hover states
- 800-900: High contrast text

---

**For complete documentation, see:** `COMPREHENSIVE_COLOR_SYSTEM.md`

















