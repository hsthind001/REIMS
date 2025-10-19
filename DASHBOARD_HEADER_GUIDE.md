# 🎨 REIMS Dashboard Header - Complete Guide

**A modern, feature-rich header component with glassmorphism effects and smooth animations**

---

## 📋 Overview

The REIMS Dashboard Header is a premium header component that includes:

✅ **Animated gradient logo** with rotating effect  
✅ **Real-time clock** updating every second  
✅ **System status indicator** with pulse animation  
✅ **User profile dropdown** with settings and logout  
✅ **Command palette search** (Cmd+K / Ctrl+K)  
✅ **Notifications bell** with badge count  
✅ **Glassmorphism effect** with backdrop blur  
✅ **Smooth animations** for all interactions  
✅ **Dark mode support**  
✅ **Fully responsive design**  

---

## 🚀 Quick Start

### Installation

```jsx
import DashboardHeader from '@/components/DashboardHeader'
import { ToastProvider } from '@/components/ui/Toast'

function App() {
  return (
    <ToastProvider>
      <DashboardHeader
        user={{ name: 'John Doe', email: 'john@reims.io' }}
        notifications={[
          {
            id: 1,
            title: 'Document Uploaded',
            message: 'Property_Analysis.pdf processed',
            time: '2 minutes ago',
            read: false
          }
        ]}
        systemStatus="healthy"
        onLogout={() => console.log('Logout')}
      />
    </ToastProvider>
  )
}
```

---

## 📖 Component API

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `user` | `object` | `{ name, email, avatar }` | User information |
| `notifications` | `array` | `[]` | Array of notification objects |
| `systemStatus` | `string` | `'healthy'` | System status: 'healthy', 'warning', 'critical' |
| `onLogout` | `function` | `null` | Logout handler function |
| `className` | `string` | `''` | Additional CSS classes |

### User Object

```typescript
{
  name: string        // User's full name
  email: string       // User's email address
  avatar?: string     // Optional avatar URL
}
```

### Notification Object

```typescript
{
  id: number | string     // Unique identifier
  title: string          // Notification title
  message: string        // Notification message
  time: string           // Time/date string
  read: boolean          // Read status
}
```

### System Status

- `'healthy'` - Green indicator, all systems operational
- `'warning'` - Yellow indicator, some issues detected
- `'critical'` - Red indicator, critical issues

---

## 🎨 Features Breakdown

### 1. Animated Logo

```jsx
// Logo with gradient and rotation animation
<div className="w-12 h-12 bg-gradient-to-br from-brand-blue-500 to-accent-purple-500 rounded-xl">
  <motion.div
    animate={{ rotate: [0, 360] }}
    transition={{ duration: 20, repeat: Infinity }}
  >
    R
  </motion.div>
</div>
```

**Features:**
- Gradient background (blue to purple)
- Continuous 360° rotation
- Pulsing glow effect
- Hover scale animation

### 2. Real-time Clock

```jsx
// Updates every second
const [currentTime, setCurrentTime] = useState(new Date())

useEffect(() => {
  const timer = setInterval(() => {
    setCurrentTime(new Date())
  }, 1000)
  return () => clearInterval(timer)
}, [])
```

**Display Format:**
- Time: `02:34:56 PM` (12-hour with seconds)
- Date: `Mon, Dec 09, 2024`

**Features:**
- Smooth fade animation on update
- Monospace font for consistency
- Hidden on small screens (responsive)

### 3. System Status Indicator

```jsx
// Three status levels with animations
<div className="flex items-center gap-2">
  <StatusIcon className={status.color} />
  {status.pulse && (
    <motion.div
      animate={{ scale: [1, 1.5, 1], opacity: [0.2, 0, 0.2] }}
      transition={{ duration: 2, repeat: Infinity }}
    />
  )}
  <span>{status.label}</span>
</div>
```

**Status Configurations:**

| Status | Color | Icon | Label | Pulse |
|--------|-------|------|-------|-------|
| Healthy | Green | ✓ | All Systems Operational | Yes |
| Warning | Yellow | ⚠ | Some Issues Detected | Yes |
| Critical | Red | ✕ | Critical Issues | Yes |

### 4. Command Palette

**Keyboard Shortcut:** `Cmd+K` (Mac) / `Ctrl+K` (Windows)

```jsx
// Opens search modal
useEffect(() => {
  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      setShowCommandPalette(true)
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [])
```

**Features:**
- Global keyboard shortcut
- Real-time search filtering
- Command categories
- Keyboard shortcuts display
- ESC to close
- Auto-focus on open

### 5. Notifications

```jsx
// Notification badge with count
{unreadNotifications > 0 && (
  <motion.div
    initial={{ scale: 0 }}
    animate={{ scale: 1 }}
    className="badge"
  >
    {unreadNotifications > 9 ? '9+' : unreadNotifications}
  </motion.div>
)}
```

**Features:**
- Badge count (shows 9+ for 10+)
- Unread indicator (blue dot)
- Mark all as read
- Animated entry
- Read/unread visual distinction

### 6. User Profile Dropdown

```jsx
// Gradient profile button
<button className="bg-gradient-to-r from-brand-blue-500 to-accent-purple-500">
  <Avatar />
  <UserInfo />
  <ChevronDown />
</button>
```

**Menu Items:**
- Profile
- Settings
- Activity Log
- Logout (danger style)

---

## 🎭 Glassmorphism Effect

The header uses a modern glassmorphism effect:

```jsx
className={cn(
  'backdrop-blur-xl',                      // Blur effect
  'bg-white/80',                          // Semi-transparent bg
  'dark:bg-dark-bg-primary/80',           // Dark mode
  'border-b border-neutral-slate-200/50', // Subtle border
  'shadow-lg shadow-brand-blue-500/5'     // Colored shadow
)}
```

**Effect Breakdown:**
1. **Backdrop Blur:** `backdrop-blur-xl` creates the frosted glass effect
2. **Transparency:** `bg-white/80` for 80% opacity
3. **Border:** Subtle 50% opacity border
4. **Shadow:** Tinted shadow with brand color

---

## ✨ Animation Details

### Entry Animation

```jsx
<motion.header
  initial={{ y: -100, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
```

**Effect:** Slides down from top with fade-in

### Logo Glow Animation

```jsx
<motion.div
  animate={{
    scale: [1, 1.2, 1],
    opacity: [0.5, 0.8, 0.5]
  }}
  transition={{
    duration: 3,
    repeat: Infinity,
    ease: 'easeInOut'
  }}
/>
```

**Effect:** Pulsing glow with scale and opacity

### Status Pulse

```jsx
<motion.div
  animate={{ 
    scale: [1, 1.5, 1], 
    opacity: [0.2, 0, 0.2] 
  }}
  transition={{ 
    duration: 2, 
    repeat: Infinity 
  }}
/>
```

**Effect:** Expanding ring with fade

### Dropdown Animations

```jsx
initial={{ opacity: 0, y: -10, scale: 0.95 }}
animate={{ opacity: 1, y: 0, scale: 1 }}
exit={{ opacity: 0, y: -10, scale: 0.95 }}
transition={{ duration: 0.15 }}
```

**Effect:** Fade + slide + scale for smooth appearance

### Hover Effects

```jsx
<motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
```

**Effect:** Gentle scale up on hover, press down on tap

---

## 🌓 Dark Mode

The header fully supports dark mode:

```jsx
// Light mode
'bg-white/80 border-neutral-slate-200'

// Dark mode
'dark:bg-dark-bg-primary/80 dark:border-dark-border-primary'
```

**Dark Mode Colors:**
- Background: `dark-bg-primary/80`
- Text: `dark-text-primary`
- Secondary text: `dark-text-secondary`
- Borders: `dark-border-primary`

---

## 📱 Responsive Design

### Breakpoints

| Breakpoint | Changes |
|------------|---------|
| **< 1024px (lg)** | Hide clock |
| **< 1280px (xl)** | Hide user name/email |
| **All sizes** | Maintain core functionality |

### Mobile Optimization

```jsx
// Clock hidden on mobile
<div className="hidden lg:block">
  {/* Clock */}
</div>

// User details hidden on tablet
<div className="hidden xl:block">
  {/* Name and Email */}
</div>
```

---

## 🎯 Usage Examples

### Basic Setup

```jsx
import DashboardHeader from '@/components/DashboardHeader'

function Dashboard() {
  return (
    <div>
      <DashboardHeader
        user={{
          name: 'Jane Smith',
          email: 'jane@reims.io',
          avatar: '/avatars/jane.jpg'
        }}
        systemStatus="healthy"
        onLogout={() => handleLogout()}
      />
      <main>{/* Dashboard content */}</main>
    </div>
  )
}
```

### With Notifications

```jsx
const [notifications, setNotifications] = useState([
  {
    id: 1,
    title: 'New Document',
    message: 'Property analysis completed',
    time: '5 minutes ago',
    read: false
  },
  {
    id: 2,
    title: 'AI Insight',
    message: 'Market trend detected',
    time: '1 hour ago',
    read: false
  }
])

<DashboardHeader
  notifications={notifications}
  // ... other props
/>
```

### Dynamic Status Updates

```jsx
const [systemStatus, setSystemStatus] = useState('healthy')

// Monitor system health
useEffect(() => {
  const checkSystemHealth = async () => {
    const health = await fetchSystemHealth()
    setSystemStatus(health.status)
  }
  
  const interval = setInterval(checkSystemHealth, 30000) // Every 30s
  return () => clearInterval(interval)
}, [])

<DashboardHeader
  systemStatus={systemStatus}
  // ... other props
/>
```

### Custom Logout Handler

```jsx
const handleLogout = async () => {
  try {
    await api.logout()
    toast.success('Logged out successfully')
    navigate('/login')
  } catch (error) {
    toast.error('Logout failed')
  }
}

<DashboardHeader
  onLogout={handleLogout}
  // ... other props
/>
```

---

## 🎨 Customization

### Changing Colors

Modify colors in `tailwind.config.colors.js`:

```javascript
brand: {
  blue: {
    500: '#YOUR_COLOR', // Primary brand color
  }
}
```

### Adjusting Animations

```jsx
// Speed up logo rotation
transition={{ duration: 10 }} // Faster (default: 20)

// Change pulse speed
transition={{ duration: 1 }} // Faster pulse (default: 2)
```

### Custom Logo

```jsx
<div className="w-12 h-12">
  <img src="/logo.svg" alt="Logo" />
</div>
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+K` / `Ctrl+K` | Open command palette |
| `ESC` | Close any open dropdown/modal |

---

## 🧪 Testing

### Test Scenarios

1. **Clock Updates**
   - Verify clock updates every second
   - Check format is correct
   - Confirm smooth animation

2. **Status Changes**
   - Change between healthy/warning/critical
   - Verify color changes
   - Check pulse animation

3. **Notifications**
   - Add notifications
   - Mark as read
   - Clear all

4. **Command Palette**
   - Press Cmd+K / Ctrl+K
   - Type to search
   - Press ESC to close

5. **User Menu**
   - Click profile
   - Test menu items
   - Verify logout

---

## 🚀 Performance

### Optimizations

1. **Debounced Search**
```jsx
const debouncedSearch = debounce(searchQuery, 300)
```

2. **Memoized Components**
```jsx
const MemoizedDropdown = memo(NotificationsDropdown)
```

3. **Efficient Re-renders**
- Only clock updates every second
- Other components update on user interaction

---

## 📚 Complete Example

```jsx
import { useState } from 'react'
import DashboardHeader from '@/components/DashboardHeader'
import { ToastProvider } from '@/components/ui/Toast'

function App() {
  const [systemStatus, setSystemStatus] = useState('healthy')
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'Welcome',
      message: 'Welcome to REIMS Dashboard',
      time: 'Just now',
      read: false
    }
  ])

  const user = {
    name: 'John Doe',
    email: 'john@reims.io',
    avatar: null
  }

  const handleLogout = () => {
    // Logout logic
    console.log('Logging out...')
  }

  return (
    <ToastProvider>
      <DashboardHeader
        user={user}
        notifications={notifications}
        systemStatus={systemStatus}
        onLogout={handleLogout}
      />
      
      <main className="p-6">
        {/* Your dashboard content */}
      </main>
    </ToastProvider>
  )
}

export default App
```

---

## 🎉 Summary

The REIMS Dashboard Header provides:

✅ **Professional Design** - Modern glassmorphism effect  
✅ **Rich Features** - Clock, status, notifications, search  
✅ **Smooth Animations** - Framer Motion powered  
✅ **Keyboard Shortcuts** - Cmd+K command palette  
✅ **Fully Responsive** - Works on all screen sizes  
✅ **Dark Mode Ready** - Complete dark theme support  
✅ **Production Ready** - Optimized and tested  

**Start using the header in your REIMS dashboard today! 🚀**

















