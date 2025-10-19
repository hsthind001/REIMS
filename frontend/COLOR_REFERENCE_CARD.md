# 🎨 REIMS Color Reference Card

Quick reference for using REIMS color palette in Tailwind CSS.

## 🔵 Primary Colors

```jsx
// Brand Blue (#2563EB)
<button className="bg-brand-blue text-white">Button</button>
<div className="text-brand-blue">Text</div>
<div className="border-brand-blue">Border</div>

// Dark Blue (#1E40AF)
<button className="bg-brand-dark-blue text-white">Button</button>
<button className="hover:bg-brand-dark-blue">Hover</button>

// Light Blue (#DBEAFE)
<div className="bg-brand-light-blue">Background</div>
<div className="bg-brand-light-blue/50">Semi-transparent</div>
```

## ✅ Semantic Colors

```jsx
// Success (#10B981)
<span className="text-semantic-success">Success!</span>
<div className="bg-semantic-success text-white">Success</div>
<span className="bg-semantic-success/10 text-semantic-success">Badge</span>

// Warning (#F59E0B)
<span className="text-semantic-warning">Warning!</span>
<div className="bg-semantic-warning text-white">Warning</div>
<span className="bg-semantic-warning/10 text-semantic-warning">Badge</span>

// Critical (#EF4444)
<span className="text-semantic-critical">Error!</span>
<div className="bg-semantic-critical text-white">Delete</div>
<span className="bg-semantic-critical/10 text-semantic-critical">Badge</span>

// Info (#3B82F6)
<span className="text-semantic-info">Info</span>
<div className="bg-semantic-info text-white">Info</div>
<span className="bg-semantic-info/10 text-semantic-info">Badge</span>
```

## ⚪ Neutral Colors

```jsx
// Dark (#0F172A)
<div className="bg-neutral-dark text-white">Dark background</div>
<h1 className="text-neutral-dark">Dark text</h1>

// Light (#F8FAFC)
<div className="bg-neutral-light">Light background</div>
<div className="bg-neutral-light border border-gray-200">Card</div>

// Gray (#64748B)
<p className="text-neutral-gray">Muted text</p>
<div className="border-neutral-gray">Border</div>
```

## 🎭 Combined Examples

### Buttons
```jsx
<button className="bg-brand-blue hover:bg-brand-dark-blue text-white px-4 py-2 rounded-lg">
  Primary
</button>

<button className="bg-semantic-success hover:bg-green-600 text-white px-4 py-2 rounded-lg">
  Success
</button>

<button className="bg-neutral-light hover:bg-gray-100 text-neutral-dark border border-neutral-gray px-4 py-2 rounded-lg">
  Secondary
</button>
```

### Status Badges
```jsx
<span className="bg-semantic-success/10 text-semantic-success px-3 py-1 rounded-full text-sm font-semibold">
  Active
</span>

<span className="bg-semantic-warning/10 text-semantic-warning px-3 py-1 rounded-full text-sm font-semibold">
  Pending
</span>

<span className="bg-semantic-critical/10 text-semantic-critical px-3 py-1 rounded-full text-sm font-semibold">
  Failed
</span>
```

### Cards
```jsx
<div className="bg-neutral-light border border-neutral-gray/20 rounded-lg p-6 hover:shadow-lg transition-shadow">
  <h3 className="text-neutral-dark font-bold text-xl mb-2">Card Title</h3>
  <p className="text-neutral-gray">Card description goes here.</p>
  <button className="mt-4 bg-brand-blue hover:bg-brand-dark-blue text-white px-4 py-2 rounded-lg">
    Action
  </button>
</div>
```

### Alerts
```jsx
// Success Alert
<div className="bg-semantic-success/10 border-l-4 border-semantic-success p-4 rounded">
  <p className="text-semantic-success font-semibold">Success! Your changes have been saved.</p>
</div>

// Warning Alert
<div className="bg-semantic-warning/10 border-l-4 border-semantic-warning p-4 rounded">
  <p className="text-semantic-warning font-semibold">Warning: Please review your input.</p>
</div>

// Error Alert
<div className="bg-semantic-critical/10 border-l-4 border-semantic-critical p-4 rounded">
  <p className="text-semantic-critical font-semibold">Error: Something went wrong.</p>
</div>
```

---

**💡 Tip:** Use `/10` opacity for subtle backgrounds: `bg-brand-blue/10`

















