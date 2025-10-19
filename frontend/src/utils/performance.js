/**
 * Performance Monitoring Utilities
 * Track and optimize application performance
 */

/**
 * Measure component render time
 */
export function measureRender(componentName, callback) {
  const start = performance.now()
  const result = callback()
  const end = performance.now()
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${componentName} rendered in ${(end - start).toFixed(2)}ms`)
  }
  
  return result
}

/**
 * Debounce function for expensive operations
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for scroll/resize handlers
 */
export function throttle(func, limit = 100) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * Image optimization helper
 * Generate srcset for responsive images
 */
export function generateSrcSet(baseUrl, sizes = [320, 640, 1024, 1280]) {
  return sizes.map(size => `${baseUrl}?w=${size} ${size}w`).join(', ')
}

/**
 * Prefetch data for route
 */
export async function prefetchRouteData(queryClient, queryKey, queryFn) {
  await queryClient.prefetchQuery({
    queryKey,
    queryFn,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Bundle size analyzer
 * Log chunk sizes in development
 */
export function logBundleInfo() {
  if (process.env.NODE_ENV === 'development') {
    const modules = Object.keys(window).filter(key => key.startsWith('__webpack'))
    console.log('[Bundle Info]', {
      modules: modules.length,
      timestamp: new Date().toISOString(),
    })
  }
}

/**
 * Web Vitals monitoring
 */
export function reportWebVitals(metric) {
  const { name, value, id } = metric
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Web Vitals] ${name}:`, {
      value: Math.round(value),
      id,
      rating: getRating(name, value),
    })
  }
  
  // Send to analytics in production
  if (process.env.NODE_ENV === 'production') {
    // Send to your analytics service
    // Example: gtag('event', name, { value, metric_id: id })
  }
}

function getRating(metric, value) {
  const thresholds = {
    'FCP': [1800, 3000],
    'LCP': [2500, 4000],
    'FID': [100, 300],
    'CLS': [0.1, 0.25],
    'TTFB': [800, 1800],
  }
  
  const [good, poor] = thresholds[metric] || [0, 0]
  if (value <= good) return 'good'
  if (value <= poor) return 'needs-improvement'
  return 'poor'
}

/**
 * Memoization helper for expensive calculations
 */
export function memoize(fn) {
  const cache = new Map()
  
  return function(...args) {
    const key = JSON.stringify(args)
    
    if (cache.has(key)) {
      return cache.get(key)
    }
    
    const result = fn.apply(this, args)
    cache.set(key, result)
    
    // Limit cache size
    if (cache.size > 100) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }
    
    return result
  }
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Optimize animation performance
 */
export function getOptimizedAnimation(baseAnimation) {
  if (prefersReducedMotion()) {
    return { duration: 0 }
  }
  return baseAnimation
}

















